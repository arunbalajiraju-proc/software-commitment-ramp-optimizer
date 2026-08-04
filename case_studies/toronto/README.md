# City of Toronto case study

This case demonstrates how a sourcing team could compare an upfront software commitment with phased and flexible alternatives before contract signature.

The public evidence establishes that deployment delays and unused licences occurred. It does **not** disclose every pricing tier, concession, bundle benefit, negotiation constraint, or internal forecast available when the contracts were signed. For that reason:

- published facts are stored separately in `audit_facts.csv`;
- the runnable M365 scenario identifies every counterfactual input as illustrative;
- simulation results are described as model outputs, not realized or guaranteed savings; and
- the tool reports break-even flexibility premiums so users can test a decision without inventing a vendor quote.

## What the approval gate would have done

The audit reported that the agreement covered an initial 10,000 users even though the
network had been estimated to support only 6,000 users and the architecture required a
scalability and performance review. Entered prospectively, those facts produce a
**hold-full-commitment** result because technical capacity is not confirmed.

The gate does not claim to know the correct alternative quantity. It requires the buyer to:

1. validate the first deployable wave;
2. close the architecture dependency;
3. obtain comparable full and phased supplier pricing;
4. attach later activation to verified usage; and
5. document any decision to override the hold.

## Retrospective boundary

The JSON includes a separate `counterfactual` block with the audit's examined M365
subscription spend of CAD 8,996,400 and reported unused cost of CAD 6,896,597 across Year
1 and the first nine months of Year 2. The application calculates what a usage-aligned
billing proxy would have cost after an adjustable premium.

This calculation uses observed outcomes and is therefore retrospective. It is an
upper-bound decision boundary, not a forecast or a claim that Microsoft offered the term.

Run the case from the repository root:

```bash
python -m commitment_optimizer \
  --case case_studies/toronto/toronto_m365.json \
  --output outputs/toronto_m365
```
