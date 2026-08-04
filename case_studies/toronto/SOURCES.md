# Toronto case sources

## Primary public sources

1. City of Toronto Auditor General, [Audit of Software Acquisition and Licence Management: Managing and Optimizing Value from Software Licences](https://www.toronto.ca/legdocs/mmis/2024/au/bgrd/backgroundfile-251260.pdf), December 2024.
2. City of Toronto Auditor General, [2026 Consolidated Follow-up Report](https://www.toronto.ca/legdocs/mmis/2026/au/bgrd/backgroundfile-288922.pdf), June 2026.

Key 2024 audit references used by the application:

- report page 8: known network-capacity constraint, 10,000-user initial commitment,
  annual and five-year cost, claimed bulk-discount savings, and deployment outcome;
- report page 9: Year 1 and first-nine-months-of-Year-2 spend, utilization, and unused cost;
- report page 11: recommendations to defer or adjust licence volumes when projects or
  requirements change; and
- management response pages 29–30: commitment to balance bulk savings against unused-
  licence risk and pursue better future contract terms.

## Evidence boundary

The files in this directory distinguish three evidence classes:

- `published_audit`: a number or event reported by the City of Toronto Auditor General.
- `derived_from_published_audit`: arithmetic calculated directly from a published number, such as the monthly cost proxy used for the M365 example.
- `illustrative_counterfactual`: an assumption created to test the tool, including hypothetical price premiums, true-down rights, review frequencies, and stochastic deployment parameters.

The optimizer does not reproduce the confidential agreements or claim that a vendor would have accepted the modelled alternatives. Its purpose is to quantify what commercial flexibility would have been worth under explicit assumptions.
