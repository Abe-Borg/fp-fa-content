# Section 21 30 00 — Fire pumps (draft)

Draft. Verify with the engineer of record before issue. A pump for wet pipe, dry pipe, or double-interlock preaction. Series pumps are out of scope. Electric drive, with or without a transfer switch, and diesel drive are in scope.

## Part 1 — General

### 1.1 Summary

Do not schedule rated flow and pressure while the supply test, the basis-of-record suction, or another gate is open. A synthetic rated pressure is not acceptable. Listed ratings are not a menu of heads.

Screen at rated flow, churn, and 150 percent of rated flow. Publish `rated gpm at rated psi` only after those gates pass. Do not copy another site's horsepower or rated pressure.

### 1.2 Driver and relief

Diesel derate is per site. Do not reuse a prior site. NFPA 20-2022/2025 §11.2.2.4: 3 percent per 1,000 ft above 300 ft. §11.2.2.5: 1 percent per 10 °F above 77 °F, including room-temperature rise (A.11.2.2.5). Prefer a continuous deduction. Adding the two is shop practice. Verify the sum with the engineer of record. §11.2.2.7: 4-hour rating must meet brake horsepower. Schedule at least that horsepower. No manufacturer or model. Do not stack the §11.2.2.2 ten percent margin. An unamended 2024 I-Code floor references NFPA 20-2022 until verified.

High-desert synthetic only: 4,500 ft, 104 °F, 140 bhp. 12.6 + 2.7 = 15.3 percent (factor 0.847). Floor = 140 / 0.847 = 165.3 hp. 150 hp fails at 127.05 hp. 175 hp passes at 148.2 hp. Do not copy it.

Diesel relief is NFPA 20-2025 §4.20.1.2, not electric §4.7.7.1. Require the valve only where 121 percent of net shutoff plus maximum static suction, adjusted for elevation, exceeds the rating. Option A: 1.21 × 125 + 40 = 191.25 psi, above 175, required (§4.20.2.1). Option B: 1.21 × 110 + 40 = 173.1, within 175 only if maximum static is at or under 41.9 psi.

Reduced-voltage starting is the draft practice at 100 hp or larger, or on a generator. Across-the-line is not the default in those cases. Label it.

## Part 2 — Products

### 2.1 Controller, setpoints, and diesel points

Specify the controller by function and listing. No catalog number. Lockout and load shed stay off.

Diesel stop [CODE NFPA 20 §12.7.3 to §12.7.6], same body in 2019, 2022, and 2025. Default is manual stop. Overspeed stops at once and locks out until manual reset. It does not use the run timer. Timed stop after automatic start is only for a test or AHJ approval, then at least 30 minutes.

Leave absolute psi blank until the shop curve and controller submittal. Order: jockey stop, jockey start, then fire-pump start below jockey start [PRACTICE]. Annex A.14.2.6(4) is advisory: jockey stop is churn plus minimum static; jockey start is at least 10 psi below that stop; fire-pump start is 5 psi below jockey start in 2019 and 2022, and 10 psi below in 2025. About 5 psi above jockey stop is the wrong pattern. On FM work, check DS 3-7 before freezing absolutes. Disable series, higher-zone, and lower-zone functions, and confirm the revision.

Publish the listing's minimum and maximum pump-room temperature. Do not invent cooling minutes after power isolation.

Diesel points, not the electric list [CODE NFPA 20-2025 §12.4]: D1 engine running, separate; D2 switch off or manual, separate supervisory; D3 controller or engine trouble, common or separate (§12.4.2.3(3); see §12.4.1.4 and §12.4.1.5); D4 fail to start, overspeed, low oil, or high temperature; D5 low fuel at two-thirds; D6 each battery failure; D7 room low temperature; D8 valve tamper; D9 low suction or low reservoir; D10 jockey run or trouble, optional. Keep D1 and D2 separate. D3 may stay one trouble until the owner elects splits. Class is Section 28 31 00.

## Part 3 — Execution

### 3.1 Acceptance

Field acceptance includes the enforced NFPA 20 start counts. Take the union with any owner overlay. Do not drop the code floor or invent a count. Provide a test header that discharges without flooding the room. An integrated test does not replace pump acceptance.
