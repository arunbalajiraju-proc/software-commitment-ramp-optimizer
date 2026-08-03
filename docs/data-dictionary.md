# Data dictionary

## Forecast configuration

| Field | Type | Meaning |
|---|---|---|
| `horizon_months` | integer | Number of contract months to simulate |
| `target_units` | integer | Planned full-deployment population |
| `initial_active_units` | integer | Active users or licence-equivalent units at month zero |
| `midpoint_month` | number | Month where the unnormalized logistic curve crosses its midpoint |
| `growth_rate` | number | Steepness of the adoption curve |
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
