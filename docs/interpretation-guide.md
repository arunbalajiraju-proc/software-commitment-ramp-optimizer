# Interpretation guide

## Start with the decision, not the rank

The guided interface presents the buying decision in procurement language:

- whether the evidence supports any large commitment;
- blockers, conditions, owners, and missing decision-record fields;
- the initial quantity to commit;
- the usage-review cadence;
- the expected phased order schedule;
- the maximum modelled unit-price premium for flexibility;
- the supplier terms to request; and
- the actions required before issuing the purchase order.

The readiness decision takes precedence over the numerical rank. If it says **Hold full
commitment**, the modelled initial quantity is a conditional planning output, not an
approved PO quantity.

The first-ranked policy is the lowest value of the configured objective among feasible
candidates. The first-ranked supplier offer is likewise only the lowest financial result
among the offers entered. Neither is automatically the award recommendation. Confirm
mandatory compliance and whether every right is contractible and operationally manageable.

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

1. Define one consistent licence metric and reconcile day-one and steady-state demand.
2. Complete the readiness gate with delivery, architecture, security/privacy, finance,
   change, and business owners—not procurement alone.
3. If the gate holds the commitment, close the blockers or document an authorized exception.
4. Download the supplier-pricing request and obtain comparable full and phased offers.
5. Enter actual compliant terms in the offer comparison and review TCO, P90, unused
   exposure, utilization, and risk-adjusted difference.
6. Express each right precisely: effective date, measurement rule, notice, floor, price,
   remedy, and evidence.
7. Use the break-even boundary to form a negotiation target and walk-away condition.
8. Put activation, usage reporting, adjustment, reassignment, and delay mechanics into
   the order form.
9. Record cross-functional approval and qualitative value outside the numerical model.
10. Run the usage review monthly and before every true-up, renewal, or additional PO.

## Interpreting the Toronto run

The optimized Toronto policy is a useful hypothesis because it limits the initial floor
and aligns later commitments with observed activation. It also carries overage exposure,
which is why the 10% guardrail matters. A sourcing team should not simply request “more
flexibility.” It should ask for a measurable activation schedule, defined review dates,
price protection, and evidence rules that make the structure operable.

The 78.4% break-even premium is intentionally a boundary. It says that, under this demand
model and objective, there is substantial room to pay for flexibility. It does not say a
78.4% premium is fair, customary, or recommended.

The separate retrospective premium slider uses the audit's examined spend and reported
unused cost. It asks what a usage-aligned billing proxy would have cost after applying an
illustrative flexibility premium. Because it uses observed outcomes, it is an upper-bound
counterfactual and must not be described as forecast, recoverable cost, or realized savings.
