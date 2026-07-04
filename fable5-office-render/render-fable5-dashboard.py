#!/usr/bin/env python3
"""render-fable5-dashboard.py — PIXELS-FIRST renderer.

The FRONT-END dashboard is a STATIC RENDER of the BACKEND HBI. This tool reads the
office backend (`*.hbp` manifests + `*.hbi` cube streams, json=0) and emits
`fable5-dashboard.html`. Hand-editing the HTML is banned — change the backend HBP,
re-run this, and the pixels follow. E=0: pure file I/O, no network, no spawn.
"""
import os, glob, html, hashlib, re

OFF = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(OFF, "fable5-dashboard.html")

def parse_row(row):
    parts = row.rstrip("\n").split("|")
    tag = parts[0]
    fields = []
    for p in parts[1:]:
        if "=" in p:
            k, v = p.split("=", 1); fields.append((k, v))
        elif p:
            fields.append((p, None))
    return tag, fields

def fields_dict(fields):
    return {k: v for k, v in fields if v is not None}

# ---- read all backend HBP manifests + HBI cube streams ----
hbp_docs = {}   # name -> [rows]
hbi_docs = {}   # name -> [rows]
for fp in sorted(glob.glob(os.path.join(OFF, "*.hbp"))):
    name = os.path.basename(fp)
    hbp_docs[name] = [l for l in open(fp, encoding="utf-8", errors="replace").read().splitlines() if l.strip()]
for fp in sorted(glob.glob(os.path.join(OFF, "*.hbi"))):
    name = os.path.basename(fp)
    hbi_docs[name] = [l for l in open(fp, encoding="utf-8", errors="replace").read().splitlines() if l.strip()]

# ---- seat header from OFFICE.hbp ----
seat = {"seat": "ACER-CLAUDE-FABLE5", "pid": "8467a937cba309f7", "glyph": "BH1024:SEAT-FABLE5",
        "hilbert": "1720", "sector": "SEC-FABLE5-1720", "owner": "OP-JESSE"}
for row in hbp_docs.get("OFFICE.hbp", []):
    tag, fields = parse_row(row)
    if tag == "OFFICEHDR":
        seat.update(fields_dict(fields))

# ---- gather PIECE rows (the MEASURED work-cranks) across every manifest ----
pieces = []
for name, rows in hbp_docs.items():
    for row in rows:
        tag, fields = parse_row(row)
        if tag == "PIECE":
            d = fields_dict(fields); d["_doc"] = name; pieces.append(d)

# ---- gather EMIT cubes across every hbi (self-prism + dbbh cubes) ----
families = {}  # family -> [(name, pid)]
for name, rows in hbi_docs.items():
    for row in rows:
        tag, fields = parse_row(row)
        if tag == "EMIT":
            d = fields_dict(fields)
            fam = d.get("family", "CUBE")
            families.setdefault(fam, []).append((d.get("name", "?"), d.get("pid", "")))

# ---- bigpickle-rebuild map (the permanent reminder -> newer systems) ----
bpmap = {"spine": [], "ramp": None, "pipeline": None, "newer": None, "permanent": None}
for row in hbp_docs.get("FABLE5-BIGPICKLE-MAP-2026-07-04.hbp", []):
    tag, fields = parse_row(row); d = fields_dict(fields)
    if tag == "SPINE": bpmap["spine"].append(d)
    elif tag == "RAMP": bpmap["ramp"] = d
    elif tag == "PIPELINE": bpmap["pipeline"] = d
    elif tag == "NEWERSYSTEM": bpmap["newer"] = d
    elif tag == "PERMANENT": bpmap["permanent"] = d

# ---- CSS: reuse the existing dashboard's <style> so the look is preserved ----
css = ""
if os.path.exists(OUT):
    m = re.search(r"<style>(.*?)</style>", open(OUT, encoding="utf-8", errors="replace").read(), re.S)
    if m:
        css = m.group(1)
