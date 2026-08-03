# Guided user guide

## What the planner answers

The planner is designed for procurement, software asset management, finance, IT, and
project-delivery users who need a practical pre-award answer:

> How many licence units should we commit at contract start, how should later purchases
> be phased, and what flexibility is worth paying for?

It returns:

1. an initial committed quantity;
2. a formal usage-review cadence;
3. an expected phase-by-phase procurement schedule;
4. a quantity rule based on measured active usage and a buffer;
5. a maximum modelled price premium for flexibility;
6. a comparison with full upfront commitment;
7. supplier terms to request and actions required before award; and
8. a downloadable Markdown procurement plan and JSON model record.

## The seven required inputs

| Input | Plain-language meaning | Suggested owner or source |
|---|---|---|
| Software or project name | Label used in the downloaded plan | Procurement or project lead |
| Total licences after rollout | Maximum credible steady-state licence requirement | HR, IAM, device inventory, application owner, demand forecast |
| Day-one licences | Units able to use the software when the contract starts | Deployment wave 1 or go-live plan |
| Full-commitment unit price | Supplier price if the full planned quantity is committed now | Quote, reseller response, catalogue, incumbent renewal |
| Contract term | Number of months covered by the commercial decision | Draft order form or sourcing strategy |
| Rollout completion month | Month when the intended population should be substantially live | Approved implementation plan |
| Rollout confidence and planning posture | Degree of schedule uncertainty and desired cost/risk balance | Joint business, IT, finance, security, and procurement assessment |

The price may be entered per month or per year. The planner converts annual pricing into
a monthly unit price before running the commercial engine.

## Optional assumptions

The first run can use the documented defaults. Once supplier pricing is available,
replace:

- the overage price uplift;
- the price premium for monthly, quarterly, semiannual, or annual adjustment rights;
- the additional price premium for true-down rights; and
- the number of planning scenarios.

These values are commercial assumptions, not market benchmarks. The selected review
cadence can change when the supplier prices flexibility differently.

## How to use the procurement schedule

The schedule shows the expected active population and committed quantity at each review.
It is a planning calendar, not an instruction to place every future order automatically.

At each review:

1. obtain measured active usage;
2. reconcile leavers, reassignment rights, dormant accounts, devices, cores, or the
   applicable licence metric;
3. apply the recommended operating buffer;
4. compare the result with the contractual floor and prior commitment;
5. issue the permitted true-up or true-down; and
6. retain the usage evidence with the purchase-order record.

## How to use the price ceiling

The maximum flexibility premium is the point at which the recommended phased structure
and full upfront commitment have the same modelled risk-adjusted cost. Use it as a
negotiation boundary:

- below the boundary, the model still supports paying for flexibility;
- above the boundary, the full-commitment structure prices better under the entered
  assumptions; and
- the boundary is not a forecast of what the supplier will quote or proof that the term
  is obtainable.

## Recommended sourcing workflow

1. Run an internal planning version before releasing the sourcing event.
2. Ask bidders to price both full commitment and the recommended phased structure.
3. Replace the optional premium assumptions with each compliant bid.
4. Compare the resulting schedules, expected costs, P90 budgets, and unused spend.
5. Use the downloadable procurement plan as an input to the negotiation memo.
6. Translate the selected quantity rule, dates, floor, pricing, notice, evidence, and
   remedy into the order form or statement of work.
7. Assign an operational owner for each post-award usage review.

## Guardrails

The planner does not validate the licence metric, bundle entitlements, technical
architecture, supplier willingness, legal enforceability, tax, foreign exchange, or
confidential discount approvals. A generated plan must be reviewed by the relevant
commercial, finance, delivery, software-asset, security, architecture, and legal owners.
