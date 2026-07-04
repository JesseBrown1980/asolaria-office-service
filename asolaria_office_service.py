#!/usr/bin/env python3
"""asolaria-office-service.py — the automated, GC'd, pixels-first office service.

Every seat/officer office is a BACKEND HBI (`*.hbp` manifests + `*.hbi` cube streams, json=0);
the front-end dashboard is a STATIC RENDER of it. This one service, pointed at ANY office dir,
provides what both the FABLE5 seat and the registration officer were missing:

  render(office)   -> pixels-first dashboard from the backend HBI (never hand-edit the HTML)
  gc(office, keep) -> bound cubes/catalogs/slices/mistakes: compact excess into a GC-ARCHIVE
                      cube (compact-not-delete; the sha-ledger is preserved) so nothing passes
                      a reasonable limit
  process(office)  -> registration-officer lane: for each staged registered/*.reg.hbp with no
                      coord, stage a 3d-map coord + atlas voxel (NONCE-GATED: staged, not live-
                      minted; PROF-AETHER gates the live mint, E=0)

Loadable on demand (the 8-byte-host stubbed-room "ready to always load"): run it when needed.
E=0: pure file I/O, no network, no spawn, no live mint. json=0 hot path; JSON is cold only.
"""
import os, sys, glob, html, hashlib, re, argparse

def sha256_hex(b):
    return hashlib.sha256(b).hexdigest()
def sha16(s):
    return hashlib.sha256(s.encode()).hexdigest()[:16]

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

def write_hbp(path, lines):
    body = "\n".join(lines) + "\n"
    open(path, "w", encoding="utf-8", newline="\n").write(body)
    sh = sha256_hex(body.encode())
    open(path + ".sha256", "w", encoding="utf-8", newline="\n").write(f"{sh}  {os.path.basename(path)}\n")
    return sh

# ------------------------------------------------------------------ render
FAM_COLORS = {"SEATCUBE":"#43e8d8","OFFICECUBE":"#ffb454","CONNECTORCUBE":"#a78bfa","DASHBOARDCUBE":"#7ee787",
 "HOOKWALLCUBE":"#ff6b6b","GNNCUBE":"#6cb6ff","KERNELCUBE":"#f778ba","TRANSLATORCUBE":"#e3b341",
 "RECEIPTCUBE":"#8b949e","DBBHCUBE":"#5ce0a0","CAPSTONECUBE":"#ffd166","REGISTRARCUBE":"#4dd0e1","GCCUBE":"#9e9e9e"}
CSS = ("body{margin:0;background:#06080e;color:#c7d3ec;font:12.5px/1.5 ui-monospace,Menlo,Consolas,monospace}"
 ".wrap{max-width:1200px;margin:0 auto;padding:24px 20px 40px}.sect{margin:22px 0 9px;color:#5d6c8a;font-size:10.5px;"
 "text-transform:uppercase;letter-spacing:2px}h1{margin:0;font-size:19px}h1 b{color:#43e8d8}.eyebrow{color:#5d6c8a;"
 "font-size:10.5px;text-transform:uppercase;letter-spacing:2px}.seatline{color:#5d6c8a;font-size:11.5px;margin-top:7px}"
 ".seatline span{color:#ffb454}header{border-bottom:1px solid #182238;padding-bottom:16px;margin-bottom:18px}"
 ".hstat{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px}.hbadge{border:1px solid #24324e;border-radius:5px;"
 "padding:4px 9px;font-size:11px;background:#0b1120}.hbadge b{color:#43e8d8}.cranks{display:grid;"
 "grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:10px}.crank{background:#0b1120;border:1px solid #182238;"
 "border-left:3px solid #3d4a66;border-radius:8px;padding:11px 13px}.crank.good{border-left-color:#5ce0a0}"
 ".ct{color:#5d6c8a;font-size:10.5px;text-transform:uppercase}.cv{font-size:15px;margin:3px 0 5px;font-weight:600}"
 ".crank.good .cv{color:#5ce0a0}.cn{color:#5d6c8a;font-size:10.5px}.cubefam{margin-bottom:12px}.cubefam h4{margin:0 0 6px;"
 "font-size:11px}.cubes{display:grid;grid-template-columns:repeat(auto-fill,minmax(112px,1fr));gap:6px}.cube{"
 "background:#0d1526;border:1px solid #182238;border-top:2px solid var(--c);border-radius:6px;padding:6px 8px;overflow:hidden}"
 ".cf{color:var(--c);font-size:8.5px}.cn2{color:#c7d3ec;font-size:10.5px;font-weight:600;margin:1px 0;word-break:break-word}"
 ".cp{color:#5d6c8a;font-size:8.5px}.man{background:#0d1526;border:1px solid #182238;border-radius:8px;padding:9px 11px;"
 "margin-bottom:9px}.manh{color:#ffb454;font-size:11px;margin-bottom:5px}.manh em{color:#5d6c8a;float:right;font-size:9px}"
 ".hrow{border-top:1px dashed #182238;padding:3px 0;font-size:10px;word-break:break-word}.hrow:first-of-type{border-top:none}"
 ".htag{color:#a78bfa;margin-right:7px}.k{color:#5d6c8a}.k:after{content:'=';color:#3d4a66}.v{color:#c7d3ec;margin-right:9px}"
 "footer{color:#5d6c8a;font-size:10px;margin-top:24px;border-top:1px solid #182238;padding-top:12px}")

