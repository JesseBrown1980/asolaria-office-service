# asolaria-office-service

The automated, GC-d, pixels-first office service. Point it at ANY seat/officer office (backend HBI `*.hbp`/`*.hbi`, json=0) and it: **render** (pixels-first dashboard from the backend, never hand-edit) - **gc** (bound cubes/catalogs/slices: compact excess into a GC-ARCHIVE cube, compact-not-delete) - **process** (registration-officer lane: stage coord+voxel for each staged `.reg`, nonce-gated by PROF-AETHER). E=0, pure file I/O, no network/spawn/live-mint. Loadable on demand (8-byte-host stubbed-room "ready to always load").

Built because both the FABLE5 seat and the registration officer were file-piles with a hand-run projection and no GC. Now one service gives every office the automated backend-first + GC treatment.

```
python asolaria_office_service.py --office <office_dir> --render --gc --keep 40
python asolaria_office_service.py --office <root> --process-root <root>   # officer lane
```

MIT OR Apache-2.0.
