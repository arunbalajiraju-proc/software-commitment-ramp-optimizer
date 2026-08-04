# Software Commitment & Ramp Optimizer

A transparent software-commitment decision and control workflow for sourcing teams,
project owners, finance, architecture, and software asset management.

The application now covers three connected decisions:

1. **Plan and approve:** test demand, delivery, architecture, dependency, pilot, and
   usage-reporting evidence before a large commitment is approved.
2. **Compare supplier offers:** evaluate actual full and phased commercial structures
   against the same seeded demand scenarios.
3. **Control post-award usage:** turn active use, inactive assignments, contractual
   true-down rights, and price into a reclaim, freeze, true-up, or true-down action.

It returns a hold/proceed gate, modelled initial order, review cadence, phase-by-phase
buying schedule, P90 budget, flexibility-price ceiling, supplier pricing template,
contract controls, and downloadable decision record. Technical simulation controls
remain optional.

The tool compares upfront commitments, staged activation ramps, true-up/true-down
rights, review cadence, buffers, fees, escalation, and overage pricing across thousands
of possible adoption paths. It reports expected cost, P90 cost, conditional value at
risk (CVaR), unused capacity, overage exposure, utilization, and the break-even price of
commercial flexibility.

![Modelled option-cost comparison](docs/images/option_cost_comparison.png)

> **Important:** the City of Toronto audit figures in this repository are public facts.
> Alternative contract structures and demand distributions are illustrative model
> assumptions. Outputs are not realized savings, legal advice, or evidence that a
> supplier offered or would accept a particular term.

## The procurement problem

Software sourcing often rewards a larger initial commitment with a lower unit price.
Deployment, however, depends on infrastructure, integrations, data, security approvals,
change management, and business readiness. If those dependencies slip, the discount can
be real while the economic value is not.

Most software asset-management tools identify shelfware after purchase. This project
answers a different question before signature:

> What initial floor, activation schedule, review cadence, buffer, and flexibility
> premium produce the best risk-adjusted commercial outcome under uncertain adoption?

## Toronto case included

The City of Toronto Auditor General reported that an M365 agreement described as 30,000
subscription licences cost CAD 5,140,800 annually. At the end of Year 1, deployment was
7.5%, and the audit reported CAD 4,755,240 in unused subscription cost. The first nine
months of Year 2 showed 44.5% usage and CAD 2,141,357 of unused cost.

The case loader stores those facts separately from counterfactual terms. The model's
upfront cost proxy exactly reconciles the Year-1 arithmetic:

```text
30,000 licence equivalents × CAD 14.28 per month × 12 = CAD 5,140,800
92.5% unused × CAD 5,140,800 = CAD 4,755,240
```

Primary sources:

