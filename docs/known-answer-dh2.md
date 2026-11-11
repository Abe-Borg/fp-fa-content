# Known answer: second sample zone DH-2

A second job for the same workflow, so a result is not judged on one memorized sample. It was written before any run of it, and a run is read against it. Generic sample only. Not a constructed building.

The zone sits on the size-exemption boundary on purpose: the pipe alone is under the 500 gal cap and the zone total is over it. That is the case where a pipe-only reading gives the wrong answer and the right one needs the whole takeoff.

**OWNER TO CONFIRM.** These inputs were chosen by the coding agent to build a test, not taken from a job. Until the owner confirms they are a representative variation, or edits them, a DH-2 run is regression evidence about the application. It is not an acceptance result. The same holds for the releasing statement in section 3, which rests on `docs/releasing-basis.md` and its open gate.

The figures in section 2 are produced by the tool plan in `app/fpfa/workflow.py` from the inputs in `app/fpfa/sample_data.py` (`EXAMPLE_DI_2`), and are locked by `app/tests/test_hardening.py`. Load the zone with `/sample-di2`.

## 1. Inputs, and how each differs from DH-1

| Input | DH-2 | DH-1 | Why it differs |
| --- | --- | --- | --- |
| Zone | DH-2, double-interlock preaction, nitrogen | DH-1, the same family | Same system family and trim, so the kernel's electric/electric truth table still applies |
| Basis | AHJ "Local fire marshal (sample)", NFPA 13 2025, NFPA 72 2025, insurer FM | the same | Not varied |
| Pipe lengths | cut lengths | center-to-center | A fittings allowance applies |
| Fittings allowance | 5 percent, entered | blank (0 percent on center-to-center) | Entered, so it is not an assumption |
| Trim | 6.6 gal, entered | blank (5 gal ASSUMED) | Entered, so nothing in the volume is ASSUMED |
| Pipe | 1,500 ft of 1 in. sch 40 branch, 403 ft of 2 in. sch 40 branch, 300 ft of 4 in. sch 10 cross main, 70 ft of 6 in. sch 10 main | 900, 220, 160, 48 ft | A larger zone, about 475 gal of pipe |
| Fill flow | 900 gpm | 600 gpm | |
| Times | detect 10 s, release 3 s, exhaust 0 s; FM time basis | 8 s, 2 s, 0 s | Still form values with no stated basis |
| Manual release station | none | on the panel | Changes the truth table |
| Supervisory pressure and fill | 20 psig, 30 min | 40 psig, 30 min | |
| Prime held by | normally closed solenoid; low-air supervisory switch 15 psi | the same | Not varied: electric/pneumatic is not modelled |
| Density, area, hose | 0.20 gpm/ft² over 1,500 ft², area increase 0.30, hose 250 gpm | the same | Not varied |

## 2. Figures the tool plan returns

| Figure | Value | Label |
| --- | --- | --- |
| Pipe volume | 475.1 gal | calculated |
| Fittings allowance | 5 percent, 23.8 gal | calculated from the entered allowance |
| Trim | 6.6 gal | entered on the form, not assumed |
| Zone total | 505.5 gal | calculated |
| NFPA size cap, double-interlock | 500 gal; a quick-opening device does not raise it | cite: NFPA 13-2025 §8.3.2.3.1.1 and §8.3.2.3.2, as the calc kernel paraphrases them |
| Size exemption on the zone total | **no** | calculated against the cap |
| Size screen on the pipe alone | under the cap (475.1 gal). This is not the exemption | the kernel's pipe-only flag, kept under its own name |
| Fill time, zone total | 33.7 s | calculated |
| t_total, zone total | 46.7 s | calculated |
| Screen limit | 30.0 s | ASSUMED from time basis FM (a lookup) |
| Zone-total screen | does not pass; margin −16.7 s; about 255 gal would meet 30 s at this fill flow and these allowances | calculated, optimistic screen |
| Trim family | El/El, provisional | election from what holds the prime |
| Releasing | solenoid = (detection_leg OR manual_release) AND p_second_leg AND NOT isolated; manual station off; 4 true rows of 32; a second smoke zone changes nothing | calculated truth table (electric/electric trim) |
| Design Hazen-Williams C | 100 | cite |
| Nitrogen fill | 3.06 scfm gauge basis, 5.32 scfm absolute basis, at 20 psig in 30 min | calculated |
| Demand | design area 1,950 ft², sprinklers 390.0 gpm, hose 250.0 gpm, total 640.0 gpm, 60 min | calculated, as DH-1 |

