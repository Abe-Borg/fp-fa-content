# Nitrogen, compressor, and C-factor

Use this only after dry pipe or double-interlock is the elected family. Wet pipe is not this gate. Nitrogen is a corrosion and reliability decision. It is not a hydraulic credit.

## C-factor

Design practice for company dry and double-interlock pipe: calculate at C = 100. Do not chase C = 120.

C = 120 may be printed only as comparison-only. FM DS 2-0 has a dry/preaction black-steel plus inert-gas value of 120. Using 120 instead of 100 understates friction. FM DS 3-0 equation 15: (100/120)^1.85 is about 0.714, roughly a 29 percent understatement. Show that line when someone asks for the credit. Do not put C = 120 on the calc that sizes the system.

## Two numbers, not one

1. Maintenance capacity covers the sum of the connected system gallons.
2. The 30-minute compressor or bypass fill is sized on the largest single system, not on the campus total.

Restore-time floor: NFPA 13-2025 §8.2.7.3; NFPA 13-2019 and 2022 §8.2.6.3.2 (30 minutes). `calcs/fp` op `air_fill_scfm` reports a gauge-basis rate and an absolute-basis rate. Size on the absolute basis, which is higher at a typical supervisory pressure (about 37 percent higher at 40 psig). A listed compressor table governs when it is in hand. Verify the basis with the engineer of record.

The generator family is a design-practice setting, confirmed at submittal by duty and listing. Do not freeze a model number from a prior hall. Liquid nitrogen is not the company default. Tank gallons on a feed-air package are not system gallons.

## Sampling and the trip-test lever

Remote purge plus branch-end sampling decide whether the pipe is actually inerted. A high reading at a purge port does not prove the branch ends.

FM DS 2-81 can move a full-flow trip test from every 3 years to every 10 years, and can exempt black-steel obstruction investigation, when the system was originally installed with nitrogen and FM grants the lever on company-elected dry or double-interlock. That is a construction-document decision. It is not a later conversion, and it is not available on a single-interlock basis of design. The interval schedule itself belongs to `itm-design-for-testability`.

Minimum supervisory pressure for the preaction system is a separate trim question. See `preaction-trim-and-sequence.md`. Do not treat fill time as water-delivery time.
