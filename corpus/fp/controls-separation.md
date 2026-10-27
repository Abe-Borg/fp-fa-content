# Separating suppression controls from the business network

FM DS 7-110 (June 2026) §2.4.1.1 requires an industrial firewall or diode, and an industrial demilitarized zone, whenever inbound traffic, outbound traffic through a firewall, or remote access exists. Dual-homed bridges between information technology and operations technology are forbidden (§2.4.1.1). A virtual LAN is not an acceptable separation between those networks (Appendix A).

Remote access is only through a jump server in that zone. Keep the logs at least 180 days (§2.4.2.1). Every login uses multifactor authentication (§2.4.2.2).

Safety and fire-gas paths stay off remote access, segregated from the process-control network, with the run mode locked by a physical key or a password (§2.4.4.4). The building-management system and the electrical-management system are on the industrial-control asset inventory (§2.4.5.1).

Fire-alarm cybersecurity levels, when Chapter 11 applies, are `../fa/cybersecurity.md`. A gateway in front of the fire alarm control unit does not replace this separation when the suppression or gas-detection controllers are on the operations network.