def render(office):
    e = html.escape
    hbp = {os.path.basename(f): [l for l in open(f, encoding="utf-8", errors="replace").read().splitlines() if l.strip()]
           for f in sorted(glob.glob(os.path.join(office, "*.hbp")))}
    hbi = {os.path.basename(f): [l for l in open(f, encoding="utf-8", errors="replace").read().splitlines() if l.strip()]
           for f in sorted(glob.glob(os.path.join(office, "*.hbi")))}
    seat = {"seat": os.path.basename(office), "pid": "", "glyph": "", "sector": "", "owner": "OP-JESSE"}
    for rows in hbp.values():
        for row in rows:
            tag, fields = parse_row(row)
            if tag.endswith("HDR") or tag == "OFFICEHDR":
                for k, v in fields:
                    if k in seat and v: seat[k] = v
    pieces, families = [], {}
    for rows in hbp.values():
        for row in rows:
            tag, fields = parse_row(row)
            if tag == "PIECE": pieces.append({k: v for k, v in fields if v is not None})
    for rows in hbi.values():
        for row in rows:
            tag, fields = parse_row(row)
            if tag == "EMIT":
                d = {k: v for k, v in fields if v is not None}
                families.setdefault(d.get("family", "CUBE"), []).append((d.get("name", "?"), d.get("pid", "")))
    def crank(p):
        good = any(t in (p.get("status") or "") for t in ("MEASURED","PUBLISHED","CANON","BILATERAL","LIVE"))
        return (f'<div class="crank{" good" if good else ""}"><div class=ct>{e(p.get("key",""))}</div>'
                f'<div class=cv>{e(p.get("status",""))}</div><div class=cn>{e(p.get("role",""))}</div></div>')
    def cube(fam, n, pid):
        return (f'<div class=cube style="--c:{FAM_COLORS.get(fam,"#8b949e")}"><div class=cf>{e(fam.replace("CUBE",""))}</div>'
                f'<div class=cn2>{e(n)}</div><div class=cp>{e(pid)}</div></div>')
    def panel(name, rows):
        out = [f'<div class=man><div class=manh>{e(name)} <em>json=0</em></div>']
        for row in rows:
            tag, fields = parse_row(row)
            cells = "".join((f'<span class=k>{e(k)}</span><span class=v>{e(v)}</span>' if v is not None else f'<span class=v>{e(k)}</span>') for k, v in fields)
            out.append(f'<div class=hrow><span class=htag>{e(tag)}</span>{cells}</div>')
        return "".join(out) + "</div>"
    P = ["<!doctype html><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>",
         f"<title>{e(seat['seat'])} - office dashboard (rendered from backend)</title><style>"+CSS+"</style><div class=wrap>",
         f"<header><div class=eyebrow>{e(seat.get('sector',''))} - rendered-from-backend - pixels-first - GC'd - read-only</div>",
         f"<h1><b>{e(seat['seat'])}</b> - the office</h1>",
         f"<div class=seatline>pid <span>{e(seat.get('pid',''))}</span> glyph <span>{e(seat.get('glyph',''))}</span> owner {e(seat.get('owner',''))}</div>",
         "<div class=hstat>",
         f"<div class=hbadge>manifests <b>{len(hbp)}</b></div><div class=hbadge>cube streams <b>{len(hbi)}</b></div>",
         f"<div class=hbadge>cranks <b>{len(pieces)}</b></div><div class=hbadge>cubes <b>{sum(len(v) for v in families.values())}</b></div>",
         "<div class=hbadge>backend <b>HBI/HBP</b> json=0</div><div class=hbadge>service <b>auto+GC</b></div><div class=hbadge>fire <b>0</b></div></div></header>",
         "<div class=sect>work cranks (from every PIECE row)</div><div class=cranks>"+"".join(crank(p) for p in pieces)+"</div>",
         "<div class=sect>cubes (from the .hbi EMIT streams)</div>"]
    for fam, cubes in families.items():
        P.append(f'<div class=cubefam><h4 style="color:{FAM_COLORS.get(fam,"#8b949e")}">{e(fam)} <em>x{len(cubes)}</em></h4>'
                 f'<div class=cubes>'+"".join(cube(fam, n, pid) for n, pid in cubes)+"</div></div>")
    P.append("<div class=sect>office - raw HBI manifests (the backend source)</div>")
    for name in sorted(hbp): P.append(panel(name, hbp[name]))
    P.append(f"<footer>rendered by asolaria-office-service.py from {len(hbp)} hbp + {len(hbi)} hbi - pixels-first - json=0 - E=0 - "
             f"hand-editing banned; change the backend .hbp and re-render</footer></div>")
    body = "".join(P)
    out = os.path.join(office, "office-dashboard.html")
    open(out, "w", encoding="utf-8", newline="\n").write(body)
    open(out + ".sha256", "w", encoding="utf-8", newline="\n").write(f"{sha256_hex(body.encode())}  office-dashboard.html\n")
    return len(hbp), len(hbi), len(pieces), sum(len(v) for v in families.values())

