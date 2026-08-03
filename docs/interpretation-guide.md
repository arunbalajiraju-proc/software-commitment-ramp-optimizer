# Interpretation guide

## Start with the decision, not the rank

The guided interface presents the buying decision in procurement language:

- the initial quantity to commit;
- the usage-review cadence;
- the expected phased order schedule;
- the maximum modelled unit-price premium for flexibility;
- the supplier terms to request; and
- the actions required before issuing the purchase order.

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

1. Confirm the eventual licence requirement and the population that can use the software
   on day one.
2. Obtain a comparable unit price for committing the full quantity at contract start.
3. Validate rollout completion and confidence with delivery, architecture, security,
   finance, change, and business owners—not procurement alone.
4. Run the guided plan and use its initial quantity and review cadence as the first
   commercial position.
5. Ask bidders to price that phased structure, then replace the optional premium
   assumptions and rerun it.
6. Express each proposed right precisely: effective date, measurement rule, notice period,
   floor, price, remedy, and audit evidence.
7. Use the break-even boundary to form a negotiation target and walk-away condition.
8. Put the activation schedule and usage-review mechanics into the order form.
9. Document qualitative benefits and constraints that are outside the numerical model.

## Interpreting the Toronto run

The optimized Toronto policy is a useful hypothesis because it limits the initial floor
and aligns later commitments with observed activation. It also carries overage exposure,
which is why the 10% guardrail matters. A sourcing team should not simply request “more
flexibility.” It should ask for a measurable activation schedule, defined review dates,
price protection, and evidence rules that make the structure operable.

The 78.4% break-even premium is intentionally a boundary. It says that, under this demand
model and objective, there is substantial room to pay for flexibility. It does not say a
78.4% premium is fair, customary, or recommended.
