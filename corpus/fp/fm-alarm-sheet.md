# FM DS 5-40 is an old alarm sheet

FM DS 5-40 is the September 2007 data sheet. Its peer alarm code is NFPA 72-2006. A November 2024 file date is not a new edition. Reconcile every figure to the enforced NFPA 72 and to FM DS 5-32 (January 2026) before it reaches a construction document.

Do not take detector layout, early-warning tiers, or pathway survivability from this sheet. Detection installation is FM DS 5-48 (`fm-detection-install.md`). Hall detection performance is DS 5-32 (`../fa/detection-layout.md`).

Keep these panel rules only as insurer figures, and say the sheet date:

- Releasing standby in §2.3.4 is 90 hours plus 10 minutes. The code floor remains the shorter NFPA 72 duration (`../fa/secondary-power.md`). The printed Appendix C example that divides by 5 minutes is the wrong alarm term for a releasing panel. Use the 10 minute term in §2.3.4.
- Water-valve activation circuits, including signaling line circuits, are Class A. Those circuits prohibit cross-zoning and alarm verification (§2.2.11). An open or a ground on the releasing circuit is a trouble signal. That Class A rule supports the pathway default in `../fa/pathway-class.md`. The no-cross-zone rule matches DS 5-32 §2.4.3.2.1.3.
- Disconnect the release wiring physically before a functional test (§2.4.3). A software disable is not the impairment control.
- Table 1 acceptance: trouble within 200 seconds, waterflow within 60 seconds, alarm function within 10 seconds, off-premises transmission within 90 seconds. The 60 second waterflow time is alarm receipt. It is not a 90 second device retard (`waterflow-supervision.md`).
- Secondary power transfers within 10 seconds with no signal loss (§2.3.3).
- Batteries recharge to full within 48 hours after the required standby. The battery overcurrent device is 150 to 250 percent of maximum battery load (Appendix C.6).
- Table 3 charger factors: 0.80 at 131 °F and 0.90 at 5,000 ft.
- One municipal transmitter covers at most 100,000 ft² (§2.2.10).
- After a software change, retest 100 percent of affected devices plus 10 percent of initiating devices, and cap that sample at 50 (§2.2.7).
- Central-station response to the premises is within 1 hour, and repair starts within 4 hours (Appendix C.9 and §2.4.2). That hour is tighter than the NFPA 72 central-station supervisory dispatch of 2 hours. Keep the stricter one when this sheet is still a condition of coverage.

If a newer FM alarm sheet replaces September 2007, retire these figures. Do not average them with NFPA 72-2025.
