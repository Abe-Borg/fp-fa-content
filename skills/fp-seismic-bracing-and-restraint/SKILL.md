---
name: FP seismic bracing and restraint
description: >-
  use this when a wet, dry or double-interlock preaction sprinkler system sits in a seismic area
  and you must set the seismic coefficient, brace spacing, zone-of-influence (ZOI) brace loads,
  the standard brace detail, clearances and flexibility for mains and the riser, and print the
  delta vs NFPA 13-2025 Ch. 18. Not gas/fuel piping restraint (FM DS 1-11), not the post-earthquake
  water-supply memo, not structural attachment design (SEOR), not CAD.
---

# FP seismic bracing and restraint

**Scope lock:** the system is wet, dry or double-interlock preaction only. Dry and DI systems always have an N₂ generator and compressor, and hydraulics use C = 100. Foam, clean agent, mist (`PRACTICE REFUSED`) and single-interlock are a Stop. A single-interlock system may appear only as a comparison.

This is US work under the Design practice:
- a 3-layer basis, taking the most stringent per parameter;
- the delta vs NFPA 13-2025;
- show-and-verify math;
- every cite with section and edition;
- `[SYN]` on any invented value;
- Verify with the engineer of record plus a conservative assumption on every judgment call.

The packet is optional. Fill any gap with a stated `ASSUMED` value (the value used and why). Keep the Skill generic: no project names and no client paths.

## 1. Three-layer basis

| Layer | Source | Use |
|---|---|---|
| Code | NFPA 13 Ch. 18 (2025 delta, enforced edition per AHJ) + ASCE 7 Ch. 13 via IBC | Brace spacing, clearance, flexibility. ASCE 7 text is not in the pulls, so it stays `[V]` |
| Insurer | FM DS 2-8 (Oct-2017 / Interim Apr-2025) for sprinkler bracing; FM DS 1-2 for generic SDS when the SEOR is pending | Usually controlling for G, Wp, the detail and bans |
| Owner | Risk Category, designated-seismic system, Ip | RFI when not given |

**Held NFPA 13-2025 pins** (pull 13-12):
- Lateral braces ≤ 40 ft on center [§18.5.5.2.2].
  - 40 ft is the **ceiling**. The Fpw tables can force tighter spacing. Worked case: S_DS 1.2, Cp 0.9048, 4 in. Sch 40 main fails at 40 ft (897 > 850 lb) and passes at 30–35 ft. 30 ft is a **calculated result for that case**, not a code spacing [SYN example]. Never state 30 ft as the NFPA rule.
  - **FM DS 2-8 checked (2026-10-23d):** FM straight-run maximums are **40 ft lateral / 80 ft longitudinal** on feed and cross mains [FM DS 2-8 Oct-2017 / Interim Rev. Apr-2025 §2.2.1.1.4.4]; longitudinal brace within 40 ft of the end, lateral within 6 ft of the end [§2.2.1.1.4.2]. FM expressly allows **smaller spacing** when brace, connection or structure capacity governs [§2.2.1.1.1; commentary §3.1.2]. So the 35 ft SDC D result for a 6 in. main below is **consistent** with FM: it is a load-driven reduction under the 40 ft maximum, not a new rule. No conflict.
- Longitudinal braces on feed and cross mains ≤ 80 ft on center [§18.5.6.1]. Branch lines are also 80 ft unless §18.5.9.6 is met [§18.5.6.2].
- The last brace is ≤ 40 ft from the end of the pipe or a change of direction [§18.5.6.4].
- Clearance holes are 2 in. larger for 1–3½ in. pipe and 4 in. larger for 4 in. pipe and up [§18.4.2].
- Everything else in Ch. 18 stays `[V]` until pulled.

## 2. Steps

