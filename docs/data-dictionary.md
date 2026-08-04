# Data dictionary

## Readiness input and assessment

| Field | Type | Meaning |
|---|---|---|
| `demand_evidence_status` | status | Whether day-one and steady-state quantities have named evidence |
| `technical_capacity_status` | status | Whether architecture supports the first wave |
| `implementation_plan_status` | status | Whether dated deployment waves and owners are approved |
| `critical_dependencies_status` | status | Whether security, privacy, integration, data, and change blockers are cleared |
| `usage_reporting_status` | status | Whether buyer-accessible monthly active-use reporting exists |
| `pilot_required` / `pilot_complete` | boolean | Whether a required pilot has been completed and accepted |
| `phased_pricing_requested` | boolean | Whether comparable full and phased prices were requested |
| `decision_owner` | string | Accountable commitment decision owner |
| `project_owner` | string | Accountable deployment owner |
| `usage_review_owner` | string | Owner of each post-award reconciliation |
| `demand_evidence_reference` | string | Reference to the population or wave evidence |
| `decision` | enum | Hold full commitment, phase with conditions, or ready for comparison |
| `blockers` | list | Non-compensating items that prevent full commitment |
| `conditions` | list | Commercial or operating controls required before award |
| `record_gaps` | list | Missing audit-trail fields that do not change the numerical result |

## Forecast configuration

| Field | Type | Meaning |
|---|---|---|
| `horizon_months` | integer | Number of contract months to simulate |
| `target_units` | integer | Planned full-deployment population |
| `initial_active_units` | integer | Active users or licence-equivalent units at month zero |
| `midpoint_month` | number | Month where the unnormalized logistic curve crosses its midpoint |
| `growth_rate` | number | Steepness of the adoption curve |
| `rollout_complete_month` | integer or null | Month when the guided curve reaches target and begins its plateau; null retains end-of-horizon behavior |
| `delay_probability` | proportion | Probability that a material rollout delay occurs |
| `delay_min_months` | number | Earliest delay in the triangular distribution |
| `delay_mode_months` | number | Most likely delay in the triangular distribution |
| `delay_max_months` | number | Latest delay in the triangular distribution |
| `target_volatility_pct` | proportion | Standard deviation of the final-demand multiplier |
| `growth_volatility_pct` | proportion | Standard deviation of the adoption-speed multiplier |
| `simulations` | integer | Number of Monte Carlo demand paths |
| `seed` | integer | Random seed used to reproduce scenarios |

## Commercial option

| Field | Type | Meaning |
|---|---|---|
| `name` | string | Human-readable policy name |
| `price_tiers` | list | Unit-month prices beginning at specified commitment volumes |
| `initial_commitment_pct` | proportion | Initial commitment relative to the planning target |
| `adjustment_frequency_months` | integer | Months between formal commitment reviews |
| `allow_true_down` | boolean | Whether committed baseline can decrease at review |
| `minimum_commitment_units` | integer | Contractual floor that adjustments cannot cross |
| `buffer_pct` | proportion | Extra capacity added above demand at each review |
| `overage_multiplier` | number | Price multiplier for demand above commitment between reviews |
| `one_time_fee` | currency | Fee added once at contract inception |
| `monthly_fixed_fee` | currency | Fixed fee added each month |
| `annual_escalation_pct` | proportion | Compounded unit-price escalation after each 12 months |
| `unit_price_multiplier` | number | Multiplier applied to every tier, often representing flexibility premium |
| `description` | string | Plain-language scenario note |
| `evidence_class` | string | Published, derived, modelled, or user-entered status |

## Supplier quote

| Field | Meaning |
|---|---|
| `offer_name` | Supplier or commercial-structure label |
| `unit_price_month` | Quoted price per unit per month |
| `initial_commitment_units` | Quantity billed at contract start |
| `adjustment_frequency_months` | Formal true-up or true-down cadence |
| `allow_true_down` | Whether commitment can decrease at a review |
| `minimum_commitment_units` | Contractual quantity floor |
| `buffer_pct` | Capacity added above measured active use |
| `overage_premium_pct` | Price uplift on demand above commitment |
| `annual_escalation_pct` | Annual unit-price increase |
| `one_time_fee` / `monthly_fixed_fee` | Non-unit commercial charges |

## Usage snapshot and action

| Field | Meaning |
|---|---|
| `committed_units` | Units currently paid or contractually committed |
| `active_units` | Units meeting the buyer's agreed active-use rule |
| `assigned_but_inactive_units` | Assigned units that can be reclaimed or reassigned |
| `current_unused_cost_month` | Current unused units multiplied by monthly unit price |
| `annualized_unused_cost_exposure` | Current monthly unused cost multiplied by 12; not a forecast |
| `recommended_commitment_units` | Active use plus the selected operating buffer |
| `commitment_change_units` | Recommended commitment less current commitment |
| `primary_action` | True-up, true-down, freeze, or maintain instruction |

## Optimization configuration

| Field | Meaning |
|---|---|
| `initial_commitment_pct_grid` | Candidate starting commitments |
| `buffer_pct_grid` | Candidate operational buffers |
| `adjustment_frequency_options` | Candidate review cadences |
| `allow_true_down_options` | Whether each candidate permits true-down |
| `frequency_premium_pct` | Added price assumed for each cadence |
| `true_down_premium_pct` | Added price assumed for true-down rights |
| `risk_aversion` | Weight placed on the CVaR tail above expected cost |
| `cvar_confidence` | Quantile used to define the cost tail |
| `max_expected_overage_share` | Feasibility ceiling for emergency overage unit-months |

## Simulation output

| Field | Meaning |
|---|---|
| `expected_total_cost` | Mean total cost across all paths |
| `median_total_cost` | 50th-percentile total cost |
| `p90_total_cost` | 90th-percentile total cost |
| `cvar_total_cost` | Mean cost among paths at or above the configured tail threshold |
| `risk_adjusted_cost` | Expected cost plus weighted tail-cost gap |
| `expected_unused_cost` | Mean cost assigned to committed capacity above active demand |
| `expected_overage_cost` | Mean premium-inclusive cost for demand above commitment |
| `expected_unused_unit_months` | Mean sum of unused units across months |
| `expected_overage_unit_months` | Mean sum of overage units across months |
| `expected_overage_share_pct` | Expected overage unit-months divided by expected consumed unit-months |
| `expected_utilization_pct` | Mean demand divided by billed units |
| `monthly_expected_demand` | Mean active demand for each month |
| `monthly_expected_commitment` | Mean committed baseline for each month |
| `monthly_expected_cost` | Mean cost for each month |
