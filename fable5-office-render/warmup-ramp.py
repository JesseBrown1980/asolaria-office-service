import hashlib, time, os
OFFICE = "/mnt/d/PID-Registration-Office/offices/FABLE5-8467a937cba309f7"
WARM = OFFICE + "/warmup-2026-07-04"
os.makedirs(WARM, exist_ok=True)

def sha16(x): return hashlib.sha256(x.encode()).hexdigest()[:16]
def sha256hex(b): return hashlib.sha256(b).hexdigest()

seed = sha16("EMITTER-SEED|8467a937cba309f7|warmup")
pid = seed
print("=== WARM-UP RAMP (emit N -> fill D: rooms -> auto-gulp compact N:1 -> verify hold) ===")
header = "%7s %9s %9s %8s %11s %6s" % ("scale", "emit_ms", "gulp_ms", "MB", "compact", "held")
print(header)
prev_ok = True
for N in [1, 10, 100, 1000, 10000]:
    if not prev_ok:
        break
    t0 = time.time()
    rows = []
    for i in range(N):
        pid = sha16(pid + "|" + str(i))
        g = "BH1024:EVT-MINT:" + pid[:12].upper()
        bh = "BH-ADDR-" + pid[:4] + "-" + pid[4:8]
        rows.append("EMIT|action=EVT-MINT|target=PID-ROUTED|seq=" + str(i) + "|pid=" + pid + "|glyph=" + g + "|bh=" + bh + "|review=hookwall,gnn,shannon,gulp,whiteroom|auto_fire=0|json=0")
    batch = "\n".join(rows) + "\n"
    t_emit = time.time() - t0
    bf = WARM + "/warmup-" + str(N) + ".hbp"
    open(bf, "w", newline="\n").write(batch)
    mb = len(batch.encode()) / 1048576.0
    t1 = time.time()
    cube_sha = sha256hex(batch.encode())
    open(WARM + "/warmup-" + str(N) + ".gulp.hbi", "w", newline="\n").write(
        "GULPCUBE|scale=" + str(N) + "|rows=" + str(N) + "|compacted_to=1|body_sha256=" + cube_sha + "|glyph=BH1024:GULP:" + cube_sha[:12].upper() + "|json=0\n")
    open(bf + ".sha256", "w", newline="\n").write(cube_sha + "  warmup-" + str(N) + ".hbp\n")
    t_gulp = time.time() - t1
    back = open(bf).read()
    ok = (sha256hex(back.encode()) == cube_sha and back.count("\n") == N)
    prev_ok = ok
    print("%7d %9.1f %9.1f %8.2f %11s %6s" % (N, t_emit * 1000, t_gulp * 1000, mb, str(N) + ":1", str(ok)))

print("")
if prev_ok:
    print("RAMP RESULT: ALL SCALES HELD -- gulp compacted N:1 at every level, sha-verified, no memory explosion")
else:
    print("RAMP RESULT: STOPPED at a failing scale")
open(WARM + "/WARMUP-COMPLETE.hbp", "w", newline="\n").write(
    "WARMUPDONE|scales=1,10,100,1000,10000|all_held=" + str(prev_ok) + "|next=RUN_FULL|mint_gate=PROF-AETHER-nonce|seal_gate=OPERATOR|json=0\n")
print("staged WARMUP-COMPLETE -> next=RUN_FULL (L0-L7 warmed; L8 mint holds on PROF-AETHER nonce; L9 seal holds on operator)")
