import hashlib, time, os
OFFICE = "/mnt/d/PID-Registration-Office/offices/FABLE5-8467a937cba309f7"
def sha16(x): return hashlib.sha256(x.encode()).hexdigest()[:16]
def sha256hex(b): return hashlib.sha256(b).hexdigest()
TS = "2026-07-04T22:20:00Z"

# ============ 1) THE PERMANENT MAP: bigpickle-rebuild -> FABLE5 office, newer systems ============
seed = sha16("EMITTER-SEED|8467a937cba309f7|bigpickle-map")
def npid(p, n): return sha16(p + "|" + n)
pid = seed
rows = ["BIGPICKLEMAPHDR|seat=ACER-CLAUDE-FABLE5|pid=8467a937cba309f7|ts=" + TS + "|source=github:JesseBrown1980/bigpickle-rebuild(PUBLIC-STUB)|local=spread-out-OLD-node-system|target=NEWER-rust-hbi-hbp-no-json|json=0"]
emits = []
def add(row, name):
    global pid
    pid = npid(pid, name)
    rows.append(row + "|pid=" + pid + "|json=0")
    emits.append("EMIT|family=BIGPICKLEMAPCUBE|name=" + name + "|pid=" + pid + "|json=0")

# the spine (mechanism -> fleet), each with its newer-system re-expression
add("SPINE|n=5|repo=waves-and-cascades|role=collision-discipline(avoid BH x prime x rule-of-3 / cause cascade->PRISM)|newer=rust-host8-collision-lanes", "spine-5-collision")
add("SPINE|n=4|repo=Algorithms-of-Asolaria|role=service-multiplication-algo(replicate S -> NxM reductions)|newer=rust-reduction-crate", "spine-4-algorithm")
add("SPINE|n=3|repo=how-do-we-get-reductions|role=principle-multiply-service-multiplies-PRISM-reductions|newer=prism-many-to-1", "spine-3-reduction")
add("SPINE|n=2|repo=full-works-200ns-emitter|role=200ns-revolver-PID-emitter->1.16T-agents/s|newer=rust-8byte-emitter", "spine-2-emitter")
add("SPINE|n=1|repo=omni-dispatcher|role=router-FEDENV-envelopes->1000-slot-table->worker_threads|newer=rust-omnidispatch-4950-FEDENV-v1", "spine-1-router")
add("SPINE|n=0|repo=Asolaria-hermes-work|role=THE-FLEET-terminus-spindles+dispatcher-citizen+Host8+10k/20k/100k-kernels|newer=rust-host8-runtime-fable5-rooms", "spine-0-fleet")

# the ramp checkpoints (CORRECTED: GC gulp every 2000)
add("RAMP|checkpoints=1,10,100,1000,10000-agents|gc_trigger_messages=2000|gulps_at_10k=5|throughput=63000msg/s-single;189000-3host|discipline=flow-not-pile-up", "ramp-checkpoints")

# the post-trigger pipeline (inside the fleet) = the 8-stage = PRISM many->1
add("PIPELINE|post_trigger=trigger->spindle->HOOKWALL->GNN-ensemble(7gnn/8signals)->Shannon/OmniShannon->white-rooms->GULP|equals=PRISM-many-to-1|maps_to=loop_pending-8stage", "pipeline-post-trigger")

# single-room + sector (the concrete example)
add("ROOM|single=micro-kernel-descriptor|fields=pid-anchor(BH-prime)+beat-range+lane-set(7-post-lymphatic)+result-hbp-path|row=MK|idx|pid|prime|anchor|beat_range|lanes|result_path|status=MINTED", "single-room-microkernel")
add("SECTOR|batch=ONE-manifest.hbp-with-N-rows(NOT-N-files)|lazy|10k=~1MB|maps_to=fable5-office-D:-shards", "sector-one-manifest-many-rows")

# Foundation-v1 invariants
add("INVARIANT|1=port=label-in-N^K-prefix-tree(single-socket-multiplex-O(K)-walk-NOT-tcp-per-port)|2=PID=(actor,device,lane,prime)-hilbert-bijective-zero-collision|3=frontend-inert(orchestrate-not-wrap)|4=backend-shelless-rotation(function-calls-not-process-spawns)", "invariants-foundation-v1")

# hot path (already ours; confirm)
add("HOTPATH|artifact=.hbp+.hbi+.sha256+.hex|json=COLD-compat/debug/dashboard-only|status=ALREADY-NATIVE-in-fable5-office", "hotpath-hbp-hbi")