1. **Zone and G.**
   - Use the SEOR's SDS when it is available. Otherwise use the FM DS 1-2 generic value, flag it `ASSUMED` and keep it `[V]` until the FM map is pinned.
   - Sprinkler G = 0.754 · SDS (ASD) [CODE-insurer FM DS 2-8 Oct-2017 / Interim Rev. Apr-2025 §2.2.1.2.2; derivation §3.1.6: Fp = 0.4·SDS·1.5·Wp·(1.3/3.5)/(1.0/1.5) = 1.077·SDS·Wp, H = 0.7·Fp → G = 0.754·SDS — checked against the data-sheet derivation]. This G already includes Ip = 1.5, so **do not multiply by Ip again**. Generic G when site SDS is not available (must be used then): FM 50-yr zone G = 1.0 (SDS 1.3g); 100-yr G = 0.7 (0.9g); 250-yr and 500-yr G = 0.4 (0.55g); use a higher G if local authorities require [§2.2.1.2.2]. FM has **no separate horizontal-capacity load-factor table** beyond this equation; Tables 3.1.8-A–F are already **maximum ASD horizontal loads** for brace members (tangent-by-angle values in their Note 1), which supports `capacity_is_horizontal:true` for FM table values.
   - Do not use the FG/IL G from DS 1-11.
   - **NFPA 13 path (2026-10-23b):** Fpw = Cp·Wp, Cp = 0.754·S_DS, Wp = 1.15 × water-filled weight [CODE NFPA 13-2025 §18.5.9.2, §18.5.9.3]. The published equation text is flattened (Cp = 0.754 SDS); confirm against the page image `[V]`. No S_DS data → Cp = 0.5 [§18.5.9.5]. Use the larger of the NFPA Fpw and the FM G route. Note FM Wp = water-filled weight tributary to the brace, **no 1.15 factor** [FM DS 2-8 §2.2.1.2.3]; NFPA adds 1.15 — the routes differ by design, take the larger, not a conflict.
   - Height reductions ×0.875 / ×0.75 [§18.5.9.3.3/.4] are **not applied** by default. That is a Design practice (×1.0), not a code limit. **Verify with the engineer of record** before you use them.
   - `calcs/fp` ops: `cp_from_sds` → `brace_spacing_max` (checks S = 20/25/30/35/40 ft against the Tables 18.5.5.2 Fpw max). Kernel `brace_load`: pass `capacity_is_horizontal:true` for FM horizontal ASD listings (already horizontal and ÷1.5) so the FM factor applies once; `false` (default) keeps the NFPA 13-2025 Table 18.5.2.3 angle-divisor path for UL/axial values (angle-divisor reading Verify with the engineer of record).
  - Worked case: SDC D, Cp 0.5655, 6 in. main @ 40 ft Fpw 1,139.37 lb > brace cap 1,060.82 lb FAIL; @ 35 ft OK; 4 in. @ 40 ft 743.97 lb OK. 35 ft is that case's calculated result / Design practice, **not** a code spacing; code max stays 40 ft [CODE NFPA 13-2025 §18.5.5.2.2]. Rerun with the job's Cp, pipe and listed brace capacity.
   - S_DS: ASCE 7-22 is not held. FEMA P-2082-1 is a labeled proxy (Verify with the engineer of record).
   - Refuse "SDS = 2.5" folklore values.
   - Risk Category can change the seismic design category at the same S_DS. See §5. The teaching pair is **RC II / SDC B**.
2. **Wp = water-filled** for every system type, including dry and DI. The design case is the tripped system [FM DS 2-8 §2.2.1.2.1, §3.1.7, Table 3.1.5]. Refuse dry-weight value engineering on dry or DI systems.
3. **Fix the standard detail before sizing members:**
   - θ 60–90° from vertical; the sheet minimum is 30°.
   - l/r ≤ 200 in tension and compression.
   - No cable braces, powder-driven fasteners or C-clamps on braces, and no aboveground CPVC in earthquake zones [FM DS 2-8 §2.2.1.3.5–.6, §2.3.1.1, §3.1.14].
   - Brace connectors are FM Approved, and their listing capacity is the submittal value.
4. **ZOI loads:** H = G · Wp [FM DS 2-8 §3.1.7].
   - Lateral braces carry their tributary main plus the branches in the span.
   - Longitudinal braces carry the main only and exclude branches.
   - A dual-duty brace within 24 in. of a direction change sums both ZOIs.
   - Show every product. Example `[SYN]`: G 0.7 × (80 ft × 23.0 lb/ft) = 1,288 lb.
