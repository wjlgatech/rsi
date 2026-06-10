#!/usr/bin/env python3
"""awesome_kg.py — compile an awesome-list README into a living knowledge graph.

Zero external deps (stdlib only). The parse is DETERMINISTIC — no LLM call is needed
to build the graph, so it costs zero tokens and runs identically in CI. An optional
`nim-enrich` pass proposes cross-paper lineage edges via NVIDIA's free NIM API.

What it understands (the de-facto awesome-list grammar):
  • GFM tables under ##/###/#### headings — the header row names the columns
    (Paper/Repo/Person/Lab/Benchmark/Title → node type; Authors/Speaker(s),
    Venue/Event, Year, Citations, Stars, Code/Link(s), Description/Focus → fields)
  • bold **Name** spans inside author/speaker cells → person mentions, resolved
    against the people tables by surname + first initial ("S. Hu" ≈ "Shengran Hu")
  • [text](url) markdown links anywhere in a cell
  • section headings → category nodes; every table row is part_of its category

Emitted edges: authored_by · has_code · given_by · member_of · part_of · builds_on
(builds_on comes only from an --enrich overlay or the nim-enrich pass — never guessed).

Usage:
  awesome_kg.py build README.md [--out graph.json] [--html graph.html]
                                [--enrich overlay.json] [--title "T"]
  awesome_kg.py nim-enrich graph.json [--model z-ai/glm-5.1]   # needs NVIDIA_API_KEY
  awesome_kg.py schema                                          # print graph JSON shape
"""

from __future__ import annotations

import json
import math
import os
import re
import sys
import urllib.request

# ── column → role mapping (header keywords, lowercased) ─────────────────────────
_NAME_TYPES = {
    "paper": "paper",
    "repo": "repo",
    "tool": "repo",
    "benchmark": "benchmark",
    "person": "person",
    "lab": "lab",
    "title": "talk",  # Title+Speaker tables are talk tables; Title alone → item
}
_ROLES = {
    "authors": "authors",
    "author": "authors",
    "speaker": "authors",
    "speakers": "authors",
    "speaker(s)": "authors",
    "venue": "venue",
    "event": "venue",
    "year": "year",
    "citations": "citations",
    "stars": "stars",
    "code": "code",
    "link": "code",
    "links": "links",
    "description": "summary",
    "focus": "summary",
    "research focus": "summary",
    "task": "summary",
    "previous roles": "roles",
    "role": "roles",
    "status": "status",
    "key papers": "papers",
}

_LINK = re.compile(r"\[([^\]]*)\]\(([^)\s]+)\)")
_BOLD = re.compile(r"\*\*([^*]+)\*\*")
_NUM = re.compile(r"[\d,]+")


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60]


def _plain(cell: str) -> str:
    """Cell → display text: unlink, unbold, drop emoji-ish leading symbols."""
    t = _LINK.sub(r"\1", cell)
    t = t.replace("**", "").replace("*", "")
    return re.sub(r"\s+", " ", t).strip(" —–-")


def _num(cell: str) -> int:
    m = _NUM.search(cell.replace("~", "").replace("+", ""))
    if not m:
        return 0
    try:
        v = int(m.group().replace(",", ""))
    except ValueError:
        return 0
    if "k" in cell.lower().split(m.group())[-1][:2]:
        v *= 1000
    return v


def _gh_slug(url: str) -> str:
    m = re.search(r"github\.com/([\w.-]+/[\w.-]+)", url)
    return m.group(1).lower().rstrip("/").removesuffix(".git") if m else ""


_GENERIC_ORG = {"research", "university", "institute", "group", "lab", "labs", "team", "the", "nlp", "llm"}


def _org_tokens(lab_name: str) -> list[str]:
    """Distinctive tokens of an org name: acronyms (UCL, UBC, KAUST) or long words
    (DeepMind, Sakana, Recursive). The pre-parenthesis part only."""
    base = lab_name.split("(")[0]
    out = []
    for w in re.findall(r"[A-Za-zÀ-ÿ-]+", base):
        if w.lower() in _GENERIC_ORG:
            continue
        if (w.isupper() and len(w) >= 3) or len(w) >= 6:
            out.append(w.lower())
    return out


def _org_in(tokens: list[str], text: str) -> bool:
    return any(re.search(rf"\b{re.escape(t)}\b", text) for t in tokens)


