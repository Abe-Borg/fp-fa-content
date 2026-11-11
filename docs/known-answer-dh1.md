# Known answer: sample zone DH-1

The oracle for the v0 task "Give me the design basis for zone DH-1." The lead reply and the Design Basis and Open Questions export are judged against this page. Generic sample only. Not a constructed building.

The figures in section 2 are produced by the tool plan in `app/fpfa/workflow.py` from the inputs in `app/fpfa/sample_data.py`, and are locked by tests. Everything after section 2 is the expected design-basis content. Items marked OWNER TO CONFIRM need the project owner's yes or edit before Phase 2 uses this page as the gate.

## 1. Inputs

| Input | Value |
| --- | --- |
| Zone | DH-1, double-interlock preaction, nitrogen supervisory medium |
| Basis | AHJ "Local fire marshal (sample)", NFPA 13 2025, NFPA 72 2025, insurer FM |
| Hazard | Ordinary-hazard analogue, waterflow supervised |
| Density and area | 0.20 gpm/ft² over 1,500 ft², area increase 0.30 |
| Hose | 250 gpm designer value |
| Fill flow | 600 gpm |
| Times | detect 8 s, release 2 s, exhaust 0 s; FM time basis |
| Trim | blank on the form |
| Prime held by | normally closed solenoid; not failsafe on total power loss; low-air supervisory switch 15 psi |
| Supervisory pressure and fill | 40 psig, 30 min |
| Pipe, center-to-center lengths | 900 ft of 1 in. sch 40 branch (ID 1.049), 220 ft of 2 in. sch 40 branch (ID 2.067), 160 ft of 4 in. sch 10 cross main (ID 4.260), 48 ft of 6 in. sch 10 main (ID 6.357) |

## 2. Figures the tool plan returns

| Figure | Value | Label |
| --- | --- | --- |
| Pipe volume | 276.3 gal | calculated |
| Fittings allowance | 0 percent, 0.0 gal (center-to-center lengths) | calculated |
| Trim | 5.0 gal | ASSUMED (blank trim, no valve data sheet) |
| Zone total | 281.3 gal | calculated |
| NFPA size cap, double-interlock | 500 gal; quick-opening device does not raise it | cite: NFPA 13-2025 §8.3.2.3.1.1 and §8.3.2.3.2 |
| Size exemption on the zone total | yes | calculated against the cap |
| Fill time, zone total | 28.1 s | calculated |
| t_total, zone total | 38.1 s | calculated |
| Screen limit | 30.0 s | ASSUMED from time basis FM (a lookup) |
| Zone-total screen | does not pass; margin −8.1 s; about 200 gal would meet 30 s at this fill flow and these allowances | calculated, optimistic screen |
| Trim family | El/El, provisional | election from what holds the prime |
| Releasing | solenoid = (detection_leg OR manual_release) AND p_second_leg AND NOT isolated; p_second_leg is P, the pressure drop from sprinkler operation; low air is supervisory only and is not in the Boolean; manual station on; 6 true rows of 32; a second smoke zone changes nothing | calculated truth table (electric/electric trim) |
| Design Hazen-Williams C | 100; C 120 is comparison only and multiplies friction by about 0.714 | cite |
| Nitrogen fill | 3.41 scfm gauge basis, 4.67 scfm absolute basis, at 40 psig in 30 min | calculated |
| Design area | 1,950 ft² | calculated |
| Sprinkler demand | 390.0 gpm | calculated |
| Hose | 250.0 gpm designer value; table combined hose 250 gpm | calculated |
| Total demand | 640.0 gpm | calculated |
| Duration | 60 min, table range 60 to 90 | cite: NFPA 13-2025 Table 19.2.3.1.2 and §19.2.3.1.3 |
| Duration volume | 38,400 gal including hose | calculated |

## 3. Expected design-basis statements

The export and the lead reply say these, in some wording, with the label kept:

1. Basis of design is double-interlock preaction, elected. NFPA 13-2025 is the delta baseline. An unamended 2024 I-Code adoption enforces NFPA 13-2022 until the adoption is verified; the sample's 2025 pin is the delta, not a confirmed enforced edition. OWNER TO CONFIRM: whether the sample should carry a stated enforced edition or leave it open as an RFI.
2. FM DS 5-32 is the insurer layer. Its 30 s criterion runs to design pressure at the single most remote sprinkler. It is not the NFPA floor. First water at the inspector's test connection is not that endpoint.
3. The zone total of 281.3 gal is inside the 500 gal NFPA cap, so no specific delivery time is required by NFPA 13 §8.3.2.3.1.1. The FM 30 s insurer screen still misses at 38.1 s. The cap does not close the insurer screen.
4. The delivery time is an optimistic screen from trapped volume and an assumed fill flow. It is not a listed water-delivery-time calculation. A listed calculation or a witnessed test is needed to claim 30 s.
5. Trim is El/El, provisional. A normally closed solenoid holds the prime. The 15 psi low-air supervisory setting is an electric/electric nominal, not a pneumatic-actuator band. No catalog number is elected.
6. Releasing is the detection leg (one detection zone, or a manual station in its place) AND P, AND not isolated. P is the pressure drop from sprinkler operation: on this electric/electric trim, a separate pressure contact (PSL-REL) that the panel ANDs with the detection leg. Low air is supervisory only (PSL-SUP) and is never a release input. A manual release station still needs P. The basis of this statement, and what in it still needs a qualified engineer, is `docs/releasing-basis.md`. No cross-zone on an FM job. FM DS 5-32 ranks double-interlock late; the conflict is flagged to the owner and the insurer and the basis stays double-interlock.
7. Design C is 100 on the nitrogen-supervised pipe. Nitrogen is a corrosion decision, not a hydraulic credit.
8. Demand is 390 gpm sprinklers plus 250 gpm hose, 640 gpm total, 60 min, on the 30 percent dry and double-interlock area increase applied to the code-floor area and not stacked on an insurer absolute area.
9. Hazard notes and any sentence the tools did not return are labeled use best judgment.