if not css:
    css = (":root{--bg:#06080e;--pnl:#0b1120;--pnl2:#0d1526;--ln:#182238;--ln2:#24324e;--tx:#c7d3ec;"
           "--dim:#5d6c8a;--dim2:#3d4a66;--cy:#43e8d8;--up:#5ce0a0;--down:#ff6b6b;--warn:#ffb454;--vi:#a78bfa}"
           "*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--tx);"
           "font:12.5px/1.5 ui-monospace,Menlo,Consolas,monospace}.wrap{max-width:1200px;margin:0 auto;padding:24px 20px 40px}"
           ".sect{margin:22px 0 9px;color:var(--dim);font-size:10.5px;text-transform:uppercase;letter-spacing:2px}"
           ".cranks{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:10px}"
           ".crank{background:var(--pnl);border:1px solid var(--ln);border-left:3px solid var(--dim2);border-radius:8px;padding:11px 13px}"
           ".crank.good{border-left-color:var(--up)}.ct{color:var(--dim);font-size:10.5px;text-transform:uppercase;letter-spacing:1px}"
           ".cv{font-size:15px;margin:3px 0 5px;color:var(--tx);font-weight:600}.crank.good .cv{color:var(--up)}"
           ".cn{color:var(--dim);font-size:10.5px;line-height:1.45}"
           ".cubefam{margin-bottom:12px}.cubefam h4{margin:0 0 6px;font-size:11px}.cubes{display:grid;"
           "grid-template-columns:repeat(auto-fill,minmax(112px,1fr));gap:6px}.cube{background:var(--pnl2);"
           "border:1px solid var(--ln);border-top:2px solid var(--c);border-radius:6px;padding:6px 8px;overflow:hidden}"
           ".cf{color:var(--c);font-size:8.5px}.cn2{color:var(--tx);font-size:10.5px;font-weight:600;margin:1px 0;word-break:break-word}"
           ".cp{color:var(--dim);font-size:8.5px}.man{background:var(--pnl2);border:1px solid var(--ln);border-radius:8px;"
           "padding:9px 11px;margin-bottom:9px}.manh{color:var(--warn);font-size:11px;margin-bottom:5px}.manh em{color:var(--dim);float:right;font-size:9px}"
           ".hrow{border-top:1px dashed var(--ln);padding:3px 0;font-size:10px;word-break:break-word}.hrow:first-of-type{border-top:none}"
           ".htag{color:var(--vi);margin-right:7px}.k{color:var(--dim)}.k:after{content:'=';color:var(--dim2)}"
           ".v{color:var(--tx);margin-right:9px}header{border-bottom:1px solid var(--ln);padding-bottom:16px;margin-bottom:18px}"
           "h1{margin:0;font-size:19px}h1 b{color:var(--cy)}.eyebrow{color:var(--dim);font-size:10.5px;text-transform:uppercase;letter-spacing:2px}"
           ".seatline{color:var(--dim);font-size:11.5px;margin-top:7px}.seatline span{color:var(--warn)}"
           ".hstat{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px}.hbadge{border:1px solid var(--ln2);border-radius:5px;padding:4px 9px;font-size:11px;background:var(--pnl)}"
           ".hbadge b{color:var(--cy)}footer{color:var(--dim);font-size:10px;margin-top:24px;border-top:1px solid var(--ln);padding-top:12px}")
css += (".bpmap{background:linear-gradient(180deg,#0d1526,#0b1120);border:1px solid var(--cy);border-radius:8px;padding:12px 14px;margin-bottom:16px}"
        ".bpflow{color:var(--cy);font-size:11px;margin:5px 0 10px;font-weight:600;word-break:break-word;line-height:1.7}"
        ".bprow{border-top:1px dashed var(--ln);padding:4px 0;font-size:10px;word-break:break-word}.bprow:first-of-type{border-top:none}"
        ".bpn{color:var(--warn);font-weight:600;margin-right:7px;display:inline-block;min-width:44px}.bpo{color:var(--tx)}.bpa{color:var(--up)}")

