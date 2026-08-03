# Software Commitment & Ramp Optimizer

A transparent, pre-award decision tool for sourcing teams deciding how much software
capacity to commit before deployment readiness and adoption are certain.

The tool compares upfront commitments, staged activation ramps, true-up/true-down
rights, review cadence, buffers, fees, escalation, and overage pricing across thousands
of possible adoption paths. It reports expected cost, P90 cost, conditional value at
risk (CVaR), unused capacity, overage exposure, utilization, and the break-even price of
commercial flexibility.

**[Try the live application](https://software-commitment-ramp-optimizer-fc6bp9efudeeubwsdgnpo5.streamlit.app/)**

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
| Evidence boundary | Loads public facts separately from assumptions and hypothetical terms | `case_loader.py` |
| Adoption forecast | Creates seeded logistic rollout paths with demand, speed, and delay uncertainty | `forecast.py` |
| Commercial engine | Applies floors, review dates, buffers, true-down rules, overage, fees, and escalation monthly | `pricing.py` |
| Monte Carlo engine | Evaluates every option across all demand scenarios and calculates risk statistics | `simulation.py` |
| Policy optimizer | Grid-searches auditable combinations and enforces an overage feasibility guardrail | `optimizer.py` |
| Break-even analysis | Finds the maximum flexibility premium that preserves a risk-adjusted advantage | `analysis.py` |
| Exports | Writes summary CSV, monthly profiles, detailed JSON, and a Markdown result card | `reporting.py` |
| User interface | Provides editable assumptions, option comparison, charts, evidence, and downloads | `app.py` |

Read [the architecture](docs/architecture.md), [methodology](docs/methodology.md),
[data dictionary](docs/data-dictionary.md), [interpretation guide](docs/interpretation-guide.md),
and [repository guide](docs/repository-guide.md).

## Repository structure

```text
software-commitment-ramp-optimizer/
├── app.py                         # Streamlit decision dashboard
├── case_studies/toronto/          # Public facts, sources, and runnable case
├── docs/                          # Architecture, method, guides, article, charts
├── outputs/toronto_m365/          # Reproducible model results
├── scripts/generate_charts.py     # Publication chart build
├── src/commitment_optimizer/      # Forecast, pricing, simulation, optimization
└── tests/                         # Unit and public-arithmetic reconciliation tests
```

## Intended use

Use the model during sourcing to define a negotiation zone and to make assumptions
reviewable by procurement, finance, IT, security, implementation, and legal teams. It
does not replace supplier quotes, contract review, architecture analysis, or a validated
deployment plan.

## Licence and attribution

Code is released under the [MIT License](LICENSE). Public-source data retains its source
attribution. If you use the model in research, see [`CITATION.cff`](CITATION.cff).