## 4. Expected open questions and RFIs

OWNER TO CONFIRM the list. Draft:

1. Trim volume from the elected valve's data sheet, to replace the 5 gal assumption.
2. Fill flow basis: the 600 gpm is a form input. Confirm against the supply curve at low back-pressure.
3. Delivery-time proof method: named listed calculation program, or witnessed remote-end test. Until named, the 30 s claim stays open.
4. Enforced NFPA 13 and NFPA 72 editions for the authority having jurisdiction.
5. Owner standard: any layer stricter than code or FM on area, hose, duration, or zone size.
6. Exhaust time allowance (0 s on the form) and whether an accelerator or exhauster is elected.
7. Zone split: whether DH-1 is split or a higher fill flow is available, given the 30 s miss at 281 gal.
8. FM double-interlock ranking conflict, to the owner and the insurer.

## 5. Expected ASSUMED list

Trim 5 gal. Screen limit 30 s from the FM time basis. Any schedule the shop default filled in (none on this sample; every segment names its schedule).

## 6. What the trace check must find

The check is a trace check. It asks whether each finding is consistent with the rows it cites. It does not open a standard, and nothing in the app says it does.

Every claim with a number traces to a calc record, a content-pack note the app looked up, or a project input. A figure in a claim that is not in the rows it cites makes the claim Not supported, whatever the checker said. No claim is Supported on a note that only repeats the claim. A cite to a section the content pack does not hold rests on its author's note alone and is reported that way. A finding whose basis changed is not judged; it is out of date.

The Design Basis export waits for a trace check that judged the findings as they are now, and for nothing on the record to be out of date. It does not wait for every finding to be Supported: a finding that is not supported, has no source, or is objected to is printed under "Needs further evidence or engineering review", where the engineer of record can see it. The Section 21 13 19 export keeps its own stricter gate: every claim Supported.

## 7. What the record must show about the team's work

The request is a plain objective. It names no specialist and no sequence. The evidence below is read from the Team panel, `/status`, and the export. Two role names on a roster are not evidence. A handoff row with nothing in it is not evidence. Two specialists run one after the other, neither reading the other's rows, is not evidence.

1. **A plan the lead set.** An objective and steps with owners, before the first delegation.
2. **Both contributions.** A sprinkler contribution covering items 1 through 5, 7, and 8 of section 3. A releasing contribution covering item 6 and the supervisory points that follow from it. Each finding names the calc records, cites, or inputs it rests on.
3. **The dependency, carried by the record.** The releasing sequence depends on the trim family and the supervisory pressures the sprinkler specialist owns. The delivery screen depends on a detection time and a release time that describe the releasing specialist's devices. The record shows each fact reaching the other specialist: a finding or calc record the other one cites or reviews, or a consult with its question and its answer.
4. **A position on the other's work.** At least one review of a finding by the specialist who did not write it: agree, or object with the reason. The two times in the delivery screen (8 s and 2 s on the sample) are the natural case. They are form inputs with no stated basis, so an objection or an ASSUMED note on them is a correct outcome, not a failure.
5. **Every disagreement has an end.** An objection is closed by the author's revision, settled by the lead with a recorded decision, or escalated as a question to the designer or the engineer of record. None is left open without a word in the lead's reply.
6. **A trace check** with a verdict per finding, and the tier each finding earned.
7. **The lead's reply quotes only what is on the record.** The governing zone total and t_total texts come from current calc records. The app lists under the reply any figure it could not find on one.

## 8. What a live run may add, and how to read it

The sample is generic and some of its inputs are loose on purpose. A live specialist may raise points this page does not list. Read each against the content pack before calling it wrong.

- The sample carries a 40 psig supervisory fill pressure beside a 15 psi low-air supervisory setting. The trim skill teaches supervisory bands per valve family, and a specialist may object that 40 psig sits outside the band for an electric/electric trim. That is a fair catch against the sample's inputs. It belongs in the open questions.
- The detection and release times (8 s and 2 s) have no stated basis. Expect them to be carried as ASSUMED or questioned.
- A specialist may run an alternative (another fill flow, a split zone). The app marks a calc that left the project inputs as an alternative. The reply must not present it as the design case.

A run that produces every figure in section 2 and none of the evidence in section 7 did the arithmetic and not the teamwork. Score it that way.
