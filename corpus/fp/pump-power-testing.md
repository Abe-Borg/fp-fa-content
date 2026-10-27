# Fire-pump power path testing

FM DS 5-20 (October 2016 / interim October 2025) covers low-voltage equipment and transformers through 5 MVA. It is an electrical-maintenance sheet. It does not size the pump.

Infrared survey of electrical equipment, including both transfer-switch positions, is annual (§2.1.3.1.1). Table 2.1.3.1.1 calls for repair within hours when the rise exceeds 27 °F versus a similar part or 72 °F versus ambient.

Automatic transfer switches are tested and serviced every 3 to 5 years, with insulation resistance at least 100 megohms (§2.1.3.5). A diesel generator runs monthly for 30 minutes at not less than 30 percent of nameplate, and it is co-tested with the transfer switch every 3 to 5 years (§2.1.3.9.1). Controller configuration, including manual stop only, is `fire-pump-controller.md`. FM DS 2-81 Table 7 item 5 checks that manual-stop setting annually. Diesel churn on that sheet is at least 30 minutes weekly, and electric churn is at least 10 minutes monthly. Diesel fuel stays at least three-quarters full or able to run 8 hours at 100 percent load (§2.9.3.1.3).

Ground resistance of at most 1 ohm is the acceptance in §2.1.3.13.1.

A switchroom is limited to 86 °F, or 68 °F to 77 °F where electronics or valve-regulated lead-acid batteries are present (§3.6.2). Publish the controller's own minimum and maximum as well (`fire-pump-controller.md`).

A new fault and coordination study is required when a feeder or transformer is added, or when motors or generation exceed 50 hp (§2.2.2).

Backflow is tested annually above the greatest sprinkler demand, and the internals are inspected every 5 years (FM DS 2-81 Table 5). Main flushing at 10 ft/s, from Table 11 of that sheet: 880 gpm for 6 in., 1,560 gpm for 8 in., 2,440 gpm for 10 in., and 3,520 gpm for 12 in.
