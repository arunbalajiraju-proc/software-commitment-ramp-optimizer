# Assumptions and limitations

## Evidence limitations

- Public audits do not disclose every commercial concession, bundle benefit, price tier,
  deployment forecast, or negotiation constraint available at signature.
- The CAD 14.28 unit-month figure is an allocation proxy, not a disclosed SKU price.
- “30,000 subscription licences” combines enterprise licences and add-ons as presented in
  the audit; it is not treated as 30,000 distinct users.
- The experiment does not claim the City could have procured the hypothetical rights.

## Forecast limitations

- Adoption follows a smooth, monotonic logistic curve. Real programs can pause, reverse,
  migrate between products, or add cohorts discontinuously.
- Scenario probabilities are illustrative and are not calibrated from Toronto project
  history.
- Normal multipliers and a triangular delay distribution are chosen for transparency,
  not asserted as the true data-generating process.
- Demand paths do not model correlated macroeconomic, organizational, or supplier events.

## Commercial limitations

- The engine models licence-equivalent units; bundles with heterogeneous feature value
  need SKU-level or value-weighted extensions.
- Overage is billed monthly at a multiplier. Actual agreements may apply retroactive
  true-up, audit penalties, minimum order sizes, anniversary proration, or no lawful
  overage mechanism at all.
- Taxes, foreign exchange, financing, payment timing, accounting treatment, and cost of
  capital are not included.
- One-time and fixed fees are supported, but implementation and internal operating costs
  are not part of the Toronto scenario.
- Supplier capacity, competition, negotiation leverage, and approval governance are
  outside the optimizer.

## Decision limitations

- Lower modelled cost does not establish legal feasibility or service continuity.
- Unused capacity can carry option value, disaster-recovery value, or bundle benefits not
  captured in utilization.
- A seeded Monte Carlo run is reproducible but not necessarily accurate.
- Risk-adjusted cost depends on the guided risk posture or programmatic risk weight and
  CVaR confidence level.
- The overage guardrail is a policy choice and should be tailored to compliance needs.

The tool is decision support for professional review. It is not legal, accounting,
financial, or procurement advice and does not certify contract compliance.