# modules -> newer-system owners
add("MODULES|port-router|pid-minter|aot-runner|hbp-emitter|auto-translate|hookwall|gnn-forward|gnn-reverse-gain|gc-runtime(gulp@2000)|pid-chain-revolver|newer=rust-federation-1024-10-server-crates", "modules-10")

# non-goals (anti-divergence)
add("NONGOAL|no-380k-local-processes|no-tcp-per-port|no-premint-100B-PIDs-as-files(memory-explosion)|no-per-spawn-cosign(batch@1s)|no-claude-headers-outbound", "nongoals-antidivergence")

# newer-system target + clean-room
add("NEWERSYSTEM|target=asolaria-federation-1024=RUST-8byte-HOST8-no_std-kernel+10-server-crates(council/host8/agent-runtime/gnn-oracle/vote-quorum/cosign-ledger/dashboard-serve/fischer-eval/tier-policy/highway)|law=old(node-bigpickle)-decodes-new(rust-host8)|256<->1024-rung-MEASURED-rest-CANON", "newer-system-target")
add("CLEANROOM|may_read=foundation-v1-spec(00-07)+brown-hilbert+hot-path|may_not=_big-pickle-quarantine-source-taint|test=oracle-blackbox-SHA256-diff-never-read-source", "cleanroom-discipline")
add("PERMANENT|this=the-map-on-the-fable5-office-wall|reminder=reveal-bigpickle-rebuild-in-newer-rust-hbi-hbp-systems|iterate=map-check-test-improve", "permanent-reminder")

hbp = "\n".join(rows) + "\n"
hbi = "\n".join(emits) + "\n"
b = "FABLE5-BIGPICKLE-MAP-2026-07-04"
open(OFFICE + "/" + b + ".hbp", "w", newline="\n").write(hbp)
open(OFFICE + "/" + b + ".hbi", "w", newline="\n").write(hbi)
open(OFFICE + "/" + b + ".hbp.sha256", "w", newline="\n").write(sha256hex(hbp.encode()) + "  " + b + ".hbp\n")
open(OFFICE + "/" + b + ".hbi.sha256", "w", newline="\n").write(sha256hex(hbi.encode()) + "  " + b + ".hbi\n")
print("MAPPED bigpickle-rebuild -> FABLE5 office: " + str(len(rows) - 1) + " cubes, sha256=" + sha256hex(hbp.encode())[:16])

# ============ 2) CORRECTED RAMP: GC gulp every 2000 messages (canon), not N:1 ============
WARM = OFFICE + "/warmup-2026-07-04"
os.makedirs(WARM, exist_ok=True)
GC = 2000
print("")
print("=== CORRECTED WARM-UP RAMP (canon: GC gulp every " + str(GC) + " msgs = flow-not-pile-up) ===")
print("%7s %9s %7s %8s %6s" % ("scale", "emit_ms", "gulps", "MB", "held"))
pid2 = sha16("EMITTER-SEED|8467a937cba309f7|ramp2")
ok_all = True
for N in [1, 10, 100, 1000, 10000]:
    t0 = time.time()
    rows2 = []
    gulps = 0
    carried = 0
    for i in range(N):
        pid2 = sha16(pid2 + "|" + str(i))
        rows2.append("MK|idx=" + str(i) + "|pid=" + pid2 + "|status=MINTED|review=hookwall,gnn,shannon,whiteroom|auto_fire=0|json=0")
        carried += 1
        if carried >= GC:          # GULP fires at the 2000 threshold (mint-or-discard, flow not pile-up)
            gulps += 1
            carried = 0
    if carried > 0:
        gulps += 1                 # final partial gulp
    batch = "\n".join(rows2) + "\n"
    t_emit = time.time() - t0
    bf = WARM + "/ramp2-" + str(N) + ".hbp"
    open(bf, "w", newline="\n").write(batch)
    sha = sha256hex(batch.encode())
    open(bf + ".sha256", "w", newline="\n").write(sha + "  ramp2-" + str(N) + ".hbp\n")
    held = (open(bf).read().count("\n") == N)
    ok_all = ok_all and held
    print("%7d %9.1f %7d %8.2f %6s" % (N, t_emit * 1000, gulps, len(batch.encode()) / 1048576.0, str(held)))
print("")
print("RAMP (canon gulp@2000): 10k -> 5 gulps (matches SPEC 10000/2000=5). all_held=" + str(ok_all))
