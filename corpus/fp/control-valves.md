# Control valves

A control valve must not be able to close in less than 5 seconds at maximum operating speed. The source note flags that limit for verification against NFPA 13-2025 before a submittal cites it. Treat the 5 seconds as `[V]` until that paragraph is confirmed.

A butterfly valve costs more friction than a gate. FM DS 3-0 Appendix C Table 12, 4 in. pipe at C = 120, assigns 2 ft equivalent length to a fully open gate and 12 ft to a butterfly. At 4 in. Schedule 40 and C = 120, one butterfly-for-gate swap is about 0.72 psi at 500 gpm and about 1.52 psi at 750 gpm. Those psi figures illustrate the table. Company dry and double-interlock calculations still use C = 100 (`nitrogen-compressor-and-c-factor.md`). Do not run the friction comparison at C = 120 and then size the system at C = 120.

NFPA 20-2019 through 2025 §4.16.5.1 and §4.16.5.4 require a listed outside-stem-and-yoke gate in the pump suction and no other control valve within 50 ft of the suction flange. FM DS 3-7 §3.1.3.1 allows no butterfly valve anywhere in the suction piping, which is stricter than the 50 ft limit. One carrier sheet also prohibits a butterfly within 50 ft of the pump flange and prohibits motorized valves in fire-protection piping. Another carrier preference for post-indicator valves at 40 ft from a wall is that sheet's siting rule. Confirm it before you move a valve to satisfy it.

The common listing plateau is 175 psi for heads, control valves, checks, and backflow preventers. Many valves are listed at 300 psi. A higher working pressure requalifies every device class. It is not inherited from the valve alone. NFPA 14-2024 §10.2.4.2 calls for pressure control where static pressure exceeds 175 psi. Pressure-reducing valves on a dedicated fire main are a separate question. A federal criterion bans them on dedicated fire piping and rates the pipe for the full static pressure. That ban is not the unamended I-Code pin (`ufc-outside-pin.md`). Where a pressure-reducing valve is actually in a wet basis of design, the NFPA 13 section is the one in `itm-testability.md`.

FM DS 2-81 scopes a monthly physical valve test by type, including non-FM-Approved indicating butterflies. An FM Approved indicating butterfly can leave that monthly population. Read the approval before you drop the test.

Supervision methods and the two-turn threshold are `waterflow-supervision.md`.
