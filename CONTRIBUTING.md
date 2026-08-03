# Contributing

Contributions that improve sourcing realism, evidence discipline, validation, or user
experience are welcome.

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev,publication]"
python -m pytest
python -m ruff check .
```

## Pull-request expectations

- Add tests for every behavior change.
- Keep stochastic tests seeded and reproducible.
- Preserve the separation between published facts, derived values, and illustrative
  assumptions.
- Cite a primary source and page or section for new public case-study facts.
- Never describe modelled differences as realized savings.
- Document new fields in `docs/data-dictionary.md`.
- Update the methodology when changing the objective, distributions, or default
  premiums.

Please open an issue before making a large architectural change.