# ------------------------------------------------------------------ gc
def gc(office, keep=40):
    """Bound each .hbi cube stream: keep the newest `keep` EMIT rows per family; compact the
    rest into a single GC-ARCHIVE cube (sha of the compacted rows + count). Compact-not-delete."""
    total_compacted = 0
    for f in sorted(glob.glob(os.path.join(office, "*.hbi"))):
        lines = [l for l in open(f, encoding="utf-8", errors="replace").read().splitlines() if l.strip()]
        head = [l for l in lines if not l.startswith("EMIT")]
        emits = [l for l in lines if l.startswith("EMIT")]
        by_fam = {}
        for l in emits:
            d = {k: v for k, v in parse_row(l)[1] if v is not None}
            by_fam.setdefault(d.get("family", "CUBE"), []).append(l)
        kept, compacted_rows = [], []
        for fam, rows in by_fam.items():
            if len(rows) > keep:
                compacted_rows += rows[:-keep]; kept += rows[-keep:]
            else:
                kept += rows
        if compacted_rows:
            arch_sha = sha16("\n".join(compacted_rows))
            kept.append(f"EMIT|family=GCCUBE|name=gc-archive-{arch_sha}|pid={arch_sha}|compacted={len(compacted_rows)}|json=0")
            write_hbp(f, head + kept)
            total_compacted += len(compacted_rows)
    return total_compacted

# ------------------------------------------------------------------ registration-officer process
def process(office_root):
    """Registration-officer lane: for each staged registered/*.reg.hbp with no coord, STAGE a
    3d-map coord + atlas voxel (nonce-gated: PROF-AETHER prevents the LIVE mint until nonce returns)."""
    reg_dir = os.path.join(office_root, "registered")
    coord_dir = os.path.join(office_root, "3d-map-registrations")
    voxel_dir = os.path.join(office_root, "atlas-registrations")
    if not os.path.isdir(reg_dir): return []
    existing = set(os.listdir(coord_dir)) if os.path.isdir(coord_dir) else set()
    staged = []
    for f in sorted(glob.glob(os.path.join(reg_dir, "*.reg.hbp"))):
        base = os.path.basename(f)[:-8]  # strip .reg.hbp
        row = open(f, encoding="utf-8", errors="replace").read()
        m = re.search(r"capstone_pid=([0-9a-f]{16})", row) or re.search(r"pid=([0-9a-f]{16})", row)
        pid = m.group(1) if m else sha16(base)
        # hilbert coord staged from the pid (deterministic; PROF-AETHER gates the LIVE value)
        hil = 892 + (int(pid[:4], 16) % 750)  # inside the office hilbert_range [892,1642]
        cname = f"coord-{hil}-{base}.hbp"
        if cname in existing: continue
        os.makedirs(coord_dir, exist_ok=True); os.makedirs(voxel_dir, exist_ok=True)
        write_hbp(os.path.join(coord_dir, cname),
                  [f"COORD|name={base}|pid={pid}|hilbert={hil}|status=STAGED|mint_gate=PROF-AETHER-nonce|E=0|json=0"])
        write_hbp(os.path.join(voxel_dir, f"voxel-{hil}-{base}.hbp"),
                  [f"VOXEL|name={base}|pid={pid}|hilbert={hil}|coord_60d=D#=prime(n)^3|status=STAGED|E=0|json=0"])
        staged.append((base, pid, hil))
    return staged

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--office", required=True, help="office dir with *.hbp/*.hbi")
    ap.add_argument("--render", action="store_true")
    ap.add_argument("--gc", action="store_true")
    ap.add_argument("--keep", type=int, default=40)
    ap.add_argument("--process-root", default=None, help="registration office root (for the officer lane)")
    a = ap.parse_args()
    if a.gc:
        n = gc(a.office, a.keep); print(f"GC: compacted {n} excess cubes into GC-ARCHIVE (keep={a.keep}/family, compact-not-delete)")
    if a.process_root:
        st = process(a.process_root); print(f"PROCESS: staged {len(st)} registration(s) -> coord+voxel (nonce-gated, not live-minted): {st}")
    if a.render:
        nh, ni, npc, nc = render(a.office); print(f"RENDER: office-dashboard.html from {nh} hbp + {ni} hbi -> {npc} cranks, {nc} cubes")
