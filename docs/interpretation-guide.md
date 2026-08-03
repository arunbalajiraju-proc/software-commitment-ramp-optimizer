# Interpretation guide

## Start with the decision, not the rank

The first-ranked policy is the lowest value of the configured objective among feasible
candidates. It is not automatically the best contract. Before using it in a negotiation,
ask whether each right is contractible, operationally manageable, and acceptable to the
supplier.

## Read the metrics together

| Metric | Use it to ask | Common misread |
|---|---|---|
| Expected cost | What is the average outcome under these probabilities? | Treating the mean as a budget guarantee |
| P90 cost | What budget covers 90% of simulated paths? | Calling P90 the worst case |
| CVaR | How expensive are the costliest 10% of paths on average? | Confusing it with probability of loss |
| Risk-adjusted cost | How does the chosen tail-risk preference change ranking? | Treating its weighting as objective truth |
| Unused cost | How much paid capacity is idle in the model? | Assuming every idle unit has zero strategic value |
| Overage cost/share | How much does the policy rely on exception purchasing? | Ignoring compliance and administrative burden |
| Utilization | How closely does paid capacity track active demand? | Assuming 100% utilization is always operationally safe |
| Break-even premium | What price room exists for flexibility? | Treating it as a supplier's likely quote |

## Procurement decision sequence

1. Validate public or internal baseline quantities and cash flows.
2. Replace proxy pricing with actual supplier bid sheets.
3. Build demand scenarios with delivery, architecture, security, finance, and business
   owners—not procurement alone.
4. Express each proposed right precisely: effective date, measurement rule, notice period,
   floor, price, remedy, and audit evidence.
5. Set risk appetite and overage limits before viewing the optimizer's rank.
6. Run sensitivities for delay, demand, price premiums, floors, and escalation.
7. Use the break-even boundary to form a negotiation target and walk-away condition.
8. Document qualitative benefits and constraints that are outside the numerical model.

## Interpreting the Toronto run

The optimized Toronto policy is a useful hypothesis because it limits the initial floor
and aligns later commitments with observed activation. It also carries overage exposure,
which is why the 10% guardrail matters. A sourcing team should not simply request “more
flexibility.” It should ask for a measurable activation schedule, defined review dates,
price protection, and evidence rules that make the structure operable.

The 78.4% break-even premium is intentionally a boundary. It says that, under this demand
model and objective, there is substantial room to pay for flexibility. It does not say a
78.4% premium is fair, customary, or recommended.