- [City of Toronto Auditor General: Audit of Software Acquisition and Licence Management (2024)](https://www.toronto.ca/legdocs/mmis/2024/au/bgrd/backgroundfile-251260.pdf)
- [City of Toronto Auditor General: 2026 Consolidated Follow-up Report](https://www.toronto.ca/legdocs/mmis/2026/au/bgrd/backgroundfile-288922.pdf)

See [the evidence file](case_studies/toronto/audit_facts.csv),
[source notes](case_studies/toronto/SOURCES.md), and
[case documentation](case_studies/toronto/README.md).

### Would this tool have prevented the Toronto M365 unused cost?

It could not have guaranteed that result, because the confidential agreement, supplier
concessions, implementation forecast, and internal approvals are not public. It would,
however, have produced a clear **hold-full-commitment** decision if the public facts had
been entered honestly:

- the audit said the network was estimated to support only 6,000 users while the
  agreement committed an initial 10,000 users;
- the architecture still required scalability and performance review;
- later purchasing was not tied to verified deployment; and
- the commercial evaluation emphasized the bulk discount without an enforceable
  deployment-aligned alternative.

The improved workflow would have required the technical-capacity gate to close, asked
suppliers to price full and phased structures on the same response sheet, limited the
initial PO to an approved wave, and blocked later activation until usage evidence was
reviewed. A decision-maker could still override the gate, but the exposure, owner,
exception, and rejected alternative would be documented.

For context, the audit examined CAD 8,996,400 of M365 subscription spend across Year 1
and the first nine months of Year 2 and reported CAD 6,896,597 of unused cost. The app
contains a separately labelled retrospective boundary showing how usage-aligned billing
would have behaved at different flexibility premiums. It is an upper-bound
counterfactual—not realized savings.

## What the experiment found

With the checked-in assumptions and 2,000 seeded demand scenarios, the search evaluated
288 policies and found 204 that met a 10% expected-overage guardrail. The lowest
risk-adjusted model output used:

- a 7.5% initial floor;
- a six-month review cadence;
- true-up only;
- a 10% capacity buffer; and
- a modelled 6% unit-price premium for six-month flexibility.

Its expected 36-month cost was CAD 8.68 million and risk-adjusted cost was CAD 9.35
million, compared with CAD 15.58 million and CAD 15.74 million for the upfront proxy.
That CAD 6.39 million risk-adjusted difference is a **simulation result**, not a claim of
recoverable or realized savings. The flexible policy remained preferable in the model
until its unit price was approximately 78.4% above the public cost proxy. That boundary
is a negotiating input, not a market-price assertion.

Full outputs are checked in under [`outputs/toronto_m365`](outputs/toronto_m365).

## Quick start

Requires Python 3.11 or newer.

```bash
git clone https://github.com/arunbalajiraju-proc/software-commitment-ramp-optimizer.git
cd software-commitment-ramp-optimizer
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev,publication]"
```

Run the interactive dashboard:

```bash
streamlit run app.py
```

In the app:

1. build the approval and procurement plan;
2. replace the example offer rows with actual supplier terms;
3. download the pricing request, decision record, and comparison; and
4. return monthly after award to run the usage-review action.

Reproduce the Toronto publication run:

```bash
commitment-optimizer \
  --case case_studies/toronto/toronto_m365.json \
  --output outputs/toronto_m365
python scripts/generate_charts.py
```

Run validation:

```bash
python -m pytest
python -m ruff check .
```

## Components

| Component | What it does | Main file |
|---|---|---|
| Guided planner | Translates plain-language procurement inputs into validated forecast, pricing, and risk settings | `planner.py` |
| Readiness gate | Blocks an unsupported full commitment and identifies evidence, owner, and control gaps | `readiness.py` |
| Supplier-offer comparison | Prices actual full, phased, and true-down offers on the same scenarios | `quotes.py` |
| Usage reconciliation | Quantifies unused exposure and produces a reclaim, freeze, true-up, or true-down action | `monitoring.py` |
| Public counterfactual | Calculates a strictly labelled retrospective usage-aligned billing boundary | `case_analysis.py` |
| Evidence boundary | Loads public facts separately from assumptions and hypothetical terms | `case_loader.py` |
| Adoption forecast | Creates seeded logistic rollout paths with demand, speed, and delay uncertainty | `forecast.py` |
| Commercial engine | Applies floors, review dates, buffers, true-down rules, overage, fees, and escalation monthly | `pricing.py` |
| Monte Carlo engine | Evaluates every option across all demand scenarios and calculates risk statistics | `simulation.py` |
| Policy optimizer | Grid-searches auditable combinations and enforces an overage feasibility guardrail | `optimizer.py` |
| Break-even analysis | Finds the maximum flexibility premium that preserves a risk-adjusted advantage | `analysis.py` |
| Exports | Writes summary CSV, monthly profiles, detailed JSON, and a Markdown result card | `reporting.py` |
| User interface | Connects approval, sourcing, offer comparison, and recurring control in one workflow | `webapp.py` |

Read [the architecture](docs/architecture.md), [methodology](docs/methodology.md),
[data dictionary](docs/data-dictionary.md), [interpretation guide](docs/interpretation-guide.md),
[repository guide](docs/repository-guide.md), and
[organizational pilot playbook](docs/organizational-pilot.md).

## Repository structure

```text
software-commitment-ramp-optimizer/
├── app.py                         # Stable Streamlit entry point
├── case_studies/toronto/          # Public facts, sources, and runnable case
├── docs/                          # Architecture, method, guides, article, charts
├── outputs/toronto_m365/          # Reproducible model results
├── scripts/generate_charts.py     # Publication chart build
├── src/commitment_optimizer/      # Decision gate, sourcing, monitoring, and engine
└── tests/                         # Unit and public-arithmetic reconciliation tests
```

## Intended use

Use the workflow as an auditable control during intake, sourcing, approval, PO issuance,
true-up, and renewal. The open-source release is suitable for an analyst-led pilot and
can be run inside an organization's environment. A public Streamlit deployment should
use only non-confidential or masked values.

Enterprise-wide production deployment still requires identity and access management,
persistent encrypted storage, approval workflow, audit-history controls, notifications,
and integrations with IAM, HR, ITAM/SAM, ERP/PO, and supplier usage systems. The tool
does not replace contract review, architecture analysis, supplier quotes, or a validated
deployment plan.

See the [guided user guide](docs/user-guide.md) for the exact inputs, owners, output
definitions, and recommended sourcing workflow.

## Licence and attribution

Code is released under the [MIT License](LICENSE). Public-source data retains its source
attribution. If you use the model in research, see [`CITATION.cff`](CITATION.cff).