e = html.escape
FAM_COLORS = {"SEATCUBE": "#43e8d8", "OFFICECUBE": "#ffb454", "CONNECTORCUBE": "#a78bfa",
              "DASHBOARDCUBE": "#7ee787", "HOOKWALLCUBE": "#ff6b6b", "GNNCUBE": "#6cb6ff",
              "KERNELCUBE": "#f778ba", "TRANSLATORCUBE": "#e3b341", "RECEIPTCUBE": "#8b949e",
              "DBBHCUBE": "#5ce0a0"}

def crank_card(p):
    good = any(t in (p.get("status") or "") for t in ("MEASURED", "PUBLISHED", "CANON", "BILATERAL"))
    cls = "crank good" if good else "crank"
    return (f'<div class="{cls}"><div class=ct>{e(p.get("key",""))}</div>'
            f'<div class=cv>{e(p.get("status",""))}</div>'
            f'<div class=cn>{e(p.get("role",""))}</div></div>')

def cube_div(fam, name, pid):
    c = FAM_COLORS.get(fam, "#8b949e")
    return (f'<div class=cube style="--c:{c}"><div class=cf>{e(fam.replace("CUBE",""))}</div>'
            f'<div class=cn2>{e(name)}</div><div class=cp>{e(pid)}</div></div>')

def manifest_panel(name, rows):
    out = [f'<div class=man><div class=manh>{e(name)} <em>json=0</em></div>']
    for row in rows:
        tag, fields = parse_row(row)
        cells = "".join(
            (f'<span class=k>{e(k)}</span><span class=v>{e(v)}</span>' if v is not None else f'<span class=v>{e(k)}</span>')
            for k, v in fields)
        out.append(f'<div class=hrow><span class=htag>{e(tag)}</span>{cells}</div>')
    out.append("</div>")
    return "".join(out)

def bigpickle_panel():
    if not bpmap["spine"]: return ""
    spine = sorted(bpmap["spine"], key=lambda d: -int(d.get("n", "0")))
    flow = " &rarr; ".join(f'[{e(d.get("n",""))}]&nbsp;{e(d.get("role","").split("(")[0].split("-")[0][:15])}' for d in spine)
    out = ['<div class=bpmap><div class=manh style="color:var(--cy)">BIG PICKLE REBUILD &mdash; the ramp map, re-expressed in the NEWER systems (Rust HBI/HBP, json=0) <em>github stub &rarr; local newer</em></div>']
    out.append(f'<div class=bpflow>{flow} &rarr; <b>FLEET</b></div>')
    for d in spine:
        out.append(f'<div class=bprow><span class=bpn>[{e(d.get("n",""))}]</span><span class=bpo>{e(d.get("role","")[:56])}</span> <span class=bpa>&rarr; {e(d.get("newer",""))}</span></div>')
    r = bpmap["ramp"]
    if r: out.append(f'<div class=bprow><span class=bpn>RAMP</span><span class=bpo>{e(r.get("checkpoints",""))}</span> <span class=bpa>gulp@{e(r.get("gc_trigger_messages",""))} &rarr; {e(r.get("gulps_at_10k",""))} gulps@10k &middot; {e(r.get("throughput",""))}</span></div>')
    p = bpmap["pipeline"]
    if p: out.append(f'<div class=bprow><span class=bpn>PIPE</span><span class=bpo>{e(p.get("post_trigger","")[:72])}</span> <span class=bpa>= {e(p.get("equals",""))}</span></div>')
    n = bpmap["newer"]
    if n: out.append(f'<div class=bprow><span class=bpn>NEWER</span><span class=bpa>{e(n.get("law",""))}</span></div>')
    pm = bpmap["permanent"]
    if pm: out.append(f'<div class=bprow><span class=bpn>&#9873;</span><span class=bpa>{e(pm.get("reminder",""))} &middot; {e(pm.get("iterate",""))}</span></div>')
    out.append("</div>")
    return "".join(out)