5. **Capacity chain:** H ≤ min(member allowable, pipe connector, structure attachment).
   - Use the FM DS 2-8 Table 3.1.8 member allowables and Table 3.1.9 attachment allowables.
   - If the attachment governs, shorten the spacing. Show the new spacing, e.g. spacing = allowable / (G · w).
   - The SEOR signs off every point load into the primary structure.
6. **Spacing:** use the tighter of NFPA 13 and DS 2-8, per brace type.
7. **Flexibility and clearance:**
   - Use flexible couplings, or seismic separation assemblies at building seismic joints, sized to the SEOR drift. Do not put flexible couplings inside a separation assembly.
   - Use the clearance holes in §1. Where pulls are missing, mark `[V]`.
8. **Riser:** provide a 4-way brace within 2 ft of the top of each riser; avoid a manifolded brace over more than two risers [FM DS 2-8 Oct-2017/IR Apr-2025 §2.2.1.1.2.1]; intermediate 4-way braces ≤ 25 ft on risers [§2.2.1.1.2.3]; in multistory, within 2 ft of each floor [§2.2.1.1.2.2]. The NFPA 13-2025 riser section number is still not pulled → that cite stays `[V]`.
9. **Output:** a brace schedule (ID, type, location, ZOI, Wp, H, detail, capacity, governing link), a delta-vs-13-2025 column and a status register.

## 3. Verify with the engineer of record (default)

- **G from the FM generic SDS instead of the SEOR value.** Conservative assumption: use the higher of the FM generic and the code value.
- **Bracing a dry or DI system at water-filled weight.** Keep it; it is the conservative case.
- **Branch-line longitudinal bracing under §18.5.9.6**, which is not pulled. Conservative assumption: brace at 80 ft.

## 4. Handoffs

- Gas and fuel restraint goes to the DS 1-11 package.
- Material election (Sch 10 vs Sch 40) is decided outside this Skill. Re-run Wp if it changes.
- Hydraulics go to `density-area-dry-increase` and `pump-envelope`.
- Dry/DI N₂ goes to `nitrogen-inerting-and-c-factor-gate`.
- The post-earthquake water supply goes to `campus-looped-main-sizing` and `hydrant-supply-curve`.

Method sources (synthetic, method only): worked package *seismic FP bracing / fire-following — DS 2-8 hall brace schedule*; outline *wet hall, high seismic, DS 2-8*; KB `90_/seismic-bracing-and-restraint-of-sprinkler-piping`; pull 13-12.

## 5. Risk Category can flip the seismic design category

1. Take S_DS, S_D1, and the seismic design category from the USGS ASCE 7-22 design-maps service for the site latitude and longitude, the geotechnical site class (otherwise site class D, labeled ASSUMED), and the **Risk Category**. Do not invent a city to stand in for the coordinates.
2. Risk Category can change the seismic design category at the same S_DS. Worked `[SYN]`: S_DS 0.19 and site class D give **RC II / SDC B**, and RC IV gives SDC C.
3. Seismic design category C or higher, or an AHJ or FM requirement that bracing apply anyway, means the full NFPA 13-2025 Chapter 18: couplings §18.2, separation §18.3, clearance §18.4, sway bracing §18.5 (lateral 40 ft, longitudinal 80 ft, end at or under 40 ft), and restraint §18.6. Cp = 0.754 × S_DS (§18.5.9.3), so 0.754 × 0.19 = **0.143**. If S_DS is missing, Cp = 0.5 (§18.5.9.5).
4. Teaching pin: **RC II / SDC B** means Chapter 18 is not bound on that worked case. The ASCE 7 nonstructural exemption text is not held in this pack, so that exemption stays `[V]`. Verify with the engineer of record. If the owner elects RC III or RC IV, the same S_DS becomes SDC C, Chapter 18 binds, and Cp is 0.143. FM DS 2-8 still follows the DS 1-2 zone from the FM map. That map reading stays `[V]` until the zone is pinned. Wet, dry, and double-interlock only. Foam, clean agent, and single-interlock stay out of scope.
