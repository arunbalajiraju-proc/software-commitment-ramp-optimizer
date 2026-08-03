# City of Toronto case study

This case demonstrates how a sourcing team could compare an upfront software commitment with phased and flexible alternatives before contract signature.

The public evidence establishes that deployment delays and unused licences occurred. It does **not** disclose every pricing tier, concession, bundle benefit, negotiation constraint, or internal forecast available when the contracts were signed. For that reason:

- published facts are stored separately in `audit_facts.csv`;
- the runnable M365 scenario identifies every counterfactual input as illustrative;
- simulation results are described as model outputs, not realized or guaranteed savings; and
- the tool reports break-even flexibility premiums so users can test a decision without inventing a vendor quote.

Run the case from the repository root:

```bash
python -m commitment_optimizer \
  --case case_studies/toronto/toronto_m365.json \
  --output outputs/toronto_m365
```
