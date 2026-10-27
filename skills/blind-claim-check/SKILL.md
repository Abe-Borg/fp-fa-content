---
name: blind-claim-check
description: >-
 Use when a spec section is drafted and its code claims must be checked by
 someone who does not see the draft or the reasoning behind it.
---
# Blind claim check

A checker who reads the draft tends to agree with its mistakes. The QA checker sees only the claim list and a short cite for each claim.

## 1. Designer: claim list

Next to the section, save `<section>-claims.md`. Each line is one claim:

```
1. NFPA 72-2025 §18.4.3 requires <one atomic requirement>.
2. IBC 2021 §903.2 requires <one atomic requirement>.
```

One claim per line. A claim that names a section carries the edition and the section. A figure with no section says so. No reasoning. No spec sentences.

## 2. Designer: short cites

For each claim, record a matching note in `<section>-sources.md`, numbered the same way. Each note is the edition, the section, and a short cite. If the passage is longer than a sentence or two, paraphrase it and keep the section number. Do not paste a long quotation. This step does not judge the claim. Where the text cannot be retrieved, write `NOT PULLED`.

Take each claim from a sentence in the draft that will be exported. Keep a sentence that states a figure and names no section. Keep a sentence that names a section even when a tool already named that section. Do not replace the draft sentence with a tool string.

A tool string may be written as a package assertion. That is not a passage retrieved from the standard, and it is not `NOT PULLED`. Do not copy the claim's own words into the cite. Supported on a package assertion means the assertion states the figures in the claim. It does not mean the standard was opened. Engineer-of-record review still applies. A cite the tools did not emit stays `NOT PULLED`.

## 3. QA checker: blind verdict

The QA checker receives only the claims file and the cites file. The checker does not receive the spec, the draft, or the designer's notes. For each claim, write `<section>-claimcheck.md`:

```
<n>. Supported | Not supported | Source not found. Cite: "<short source line>"
```

## 4. Close

The designer corrects every claim that is not Supported, then repeats steps 2 and 3 on the changed claims only. The section is done only when every claim is Supported. A source that was not retrieved stays open. Do not treat it as supported. Supported on a package assertion is not a check against the standard. Engineer-of-record review still applies.
