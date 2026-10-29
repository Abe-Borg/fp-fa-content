# Section 21 30 00 — Fire pumps (draft)

Draft language. Verify with the engineer of record before issue. This section is a pump serving wet pipe, dry pipe, or double-interlock preaction. Series pumps are out of scope. Electric drive, with or without a transfer switch, and diesel drive are both in scope.

## Part 1 — General

### 1.1 Summary

Do not schedule a rated flow and pressure while the supply test, the basis-of-record suction, or another gating question is still open. A synthetic rated pressure written into an equipment schedule is not acceptable. Listed pressure ratings are not a menu of screening heads.

Screen the pump at rated flow, at churn, and at 150 percent of rated flow against the demand and the suction condition. Publish `rated gpm at rated psi` only after those gates pass. Do not copy another site's horsepower or rated pressure.

### 1.2 Driver and relief

Diesel derate is per site. Do not reuse a prior site. NFPA 20-2022/2025 §11.2.2.4 is 3 percent per 1,000 ft above 300 ft. §11.2.2.5 is 1 percent per 10 °F above 77 °F. Include room-temperature rise (A.11.2.2.5). Prefer a continuous deduction. Adding the two deductions is shop practice. Verify the sum with the engineer of record. §11.2.2.7 then requires the 4-hour rating to meet brake horsepower. Schedule at least that computed horsepower, 4-hour, after the derate. Do not name a manufacturer or a model. Do not stack the §11.2.2.2 ten percent listing margin. An unamended 2024 I-Code floor references NFPA 20-2022 until adoption is verified.

High-desert synthetic only: 4,500 ft, 104 °F, 140 bhp. 12.6 percent + 2.7 percent = 15.3 percent (factor 0.847). Floor = 140 / 0.847 = 165.3 hp. 150 hp derates to 127.05 hp and fails. 175 hp derates to 148.2 hp and passes. Whole-step rounding is about 162.8 hp. Do not copy the number.

Diesel relief is NFPA 20-2025 §4.20.1.2, not electric §4.7.7.1. Require a main relief valve only where 121 percent of net shutoff plus maximum static suction, adjusted for elevation, exceeds the rating. Overspeed makes pressure scale about with speed squared (about 1.21 at 110 percent). Option A: 1.21 × 125 + 40 = 191.25 psi, above 175, so the valve is required (§4.20.2.1). Option B: 1.21 × 110 + 40 = 173.1, within 175 only if maximum static is at or under 41.9 psi. Do not skip the check because a prior schedule had no valve.

Reduced-voltage starting is the draft practice where the motor is 100 hp or larger, or where the pump is on a generator. Across-the-line is not the default in those two cases. Label the choice.

## Part 2 — Products

### 2.1 Controller

Specify the controller by function and listing. Do not elect a catalog number. State on the submittal that lockout, load shed, and automatic stop are off. Those functions defeat a fire pump.

On FM work, disable series, higher-zone, and lower-zone functions and say so on the submittal. Confirm the FM DS 3-7 revision in hand.

Publish both the minimum and the maximum pump-room temperature the controller listing allows. Do not invent a cooling-continuation time after power isolation. If a minute count is required and none is held, mark it unverified.

Map each required remote signal to a named terminal. Controller-side cites: NFPA 20 §10.4.7 (electric), §12.4.2 (diesel), and §4.18. The fire-alarm class and the module count are specified in Section 28 31 00. One common diesel trouble point is the draft practice unless the owner, the insurer, or the authority having jurisdiction asks for the discrete points.

## Part 3 — Execution

### 3.1 Acceptance

Field acceptance includes the enforced NFPA 20 start counts. An owner overlay can require more starts. Take the union. Do not drop the code floor because an overlay was silent, and do not invent a start count.

Provide a test header and a discharge path that can be used without flooding the room. Commissioning of the pump with the sprinkler and alarm systems is an integrated test. It is not a substitute for the pump field-acceptance test.