# ── markdown walk: headings + tables ─────────────────────────────────────────────
def _tables(md: str):
    """Yield (heading_stack, header_cells, rows) for every GFM table."""
    heads: dict[int, str] = {}
    lines = md.splitlines()
    i = 0
    while i < len(lines):
        ln = lines[i]
        hm = re.match(r"^(#{2,4})\s+(.*)", ln)
        if hm:
            lvl = len(hm.group(1))
            heads[lvl] = re.sub(r"[#️⃣🏛️📄🧬🔬🤖🧠🌐✏️📊🗺️🛠️👥🎯🎙️📈📅🏆🤝📜⭐🔥🆕💻▶️📖]", "", hm.group(2)).strip()
            for deeper in list(heads):
                if deeper > lvl:
                    del heads[deeper]
        if ln.lstrip().startswith("|") and i + 1 < len(lines) and re.match(
            r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]
        ):
            header = [c.strip() for c in ln.strip().strip("|").split("|")]
            rows = []
            j = i + 2
            while j < len(lines) and lines[j].lstrip().startswith("|"):
                rows.append([c.strip() for c in lines[j].strip().strip("|").split("|")])
                j += 1
            stack = [heads[k] for k in sorted(heads)]
            yield stack, header, rows
            i = j
            continue
        i += 1


def _col_roles(header: list[str]) -> tuple[int, str, dict[int, str]]:
    """→ (name_col, node_type, {col: role})."""
    roles: dict[int, str] = {}
    name_col, ntype = 0, "item"
    for c, h in enumerate(header):
        hl = _plain(h).lower()
        if c == 0 or ntype == "item":
            for key, t in _NAME_TYPES.items():
                if key in hl:
                    name_col, ntype = c, t
                    break
        for key, role in _ROLES.items():
            if hl == key or hl.startswith(key):
                roles[c] = role
                break
    # Title+Speaker(s) means talk; bare Title table stays generic.
    if ntype == "talk" and "authors" not in roles.values():
        ntype = "item"
    return name_col, ntype, roles


# ── person resolution ("S. Hu" / "Clune" → "Shengran Hu" / "Jeff Clune") ────────
class _People:
    def __init__(self):
        self.by_id: dict[str, dict] = {}

    @staticmethod
    def _key(name: str) -> tuple[str, str]:
        name = re.sub(r"\([^)]*\)", " ", name)  # "Jeff Clune (Recursive)" → "Jeff Clune"
        parts = [p for p in re.sub(r"[.*†]", " ", name).split() if p]
        if not parts:
            return "", ""
        return parts[-1].lower(), parts[0][0].lower() if len(parts) > 1 else ""

    def add(self, name: str, node: dict):
        self.by_id[node["id"]] = node
        node["_key"] = self._key(name)

    def resolve(self, mention: str) -> dict | None:
        m = re.sub(r"\([^)]*\)|[*†]", " ", mention).strip().lower()
        for n in self.by_id.values():  # exact full name beats the surname heuristic
            if n["name"].lower() == m:
                return n
        sur, ini = self._key(mention)
        if not sur:
            return None
        hits = [n for n in self.by_id.values() if n["_key"][0] == sur]
        if len(hits) > 1 and ini:
            hits = [n for n in hits if n["_key"][1] == ini or not n["_key"][1]]
        return hits[0] if len(hits) == 1 else None


