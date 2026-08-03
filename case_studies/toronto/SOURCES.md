# Toronto case sources

## Primary public sources

1. City of Toronto Auditor General, [Audit of Software Acquisition and Licence Management: Managing and Optimizing Value from Software Licences](https://www.toronto.ca/legdocs/mmis/2024/au/bgrd/backgroundfile-251260.pdf), December 2024.
2. City of Toronto Auditor General, [2026 Consolidated Follow-up Report](https://www.toronto.ca/legdocs/mmis/2026/au/bgrd/backgroundfile-288922.pdf), June 2026.

## Evidence boundary

The files in this directory distinguish three evidence classes:

- `published_audit`: a number or event reported by the City of Toronto Auditor General.
- `derived_from_published_audit`: arithmetic calculated directly from a published number, such as the monthly cost proxy used for the M365 example.
- `illustrative_counterfactual`: an assumption created to test the tool, including hypothetical price premiums, true-down rights, review frequencies, and stochastic deployment parameters.

The optimizer does not reproduce the confidential agreements or claim that a vendor would have accepted the modelled alternatives. Its purpose is to quantify what commercial flexibility would have been worth under explicit assumptions.
