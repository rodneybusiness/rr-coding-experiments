# Context Addendum — v1.3.0

**Change requested by Rodney:** Treat outreach to talent/incoming pitches and idea vetting as a **separate gate** before Development.
**Resolution:** Introduced `CP-ORIG` (Creative Origination & Vetting) as DRI of the first phase and renamed the phase to **Origin** (ID stays `DISCOVER`).
Gate `G_ORIGIN_APPROVED` now controls entry into Development (keeps legacy alias `G_DEV_APPROVED` for continuity).

**Boundaries clarified:**
- `TA-DISCOVER` owns **people pipeline** (rosters, outreach).  
- `CP-ORIG` owns **concept pipeline** (pitches, internal ideas, matching ideas ↔ talent) and the editorial decision to proceed.  
- Contract execution remains with `SOL-LEGAL` in DEALS; partner negotiations remain with `BP-*`.