# ── build ────────────────────────────────────────────────────────────────────────
def build(md: str, title: str, enrich: dict | None) -> dict:
    nodes: dict[str, dict] = {}
    edges: list[dict] = []
    people = _People()
    seen_edges: set[tuple] = set()

    def put(ntype: str, name: str, **fields) -> dict:
        nid = f"{ntype}:{_slug(name)}"
        n = nodes.get(nid)
        if not n:
            n = {"id": nid, "type": ntype, "name": name, "links": []}
            nodes[nid] = n
        for k, v in fields.items():
            if v and not n.get(k):
                n[k] = v
            elif k == "links" and v:
                n["links"] = list(dict.fromkeys(n["links"] + v))
        return n

    def link(src: str, dst: str, etype: str):
        if src != dst and (src, dst, etype) not in seen_edges:
            seen_edges.add((src, dst, etype))
            edges.append({"src": src, "dst": dst, "type": etype})

    parsed = list(_tables(md))

    # Pass 1 — people & lab tables first, so author mentions can resolve.
    for stack, header, rows in parsed:
        name_col, ntype, roles = _col_roles(header)
        if ntype not in ("person", "lab"):
            continue
        for row in rows:
            if name_col >= len(row):
                continue
            name = _plain(row[name_col])
            if not name:
                continue
            urls = [u for _, u in _LINK.findall(" ".join(row))]
            summary = next(
                (_plain(row[c]) for c, r in roles.items() if r == "summary" and c < len(row)), ""
            )
            n = put(ntype, name, summary=summary, links=urls, category=stack[-1] if stack else "")
            if ntype == "person":
                people.add(name, n)

    # Pass 2 — everything else + edges.
    for stack, header, rows in parsed:
        name_col, ntype, roles = _col_roles(header)
        category = stack[-1] if stack else "misc"
        cat_node = put("category", category)
        for row in rows:
            if name_col >= len(row):
                continue
            raw_name = row[name_col]
            name = _plain(raw_name)
            if not name:
                continue
            urls = [u for _, u in _LINK.findall(raw_name)]
            fields: dict = {"links": urls, "category": category}
            authors_cell = ""
            for c, role in roles.items():
                if c >= len(row):
                    continue
                cell = row[c]
                if role == "authors":
                    authors_cell = cell
                    fields["authors"] = _plain(cell)
                elif role in ("venue", "summary", "status", "roles"):
                    fields[role if role != "roles" else "summary"] = _plain(cell)
                elif role == "year":
                    fields["year"] = _plain(cell)
                elif role == "citations":
                    fields["citations"] = _num(cell)
                elif role == "stars":
                    fields["stars"] = _num(cell)
                elif role in ("code", "links"):
                    fields["links"] = fields["links"] + [u for _, u in _LINK.findall(cell)]

            if ntype in ("person", "lab"):  # already built in pass 1; just re-anchor category
                n = put(ntype, name)
            else:
                n = put(ntype, name, **fields)
            link(n["id"], cat_node["id"], "part_of")

            # authored_by / given_by: bold mentions PLUS comma-split plain chunks —
            # speaker cells bold the lab ("Jeff Clune (**Recursive**)"), so bold alone
            # misses the person. Resolution against the people registry filters noise:
            # ambiguous surnames and non-person chunks resolve to nothing.
            mentions = _BOLD.findall(authors_cell) + [
                p for p in re.split(r"[,&]| and ", _plain(authors_cell)) if p.strip()
            ][:8]
            for m in mentions:
                p = people.resolve(m.strip())
                if p:
                    link(n["id"], p["id"], "given_by" if ntype == "talk" else "authored_by")

            # member_of: a lab's distinctive name in the person's row (URLs stripped so
            # scholar.google.com can't match "Google …") or in the table's own heading
            # (a "Recursive Lab — Co-Founders" section affiliates every row).
            if ntype == "person":
                rowtext = _plain(" ".join(row)).lower()
                headtext = " ".join(stack).lower()
                for lid, ln_ in list(nodes.items()):
                    if ln_["type"] != "lab":
                        continue
                    toks = _org_tokens(ln_["name"])
                    if toks and (_org_in(toks, rowtext) or _org_in(toks, headtext)):
                        link(n["id"], lid, "member_of")

    # has_code: paper code links ↔ repo nodes, by github slug
    repo_by_slug = {
        _gh_slug(u): n for n in nodes.values() if n["type"] == "repo" for u in n["links"]
    }
    repo_by_slug.pop("", None)
    for n in list(nodes.values()):
        if n["type"] != "paper":
            continue
        for u in n["links"]:
            r = repo_by_slug.get(_gh_slug(u))
            if r:
                link(n["id"], r["id"], "has_code")

    # confidence: deterministic, from public engagement signals
    for n in nodes.values():
        if n.get("citations"):
            n["confidence"] = round(min(1.0, 0.5 + 0.5 * math.log1p(n["citations"]) / math.log1p(3000)), 2)
        elif n.get("stars"):
            n["confidence"] = round(min(1.0, 0.5 + 0.5 * math.log1p(n["stars"]) / math.log1p(50000)), 2)
        else:
            n["confidence"] = 0.6
        n.pop("_key", None)

    g = {"kind": "awesome", "subject": title, "nodes": list(nodes.values()), "edges": edges}
    if enrich:
        merge(g, enrich)
    g["stats"] = _stats(g)
    return g


