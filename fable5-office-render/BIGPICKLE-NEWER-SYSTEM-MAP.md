# Big Pickle Rebuild → Newer Systems (Rust HBI/HBP) — the FABLE5 office map

The `bigpickle-rebuild` repo is the **public stub** of the spread-out local old-Node system. This maps its ramp architecture onto the newer systems (Rust 8-byte Host-8, HBI/HBP hot-path, json=0), rendered pixels-first onto the FABLE5 office wall.

## The spine (mechanism → fleet), re-expressed newer
| # | old (node bigpickle) | newer (rust host-8) |
|---|---|---|
| 5 | collision discipline (BH × prime × rule-of-3 / cascade→PRISM) | rust host8 collision lanes |
| 4 | service-multiplication algorithm (replicate S → N×M reductions) | rust reduction crate |
| 3 | reduction principle (multiply service → multiply PRISM reductions) | PRISM many→1 |
| 2 | 200ns revolver PID emitter (→ 1.16T agents/s) | rust 8-byte emitter |
| 1 | router (FEDENV → 1000-slot table → worker_threads) | rust omnidispatch :4950 FEDENV-v1 |
| 0 | THE FLEET (spindles + Host-8 + 10k/20k/100k kernels) | rust host8 runtime + fable5 rooms |

Inside the fleet: `trigger → spindle → HOOKWALL → GNN-ensemble(7gnn/8signals) → Shannon/OmniShannon → white-rooms → GULP` = **PRISM many→1**.

## The ramp canon (corrected)
- Checkpoints: **1 → 10 → 100 → 1000 → 10000 agents**.
- GC gulp every **2000 messages** (`GC_TRIGGER_MESSAGES=2000`) → 10K = **5 gulps** (flow-not-pile-up; **not** N:1).
- Throughput: 63 000 msg/s single-host, 189 000 msg/s across 3 hosts.

## Room & sector
- **Single room** = a micro-kernel descriptor: PID anchor (Brown-Hilbert prime) · beat-range · 7-lane set (post-lymphatic) · result-HBP path.
- **Sector** = ONE `manifest.hbp` with N rows (lazy — not N files; 10k ≈ 1 MB).

## Foundation-v1 invariants (Class-1 immutable)
1. Port = label in N^K prefix tree (single-socket multiplex, O(K) walk — NOT tcp-per-port).
2. PID = `(actor, device, lane, prime)` Hilbert-bijective tuple (zero collisions, formula-derived).
3. Frontend inert (orchestrate + guide, no shell wrapper).
4. Backend shelless rotation (function calls: sha16 PID-mint + verdict — not process spawns).

## Non-goals (anti-divergence)
❌ 380k local processes · ❌ tcp-per-port · ❌ pre-mint 100B PIDs as files (memory explosion) · ❌ per-spawn cosign (batch @ 1s) · ❌ Claude-identifier headers outbound.

## Clean-room
Build from Foundation-v1 spec only; never read the `_big-pickle-quarantine` source (taint risk); test the quarantined original as a **black-box oracle** by SHA256-diff, never by reading its source.

## Hot path (already native in the office)
Every artifact = `.hbp` + `.hbi` + `.sha256` (+ `.hex`). JSON is COLD (compat / debug / dashboard) only. The FABLE5 office wall (`fable5-dashboard.html`) is a **pixels-first render** of the backend `.hbp`/`.hbi` — change the backend + re-render via `render-fable5-dashboard.py`; hand-editing the HTML is banned.

**Law:** old (node bigpickle) decodes new (rust host-8) — every level translator is a bijection, so `H(f(X)) = H(X)`; the 256↔1024 rung is MEASURED, the rest is CANON frame.
