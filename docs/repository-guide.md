# Repository guide

## Where to start

- Product user: run `streamlit run app.py` and read the interpretation tab.
- Sourcing analyst: copy the Toronto JSON, replace facts and options, and retain the
  evidence classes.
- Research reviewer: begin with `methodology.md`, the checked-in outputs, and tests.
- Contributor: begin with `models.py`, then follow the calculation path through forecast,
  pricing, simulation, optimizer, and reporting.

## Code map

| Path | Responsibility |
|---|---|
| `app.py` | Interactive model controls, results, charts, and downloads |
| `src/commitment_optimizer/models.py` | Validated domain objects |
| `src/commitment_optimizer/case_loader.py` | JSON-to-domain loading and evidence metadata |
| `src/commitment_optimizer/forecast.py` | Deterministic curve and stochastic paths |
| `src/commitment_optimizer/pricing.py` | Unit price selection and single-path monthly cash flow |
| `src/commitment_optimizer/simulation.py` | Cross-scenario aggregation and risk metrics |
| `src/commitment_optimizer/optimizer.py` | Candidate grid, price premiums, feasibility, ranking |
| `src/commitment_optimizer/analysis.py` | Break-even premium search |
| `src/commitment_optimizer/reporting.py` | CSV, JSON, Markdown, and monthly exports |
| `src/commitment_optimizer/cli.py` | Reproducible command-line orchestration |
| `case_studies/toronto` | Audit facts, sources, assumptions, and commercial scenarios |
| `outputs/toronto_m365` | Publication result bundle |
| `scripts/generate_charts.py` | Static article charts |
| `tests` | Unit, behavior, reproducibility, and reconciliation checks |

## Add a case study

1. Copy `case_studies/toronto/toronto_m365.json` into a new case directory.
2. Replace the organization, question, published facts, and source URLs.
3. Put public facts in a separate CSV with page or section references.
4. Mark every derived and hypothetical value with the correct evidence class.
5. Configure the forecast, quoted scenarios, and optimizer template.
6. Add at least one reconciliation test against a published or internal source.
7. Run the CLI into a new output directory.
8. Review outputs with commercial, delivery, finance, and legal owners before use.

## Modify the objective

The current objective weights the gap between expected cost and CVaR. If an organization
uses another decision rule, add it to `OptimizationConfig`, calculate it in
`simulate_option`, expose it in the UI, and add ranking tests. Do not silently replace the
meaning of `risk_adjusted_cost`.

## Reproduce publication assets

```bash
python -m pip install -e ".[dev,publication]"
commitment-optimizer \
  --case case_studies/toronto/toronto_m365.json \
  --output outputs/toronto_m365
python scripts/generate_charts.py
python -m pytest
```

The CLI run is deterministic because the case fixes its seed. A dashboard run may differ
if the user changes its scenario count or assumptions.