def merge(g: dict, overlay: dict) -> None:
    """Merge an overlay {nodes:[],edges:[]} — hand-written or nim-enriched lineage."""
    ids = {n["id"] for n in g["nodes"]}
    for n in overlay.get("nodes", []):
        if n["id"] not in ids:
            n.setdefault("confidence", 0.6)
            n.setdefault("links", [])
            g["nodes"].append(n)
            ids.add(n["id"])
    have = {(e["src"], e["dst"], e["type"]) for e in g["edges"]}
    for e in overlay.get("edges", []):
        if e["src"] in ids and e["dst"] in ids and (e["src"], e["dst"], e["type"]) not in have:
            g["edges"].append(e)
            have.add((e["src"], e["dst"], e["type"]))


def _stats(g: dict) -> dict:
    def count(items, k):
        out: dict[str, int] = {}
        for it in items:
            out[it.get(k, "?")] = out.get(it.get(k, "?"), 0) + 1
        return out

    return {
        "nodes": len(g["nodes"]),
        "edges": len(g["edges"]),
        "node_types": count(g["nodes"], "type"),
        "edge_types": count(g["edges"], "type"),
    }


# ── optional NIM lineage enrichment (free NVIDIA API — zero Claude tokens) ──────
def nim_enrich(graph_path: str, model: str) -> None:
    key = os.environ.get("NVIDIA_API_KEY", "")
    if not key:
        sys.exit("nim-enrich needs NVIDIA_API_KEY (free key: build.nvidia.com/models)")
    g = json.load(open(graph_path))
    papers = [n for n in g["nodes"] if n["type"] == "paper"]
    listing = "\n".join(f'- {n["id"]}: {n["name"]} ({n.get("year", "?")})' for n in papers)
    prompt = (
        "These are papers from one research field. Output ONLY a JSON array of "
        '{"src": "<id>", "dst": "<id>", "type": "builds_on"} edges where the src paper '
        "clearly builds on the dst paper (same lineage, cited foundation, or direct "
        "successor). Be conservative — only well-known lineages.\n" + listing
    )
    body = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "max_tokens": 4096,
    }
    req = urllib.request.Request(
        "https://integrate.api.nvidia.com/v1/chat/completions",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
    )
    with urllib.request.urlopen(req, timeout=300) as r:
        text = json.loads(r.read())["choices"][0]["message"]["content"]
    m = re.search(r"\[.*\]", text, re.S)
    if not m:
        sys.exit(f"NIM returned no JSON array: {text[:300]}")
    overlay = {"edges": json.loads(m.group())}
    merge(g, overlay)
    g["stats"] = _stats(g)
    json.dump(g, open(graph_path, "w"), indent=1, ensure_ascii=False)
    print(f"merged {len(overlay['edges'])} lineage edges → {graph_path}")


# ── self-contained interactive HTML (canvas force layout, no external scripts) ──
_COLORS = {
    "paper": "#6ab0f3",
    "repo": "#7bd88f",
    "person": "#e8a2c8",
    "lab": "#f3d06a",
    "talk": "#c79bf2",
    "benchmark": "#f0926a",
    "category": "#5a5a66",
    "concept": "#9adbe8",
    "item": "#9aa4b2",
}


def render_html(g: dict) -> str:
    payload = json.dumps(
        {
            "subject": g["subject"],
            "stats": g["stats"],
            "nodes": [
                {k: n.get(k) for k in ("id", "type", "name", "summary", "authors", "venue",
                                        "year", "citations", "stars", "links", "confidence",
                                        "category") if n.get(k) is not None}
                for n in g["nodes"]
            ],
            "edges": g["edges"],
            "colors": _COLORS,
        },
        ensure_ascii=False,
    ).replace("</", "<\\/")
    return (
        _HTML_TEMPLATE.replace("__TITLE__", g["subject"] or "knowledge graph")
        .replace("__DATA__", payload)
    )


_HTML_TEMPLATE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__ — living knowledge graph</title>
<style>
:root{color-scheme:dark}
*{box-sizing:border-box;margin:0}
body{background:#0b0c10;color:#e6e6ea;font:14px/1.45 -apple-system,Inter,system-ui;overflow:hidden}
#c{position:fixed;inset:0;cursor:grab}
#hud{position:fixed;top:0;left:0;right:0;display:flex;gap:10px;align-items:center;
  padding:10px 14px;pointer-events:none;background:linear-gradient(#0b0c10ee,#0b0c1000)}
#hud>*{pointer-events:auto}
#hud h1{font-size:15px;font-weight:600;white-space:nowrap}
#hud .meta{color:#8b8b96;font-size:12px;white-space:nowrap}
#q{background:#16171d;border:1px solid #2a2b33;border-radius:8px;color:#e6e6ea;
  padding:6px 10px;width:220px;outline:none}
#legend{position:fixed;bottom:12px;left:14px;display:flex;flex-wrap:wrap;gap:6px}
#legend button{background:#16171d;border:1px solid #2a2b33;border-radius:99px;color:#cfcfd6;
  padding:3px 10px;font-size:12px;cursor:pointer;display:flex;gap:6px;align-items:center}