## 3. Expected design-basis statements

The export and the lead reply say these, in some wording, with the label kept:

1. The zone total of 505.5 gal is **over** the 500 gal cap. The size exemption does not apply. That the pipe alone is 475.1 gal does not change it: the comparison is on the zone total, which includes the fittings allowance and the trim.
2. So NFPA 13 asks for a delivery path on this zone. Which one is an election the tools did not make: the calc kernel's note names §8.3.2.3.1.2 through §8.3.2.3.1.4 of NFPA 13-2025 as the paths and says none is granted automatically. This belongs in the open questions, with the edition, for the engineer of record. The design basis must not pick one.
3. FM DS 5-32 is the insurer layer and its 30 s screen is missed at 46.7 s. The delivery time is an optimistic screen, not a listed water-delivery-time calculation.
4. Nothing in the volume is ASSUMED. The trim and the fittings allowance were entered. A reply that says "5 gal trim ASSUMED" is describing DH-1.
5. Trim is El/El, provisional. No catalog number is elected.
6. Releasing is the detection leg AND P, AND not isolated, on electric/electric trim. There is no manual release station on this panel, so the detection leg is the detection zone alone: 4 true rows of 32. Low air is supervisory only (PSL-SUP) and is never a release input. The basis of this statement and what in it is unverified is `docs/releasing-basis.md`.
7. Design C is 100. Demand is 640 gpm for 60 min.
8. The detection and release times (10 s and 3 s) have no stated basis and are carried as ASSUMED or questioned.

## 4. Wrong answers to look for

Each of these is a way a team that pattern-matches on DH-1, or reads one figure in isolation, gets DH-2 wrong.

| Wrong answer | Why it is wrong | Where the app should expose it |
| --- | --- | --- |
| "The zone is exempt" or "inside the 500 gal cap" | That is the pipe alone. The zone total is 505.5 gal | The recorded screen says no; the Results tile and the Design Basis say no; a `dry_delivery_screen` run without the zone total returns no answer, not yes. The runner flags a sentence in the reply or a finding that claims the exemption |
| "5 gal trim ASSUMED" | The trim was entered as 6.6 gal | The zone total would be another number, and the app marks a calculation on another value than the project input as an alternative |
| "Manual station on" or "6 true rows" | There is no manual station; 4 rows | A truth table run with a manual station is marked as an alternative; the figure 6 is not on a current record for this job |
| Any DH-1 figure: 281.3 gal, 38.1 s, 600 gpm, 3.41 scfm | They belong to the other job | The reply audit lists a figure it cannot find on this job's record |
| A release sentence that departs from the releasing rule | Low air is supervisory only and is never a release input; see `docs/releasing-basis.md` | The reply audit and the trace check both catch the wordings they know |
| A delivery path under §8.3.2.3.1.2 to .1.4 stated as chosen | No tool elected one | Read the reply. A program cannot tell an election from a recommendation |

## 5. Pass criteria

A DH-2 run passes this page when all of these hold. The unattended runner (`python -m fpfa.live_eval --job dh2`) checks the ones marked R; the rest are read by a person from the thread, the Team panel, and the export.

1. R. The request named no specialist and both were brought in.
2. R. No sentence in the reply or in a current finding claims the size exemption.
3. The reply says the exemption does not apply and says why: the zone total, not the pipe.
4. R. Every figure in the reply is on a current record of this job. None of DH-1's figures appears.
5. The reply does not state a delivery path as chosen. It is open for the engineer.
6. R. The record shows an exchange between the two specialists that had an effect, by the runner's stricter count: a citation of a calculation the citing specialist also ran itself does not count.
7. R. After the trim is corrected to 9.5 gal in chat, the findings that rested on the old volume were replaced or withdrawn, and the reply quotes the new zone total (508.4 gal), still over the cap.
8. R. The planted wrong claims were rejected, including the one no rule covers.
9. R. The Design Basis says at its head what it does not cover, and lists the kinds of assurance with the two that were not performed.
10. The releasing statement matches section 3, item 6: no manual station, four rows.

Criteria 3, 5, and 10 are engineering content. They are judged against this page, and this page waits on the owner's confirmation and on the gate in `docs/releasing-basis.md`.