# ---- assemble the page ----
parts = [
 "<!doctype html><html lang=en translate=no><head><meta charset=utf-8>",
 '<meta name=viewport content="width=device-width,initial-scale=1">',
 "<title>FABLE-5 &middot; raw HBI dashboard (rendered from backend)</title>",
 f"<style>{css}</style></head><body><div class=wrap>",
 "<header>",
 f'<div class=eyebrow>{e(seat.get("sector","SEC-FABLE5-1720"))} &middot; raw HBI stream &middot; pixels-first &middot; rendered-from-backend &middot; read-only</div>',
 "<h1><b>FABLE-5</b> &mdash; the room I work in</h1>",
 (f'<div class=seatline>seat <span>{e(seat.get("seat",""))}</span> &middot; pid <span>{e(seat.get("pid",""))}</span>'
  f' &middot; glyph <span>{e(seat.get("glyph",""))}</span> &middot; hilbert {e(seat.get("hilbert",""))} &middot; owner {e(seat.get("owner",""))}</div>'),
 "<div class=hstat>",
 f'<div class=hbadge>manifests <b>{len(hbp_docs)}</b> hbp</div>',
 f'<div class=hbadge>cube streams <b>{len(hbi_docs)}</b> hbi</div>',
 f'<div class=hbadge>work cranks <b>{len(pieces)}</b></div>',
 f'<div class=hbadge>cubes <b>{sum(len(v) for v in families.values())}</b></div>',
 '<div class=hbadge>backend <b>HBI / HBP</b> json=0</div><div class=hbadge>pixels-first <b>1</b></div><div class=hbadge>fire <b>0</b></div>',
 "</div></header>",
 '<div class=sect>big pickle rebuild &mdash; the ramp map re-expressed in the newer systems (pixels-first, from the backend)</div>',
 bigpickle_panel(),
 '<div class=sect>work cranks &mdash; rendered from every PIECE row in the backend HBP</div>',
 '<div class=cranks>' + "".join(crank_card(p) for p in pieces) + "</div>",
 '<div class=sect>self-prism &mdash; me + my work as descriptor cubes (from the .hbi EMIT streams)</div>',
]
for fam, cubes in families.items():
    c = FAM_COLORS.get(fam, "#8b949e")
    parts.append(f'<div class=cubefam><h4 style="color:{c}">{e(fam)} <em>&times;{len(cubes)}</em></h4><div class=cubes>'
                 + "".join(cube_div(fam, n, pid) for n, pid in cubes) + "</div></div>")
parts.append('<div class=sect>office &mdash; raw HBI manifests (the backend source; the pixels above are rendered from these)</div>')
for name in sorted(hbp_docs):
    parts.append(manifest_panel(name, hbp_docs[name]))
parts.append(
    f'<footer>rendered by render-fable5-dashboard.py from the FABLE5 backend HBI '
    f'({len(hbp_docs)} hbp + {len(hbi_docs)} hbi manifests) &middot; pixels-first &middot; json=0 &middot; E=0 &middot; '
    f'hand-editing this HTML is banned &mdash; change the backend .hbp and re-render</footer>')
parts.append("</div></body></html>")

body = "".join(parts)
open(OUT, "w", encoding="utf-8", newline="\n").write(body)
sh = hashlib.sha256(body.encode()).hexdigest()
open(OUT + ".sha256", "w", encoding="utf-8", newline="\n").write(f"{sh}  fable5-dashboard.html\n")
print(f"RENDERED fable5-dashboard.html  {len(body)}B  sha256={sh[:16]}")
print(f"  from {len(hbp_docs)} hbp + {len(hbi_docs)} hbi backend manifests")
print(f"  {len(pieces)} work-cranks, {sum(len(v) for v in families.values())} cubes across {len(families)} families")
dbbh = [p for p in pieces if 'dbbh' in p.get('key','').lower() or 'black-hole' in p.get('key','').lower() or 'quant-prism' in p.get('key','').lower()]
print(f"  DBBH-CQP cranks now rendered: {len(dbbh)}  families incl DBBHCUBE: {'DBBHCUBE' in families} ({len(families.get('DBBHCUBE',[]))} cubes)")
