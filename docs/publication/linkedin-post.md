I built an open-source tool for a software sourcing problem that usually becomes visible
too late: the commercial commitment starts before deployment is ready.

The **Software Commitment & Ramp Optimizer** compares upfront commitments, phased
activation, review cadence, true-up/true-down rights, buffers, overage, and flexibility
premiums across uncertain adoption paths.

The interface now asks seven plain-language questions and turns them into an initial
order, phase-by-phase buying schedule, flexibility-price ceiling, negotiation terms, and
a downloadable procurement plan. The simulation mechanics remain reviewable, but the
primary experience is designed for procurement, software, finance, and project users.

I tested it against public City of Toronto Auditor General data. The audit reported an
M365 annual subscription cost of CAD 5.14M, 7.5% deployment at the end of Year 1, and CAD
4.76M in unused subscription cost for that year.

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
- guided Streamlit procurement planner and downloadable buying plan
- tests, transparent model details, and the documented Toronto case

Medium article: [MEDIUM_URL]

GitHub: https://github.com/arunbalajiraju-proc/software-commitment-ramp-optimizer

I would value feedback from software sourcing, SAM, FinOps, commercial, and IT delivery
practitioners—especially on the contract mechanics you would add next.

#Procurement #StrategicSourcing #SoftwareLicensing #FinOps #SaaS #OpenSource #RiskManagement
