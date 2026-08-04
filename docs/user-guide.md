# Operating guide

## What the workflow answers

The application is designed for procurement, software asset management, finance,
architecture, IT, security/privacy, and project-delivery users. It answers five linked
questions:

1. Is the evidence strong enough to approve a large software commitment?
2. If so, what quantity should be committed initially and how should later orders be phased?
3. How much is contractual flexibility worth under uncertainty?
4. Which actual supplier offer has the best risk-adjusted commercial result?
5. After award, what action should be taken when commitment and active use diverge?

The numerical optimizer remains important, but it no longer approves a purchase by
itself. A separate readiness gate can hold the full commitment even when the engine can
calculate an attractive quantity.

## Tab 1: Plan and approve

### Required commercial and demand facts

| Input | Plain-language meaning | Suggested evidence owner |
|---|---|---|
| Software or project name | Label for the decision record | Procurement or project lead |
| Licence-unit definition | The metric being purchased: users, devices, cores, sites, or another unit | SAM/ITAM, technical owner, supplier |
| Total units after rollout | Maximum credible steady-state requirement | HR, IAM, inventory, application owner |
| Day-one units | Named population that can actually use the product at contract start | Project or deployment-wave owner |
| Full-commitment price | Price if the full target is committed immediately | Supplier quote, reseller response, catalogue |
| Contract term | Months covered by the commercial decision | Draft order form or sourcing strategy |
| Rollout-completion month | Month when the intended population should be substantially live | Approved implementation plan |
| Rollout confidence | Likelihood that dates and dependencies will hold | Joint project, IT, security, and business review |
| Planning posture | Balance between unused capacity and emergency overage | Procurement and finance |

Do not mix unlike licence metrics. A bundle of one user licence and two add-ons may be
represented as one user package or three subscription equivalents, but the quantity and
unit price must use the same denominator throughout.

### Mandatory readiness gate

Use **Confirmed** only when an accountable owner can point to evidence.

| Gate | Evidence expected | Consequence when not confirmed |
|---|---|---|
| Demand | Named day-one list and reconciled steady-state population | Hold full commitment |
| Architecture | Capacity or scalability tested for the first wave | Hold full commitment |
| Delivery | Approved dated deployment waves and named owners | Hold full commitment |
| Dependencies | Critical security, privacy, integration, data, and change items cleared | Hold full commitment |
| Pilot/POC | Required pilot completed and accepted | Hold full commitment |
| Usage reporting | Buyer can obtain active-use evidence at least monthly | Phase with conditions |
| Phased pricing | Suppliers have priced comparable full and phased structures | Phase with conditions |
| Usage owner | Named owner will run every reconciliation | Phase with conditions |

The tool intentionally does not calculate a readiness percentage. A score can hide one
critical blocker behind several easy checks. The outcome is one of:

- **Hold full commitment** — do not approve the target quantity;
- **Proceed only with phased commitment** — core delivery evidence is ready, but
  commercial or operating controls remain; or
- **Ready for commercial comparison** — compare actual compliant offers before approval.

### Primary outputs

- readiness decision, blockers, conditions, and missing decision-record fields;
- modelled initial floor and percentage of steady-state demand;
- expected activation and commitment schedule;
- P90 budget and risk-adjusted comparison with full commitment;
- break-even flexibility premium;
- three-structure supplier pricing request;
- order-form and PO controls; and
- downloadable approval plan, supplier-pricing CSV, and JSON model record.

The modelled initial floor is conditional when the readiness decision is a hold. It must
not be copied into a PO until the blockers are closed or an authorized exception is
documented.

## Tab 2: Compare offers

Use this after bidders or the incumbent provide actual commercial terms.

For each compliant offer, enter:

- monthly unit price;
- initial commitment;
- review cadence;
- true-down permission;
- contractual minimum;
- buffer;
- overage uplift;
- annual escalation;
- one-time fees; and
- monthly fixed fees.

All offers are evaluated on the same seeded demand paths and risk posture. The table
ranks expected cost, P90 budget, unused-capacity cost, utilization, and risk-adjusted
difference from the full-commitment baseline.

The lowest financial rank is not automatically the award recommendation. First confirm
functional, technical, security, legal, accessibility, implementation, and mandatory
commercial compliance. Record any qualitative value that is outside the model.

## Tab 3: Review usage

Run this monthly for material SaaS agreements and before a true-up, renewal, or
additional PO.

Enter:

- units currently paid or committed;
- actively used units under the agreed measurement rule;
- assigned but inactive units;
- monthly unit price;
- operating buffer; and
- whether true-down is contractually allowed.

The review returns:

- current utilization and unused units;
- monthly and annualized unused-cost exposure;
- units to reclaim or reassign immediately;
- recommended commitment after applying the buffer; and
- a true-up, true-down, freeze, or maintain action.

If the contract has no true-down right, the tool does not pretend that the buyer can
reduce invoices. It recommends stopping net-new purchases, consuming the existing pool,
and seeking credits, swaps, delayed billing, or renewal relief.

Retain the source usage report, reconciliation date, measurement rule, and approver with
the PO or contract-management record.

## Toronto evidence tab

The Toronto tab separates three kinds of analysis:

1. facts directly reported by the Auditor General;
2. transparent arithmetic derived from those facts; and
3. illustrative counterfactuals that were not disclosed supplier terms.

The readiness walkthrough shows that known architecture limits would have triggered a
hold-full-commitment decision. The premium slider then shows a retrospective upper-bound
difference if billing had followed observed use. That figure is not a savings claim and
must not be represented as recoverable or realized money.

## Procurement operating sequence

1. Define the licence metric and reconcile the demand population.
2. Complete the readiness gate with evidence owners—not procurement alone.
3. Download the pricing template and require comparable full and phased responses.
4. Enter actual compliant offers and compare TCO, P90, unused exposure, and risk.
5. Translate the selected structure into measurable dates, floors, prices, notices,
   reporting duties, and remedies.
6. Record cross-functional approval or a documented exception before issuing the PO.
7. Run the usage review monthly and before every adjustment date.
8. Replace forecast quantities with measured active use before each later order.
9. Re-run the plan when project dates, demand, supplier pricing, or contract terms change.

## Security and deployment

Do not put confidential supplier pricing, user-level data, or contract-sensitive terms
into a public Streamlit deployment. Use masked values or deploy the repository inside a
controlled organizational environment.

The open-source application is suitable for an analyst-led pilot. Enterprise-wide use
should add:

- SSO and role-based access;
- encrypted persistent storage and retention controls;
- approval workflow and immutable audit history;
- scheduled notifications and review calendars;
- integrations with IAM, HR, ITAM/SAM, ERP/PO, and supplier APIs;
- SKU, bundle, entitlement, tax, FX, and accounting logic; and
- organization-specific thresholds, policy rules, and approved legal language.
