I built an open-source tool for a software sourcing problem that usually becomes visible
too late: the commercial commitment starts before deployment is ready.

The **Software Commitment & Ramp Optimizer** compares upfront commitments, phased
activation, review cadence, true-up/true-down rights, buffers, overage, and flexibility
premiums across uncertain adoption paths.

I have now moved it beyond an optimizer into a practical sourcing and control workflow:

- an evidence-based hold/proceed gate before commitment approval;
- a deployment-aligned order and P90 budget;
- a downloadable supplier pricing schedule for full, phased, and true-down structures;
- comparison of actual supplier offers on the same demand scenarios; and
- a recurring post-award review that produces a reclaim, freeze, true-up, or true-down action.

I tested it against public City of Toronto Auditor General data. The audit reported an
M365 annual subscription cost of CAD 5.14M, 7.5% deployment at the end of Year 1, and CAD
4.76M in unused subscription cost for that year. The same audit said the network had been
estimated to support 6,000 users while the agreement covered an initial 10,000 users.
That evidence now triggers a hold-full-commitment decision in the tool.

The experiment does **not** claim Toronto could have obtained my counterfactual terms, and
the modelled differences are not realized savings. The useful output is a negotiation
boundary: under explicit assumptions, how much can a buyer pay for staged commitment
before the upfront discount becomes the better deal?

What is in the repo:

- seeded Monte Carlo adoption scenarios
- month-by-month commercial-term simulation
- expected, P90, and CVaR cost
- an auditable policy grid with an overage guardrail
- a break-even flexibility-premium calculator
- an auditable readiness gate and approval record
- actual supplier-offer comparison
- post-award licence reconciliation and action plan
- guided Streamlit workflow and downloadable sourcing pack
- tests, transparent model details, and the documented Toronto case

Medium article: [MEDIUM_URL]

GitHub: https://github.com/arunbalajiraju-proc/software-commitment-ramp-optimizer

I would value feedback from software sourcing, SAM, FinOps, commercial, and IT delivery
practitioners—especially on the contract mechanics you would add next.

#Procurement #StrategicSourcing #SoftwareLicensing #FinOps #SaaS #OpenSource #RiskManagement