#legend button.off{opacity:.35}
#legend i{width:9px;height:9px;border-radius:99px;display:inline-block}
#panel{position:fixed;top:54px;right:12px;width:330px;max-height:calc(100vh - 80px);
  overflow:auto;background:#13141af2;border:1px solid #2a2b33;border-radius:12px;
  padding:14px;display:none}
#panel h2{font-size:15px;margin-bottom:2px}
#panel .ty{font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:#8b8b96}
#panel .sec{margin-top:10px;font-size:13px;color:#c9c9d2}
#panel a{color:#7ab8ff;text-decoration:none;word-break:break-all}
#panel .edge{padding:3px 0;border-top:1px solid #22232b;font-size:12.5px;cursor:pointer}
#panel .edge i{color:#8b8b96;font-style:normal}
#panel .x{float:right;cursor:pointer;color:#8b8b96}
@media(max-width:640px){#panel{left:12px;width:auto}#q{width:130px}}
</style></head><body>
<canvas id="c"></canvas>
<div id="hud"><h1>__TITLE__</h1><span class="meta" id="meta"></span>
<input id="q" placeholder="search nodes…" autocomplete="off"></div>
<div id="legend"></div>
<div id="panel"></div>
<script>
const G=__DATA__;
const W=()=>innerWidth,H=()=>innerHeight,cv=document.getElementById('c'),cx=cv.getContext('2d');
const DPR=devicePixelRatio||1;
function resize(){cv.width=W()*DPR;cv.height=H()*DPR;cv.style.width=W()+'px';cv.style.height=H()+'px'}
resize();addEventListener('resize',resize);
document.getElementById('meta').textContent=G.stats.nodes+' nodes · '+G.stats.edges+' edges';
const deg={};G.edges.forEach(e=>{deg[e.src]=(deg[e.src]||0)+1;deg[e.dst]=(deg[e.dst]||0)+1});
const N=G.nodes.map((n,i)=>({...n,
  x:W()/2+Math.cos(i*2.399)*Math.sqrt(i)*22, y:H()/2+Math.sin(i*2.399)*Math.sqrt(i)*22,
  vx:0,vy:0, r:5+Math.min(11,Math.sqrt(deg[n.id]||1)*2.2)}));
const byId={};N.forEach(n=>byId[n.id]=n);
const E=G.edges.filter(e=>byId[e.src]&&byId[e.dst]);
const types=[...new Set(N.map(n=>n.type))], on=new Set(types);
let sel=null,hover=null,q='';
const vis=n=>on.has(n.type)&&(!q||(n.name+' '+(n.summary||'')+' '+(n.authors||'')).toLowerCase().includes(q));
// legend
const lg=document.getElementById('legend');
types.forEach(t=>{const b=document.createElement('button');
  b.innerHTML='<i style="background:'+(G.colors[t]||'#999')+'"></i>'+t+' <span style="color:#777">'+(G.stats.node_types[t]||'')+'</span>';
  b.onclick=()=>{on.has(t)?on.delete(t):on.add(t);b.classList.toggle('off');kick()};lg.appendChild(b)});
document.getElementById('q').addEventListener('input',e=>{q=e.target.value.toLowerCase().trim();kick()});
// physics
let alpha=1;const kick=()=>alpha=Math.max(alpha,.5);
function step(){
  const vn=N.filter(vis);if(alpha<.005)return;
  // grid-bucketed repulsion (O(n·k))
  const cell=120,grid=new Map();
  vn.forEach(n=>{const k=(n.x/cell|0)+':'+(n.y/cell|0);(grid.get(k)||grid.set(k,[]).get(k)).push(n)});
  vn.forEach(n=>{
    for(let gx=-1;gx<2;gx++)for(let gy=-1;gy<2;gy++){
      const b=grid.get(((n.x/cell|0)+gx)+':'+((n.y/cell|0)+gy));if(!b)continue;
      for(const m of b){if(m===n)continue;
        let dx=n.x-m.x,dy=n.y-m.y,d2=dx*dx+dy*dy||1;if(d2>cell*cell*4)continue;
        const f=1400/d2;n.vx+=dx*f*alpha;n.vy+=dy*f*alpha}}
    n.vx+=(W()/2-n.x)*.0012*alpha;n.vy+=(H()/2-n.y)*.0012*alpha});
  E.forEach(e=>{const a=byId[e.src],b=byId[e.dst];if(!vis(a)||!vis(b))return;
    const dx=b.x-a.x,dy=b.y-a.y,d=Math.sqrt(dx*dx+dy*dy)||1,f=(d-90)/d*.012*alpha;
    a.vx+=dx*f;a.vy+=dy*f;b.vx-=dx*f;b.vy-=dy*f});
  vn.forEach(n=>{if(n===dragN)return;n.x+=n.vx*=.85;n.y+=n.vy*=.85});
  alpha*=.985}
// view transform
let tx=0,ty=0,scale=1;
function draw(){
  cx.setTransform(DPR,0,0,DPR,0,0);cx.clearRect(0,0,W(),H());
  cx.translate(tx,ty);cx.scale(scale,scale);
  const nbr=sel?new Set(E.flatMap(e=>e.src===sel.id?[e.dst]:e.dst===sel.id?[e.src]:[])):null;
  E.forEach(e=>{const a=byId[e.src],b=byId[e.dst];if(!vis(a)||!vis(b))return;
    const hot=sel&&(e.src===sel.id||e.dst===sel.id);
    cx.strokeStyle=hot?'#9ab8ffcc':'#2c2d36';cx.lineWidth=hot?1.4:.7;
    cx.beginPath();cx.moveTo(a.x,a.y);cx.lineTo(b.x,b.y);cx.stroke()});
  N.forEach(n=>{if(!vis(n))return;
    const dim=sel&&n!==sel&&!(nbr&&nbr.has(n.id));
    cx.globalAlpha=dim?.25:1;
    cx.fillStyle=G.colors[n.type]||'#999';
    cx.beginPath();cx.arc(n.x,n.y,n.r,0,7);cx.fill();
    if(n===sel||n===hover){cx.strokeStyle='#fff';cx.lineWidth=1.5;cx.stroke()}
    if(scale>.55&&(n.r>8||n===sel||n===hover||!dim&&scale>1.1)){
      cx.fillStyle=dim?'#777':'#e6e6ea';cx.font='11px -apple-system,Inter,system-ui';
      cx.fillText(n.name.slice(0,34),n.x+n.r+4,n.y+4)}
    cx.globalAlpha=1});
  step();requestAnimationFrame(draw)}
requestAnimationFrame(draw);
// interaction
const pt=ev=>({x:(ev.clientX-tx)/scale,y:(ev.clientY-ty)/scale});
const hit=ev=>{const p=pt(ev);let best=null,bd=1e9;
  N.forEach(n=>{if(!vis(n))return;const d=(n.x-p.x)**2+(n.y-p.y)**2;
    if(d<Math.max(144,n.r*n.r*2.6)&&d<bd){bd=d;best=n}});return best};
let dragN=null,panning=false,px=0,py=0;
cv.addEventListener('pointerdown',ev=>{dragN=hit(ev);
  if(!dragN){panning=true;px=ev.clientX;py=ev.clientY;cv.style.cursor='grabbing'}});
addEventListener('pointermove',ev=>{
  if(dragN){const p=pt(ev);dragN.x=p.x;dragN.y=p.y;kick()}
  else if(panning){tx+=ev.clientX-px;ty+=ev.clientY-py;px=ev.clientX;py=ev.clientY}
  else hover=hit(ev)});
addEventListener('pointerup',ev=>{
  if(dragN&&!ev.movementX&&!ev.movementY||dragN&&hit(ev)===dragN)select(dragN);
  else if(panning&&Math.abs(ev.clientX-px)<3)select(hit(ev));
  dragN=null;panning=false;cv.style.cursor='grab'});
cv.addEventListener('wheel',ev=>{ev.preventDefault();
  const s=Math.exp(-ev.deltaY*.0012),ns=Math.min(4,Math.max(.2,scale*s));
  tx=ev.clientX-(ev.clientX-tx)*ns/scale;ty=ev.clientY-(ev.clientY-ty)*ns/scale;scale=ns},{passive:false});
// detail panel
const panel=document.getElementById('panel');
function select(n){sel=n;if(!n){panel.style.display='none';return}
  const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  let h='<span class="x" onclick="select(null)">✕</span><h2>'+esc(n.name)+'</h2>'
    +'<div class="ty">'+n.type+(n.category?' · '+esc(n.category):'')+'</div>';
  if(n.summary)h+='<div class="sec">'+esc(n.summary)+'</div>';
  if(n.authors)h+='<div class="sec"><b>authors</b> '+esc(n.authors)+'</div>';
  const facts=[n.venue,n.year,n.citations&&('~'+n.citations+' citations'),n.stars&&('~'+n.stars+'★'),
    n.confidence&&('confidence '+n.confidence)].filter(Boolean).join(' · ');
  if(facts)h+='<div class="sec">'+esc(facts)+'</div>';
  (n.links||[]).slice(0,6).forEach(u=>h+='<div class="sec"><a target="_blank" href="'+esc(u)+'">'+esc(u.replace(/^https?:\/\//,''))+'</a></div>');
  const rel=E.filter(e=>e.src===n.id||e.dst===n.id);
  if(rel.length){h+='<div class="sec"><b>'+rel.length+' connections</b></div>';
    rel.slice(0,40).forEach(e=>{const other=e.src===n.id?byId[e.dst]:byId[e.src];
      h+='<div class="edge" data-id="'+esc(other.id)+'">'+(e.src===n.id?'<i>'+e.type+' →</i> ':'<i>← '+e.type+'</i> ')+esc(other.name)+'</div>'})}
  panel.innerHTML=h;panel.style.display='block';
  panel.querySelectorAll('.edge').forEach(el=>el.onclick=()=>{const m=byId[el.dataset.id];if(m)select(m)});
  kick()}
window.select=select;
</script></body></html>
"""


# ── CLI ──────────────────────────────────────────────────────────────────────────
def main() -> None:
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help", "help"):
        print(__doc__)
        return
    cmd, rest = args[0], args[1:]

    if cmd == "schema":
        print(json.dumps({
            "kind": "awesome", "subject": "<title>",
            "nodes": [{"id": "paper:slug", "type": "paper|repo|person|lab|talk|benchmark|category|item",
                       "name": "", "summary": "", "links": [], "year": "", "citations": 0,
                       "stars": 0, "confidence": 0.0}],
            "edges": [{"src": "", "dst": "",
                       "type": "authored_by|has_code|given_by|member_of|part_of|builds_on"}],
        }, indent=2))
        return

    if cmd == "nim-enrich":
        model = "z-ai/glm-5.1"
        if "--model" in rest:
            model = rest[rest.index("--model") + 1]
        nim_enrich(rest[0], model)
        return

    if cmd != "build":
        sys.exit(f"unknown command: {cmd}\n{__doc__}")

    src, out, html_out, enrich_path, title = "", "graph.json", "", "", ""
    it = iter(rest)
    for a in it:
        if a == "--out":
            out = next(it, out)
        elif a == "--html":
            html_out = next(it, "")
        elif a == "--enrich":
            enrich_path = next(it, "")
        elif a == "--title":
            title = next(it, "")
        else:
            src = a
    if not src:
        sys.exit("usage: awesome_kg.py build README.md [--out g.json] [--html g.html] "
                 "[--enrich overlay.json] [--title T]")

    md = open(src, encoding="utf-8", errors="ignore").read()
    title = title or (re.search(r"^#\s+(.+)$", md, re.M).group(1).strip() if re.search(r"^#\s+(.+)$", md, re.M) else os.path.basename(src))
    title = re.sub(r"[#*`]|:[a-z_]+:|[\U0001F000-\U0001FAFF☀-➿]", "", title).strip()
    enrich = json.load(open(enrich_path)) if enrich_path else None
    g = build(md, title, enrich)
    json.dump(g, open(out, "w"), indent=1, ensure_ascii=False)
    print(f"graph: {out} — {g['stats']['nodes']} nodes, {g['stats']['edges']} edges")
    print(f"  node types: {g['stats']['node_types']}")
    print(f"  edge types: {g['stats']['edge_types']}")
    if html_out:
        open(html_out, "w").write(render_html(g))
        print(f"view:  {html_out} (self-contained — works from file:// and GitHub Pages)")


if __name__ == "__main__":
    main()
