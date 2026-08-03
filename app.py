"""Guided Streamlit application for software licence procurement planning."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from commitment_optimizer.case_loader import load_case
from commitment_optimizer.planner import (
    PlannerInputs,
    PlannerResult,
    procurement_plan_markdown,
    procurement_schedule,
    recommended_start_units,
    review_frequency_label,
    run_procurement_plan,
)

ROOT = Path(__file__).resolve().parent
CASE_PATH = ROOT / "case_studies" / "toronto" / "toronto_m365.json"

CONFIDENCE_OPTIONS = {
    "High – funding, dependencies, and rollout dates are largely confirmed": "High",
    "Medium – the plan is credible, but some dates or dependencies may move": "Medium",
    "Low – major dependencies, approvals, or adoption dates remain uncertain": "Low",
}
RISK_OPTIONS = {
    "Balanced – weigh expected cost and downside risk": "Balanced",
    "Conservative – favour more coverage and lower overage exposure": "Conservative",
    "Cost focused – accept more overage risk to avoid unused licences": "Cost focused",
}
PRICE_BASIS_OPTIONS = ("Per licence per month", "Per licence per year")


def _money(currency: str, value: float) -> str:
    return f"{currency} {value:,.0f}"


def _price(currency: str, value: float) -> str:
    return f"{currency} {value:,.2f}"


def _set_generic_defaults() -> None:
    defaults = {
        "deal_name_input": "My software licence procurement",
        "currency_input": "CAD",
        "target_units_input": 1_000,
        "day_one_units_input": 100,
        "unit_price_input": 25.0,
        "price_basis_input": PRICE_BASIS_OPTIONS[0],
        "contract_months_input": 36,
        "rollout_month_input": 18,
        "confidence_input": list(CONFIDENCE_OPTIONS)[1],
        "risk_input": list(RISK_OPTIONS)[0],
        "overage_premium_input": 10.0,
        "monthly_premium_input": 20.0,
        "quarterly_premium_input": 12.0,
        "semiannual_premium_input": 6.0,
        "annual_premium_input": 0.0,
        "true_down_premium_input": 8.0,
        "simulations_input": 500,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def _load_toronto_example() -> None:
    st.session_state.update(
        {
            "deal_name_input": "Toronto M365 public audit example",
            "currency_input": "CAD",
            "target_units_input": 30_000,
            "day_one_units_input": 2_250,
            "unit_price_input": 14.28,
            "price_basis_input": PRICE_BASIS_OPTIONS[0],
            "contract_months_input": 36,
            "rollout_month_input": 36,
            "confidence_input": list(CONFIDENCE_OPTIONS)[1],
            "risk_input": list(RISK_OPTIONS)[0],
            "overage_premium_input": 10.0,
            "monthly_premium_input": 20.0,
            "quarterly_premium_input": 12.0,
            "semiannual_premium_input": 6.0,
            "annual_premium_input": 0.0,
            "true_down_premium_input": 8.0,
            "simulations_input": 500,
        }
    )
    st.session_state.pop("planner_result", None)


def _build_inputs() -> tuple[PlannerInputs | None, bool]:
    st.subheader("Tell us about the purchase")
    st.write(
        "Answer seven business questions. Use the best information currently available; "
        "you can rerun the plan when the supplier quote or rollout forecast changes."
    )
    st.info(
        "You need: the eventual licence requirement, day-one requirement, supplier price, "
        "contract term, expected rollout completion, and confidence in the rollout plan."
    )

    with st.form("procurement_planner_form"):
        st.markdown("#### 1. Purchase and demand")
        deal_name = st.text_input(
            "Software or project name",
            key="deal_name_input",
            help="A label for the downloadable procurement plan.",
        )
        demand_columns = st.columns(2)
        target_units = demand_columns[0].number_input(
            "How many licences will you need when rollout is complete?",
            min_value=1,
            step=100,
            key="target_units_input",
            help=(
                "Use the maximum credible steady-state requirement, not the quantity the "
                "supplier wants you to commit on day one."
            ),
        )
        day_one_units = demand_columns[1].number_input(
            "How many licences must be active on day one?",
            min_value=0,
            step=50,
            key="day_one_units_input",
            help=(
                "Count users, devices, cores, or other licence units that can actually use "
                "the software at contract start."
            ),
        )

        st.markdown("#### 2. Supplier price")
        price_columns = st.columns(3)
        currency = price_columns[0].selectbox(
            "Currency",
            ("CAD", "USD", "EUR", "GBP", "AUD"),
            key="currency_input",
        )
        quoted_price = price_columns[1].number_input(
            "Quoted price per licence",
            min_value=0.01,
            step=1.0,
            key="unit_price_input",
            help="Use the supplier's price for committing the full planned quantity now.",
        )
        price_basis = price_columns[2].selectbox(
            "Price basis",
            PRICE_BASIS_OPTIONS,
            key="price_basis_input",
        )

        st.markdown("#### 3. Contract and rollout")
        rollout_columns = st.columns(2)
        contract_months = rollout_columns[0].selectbox(
            "Contract term",
            (12, 24, 36, 48, 60),
            format_func=lambda value: f"{value} months",
            key="contract_months_input",
        )
        rollout_complete_month = rollout_columns[1].number_input(
            "By which contract month should rollout be substantially complete?",
            min_value=2,
            max_value=60,
            step=1,
            key="rollout_month_input",
            help=(
                "Ask the project manager when the intended population should be live. "
                "The plan will allow for delay based on your confidence selection."
            ),
        )
        confidence_label = st.selectbox(
            "How confident are you in the rollout dates?",
            tuple(CONFIDENCE_OPTIONS),
            key="confidence_input",
        )
        risk_label = st.selectbox(
            "How should the tool balance unused licences against emergency overage?",
            tuple(RISK_OPTIONS),
            key="risk_input",
        )

        with st.expander("Optional: replace negotiation assumptions with supplier quotes"):
            st.caption(
                "Leave these defaults for an initial planning run. Replace them when bidders "
                "price the flexibility you request."
            )
            overage_premium = st.number_input(
                "Emergency overage price uplift",
                min_value=0.0,
                max_value=200.0,
                step=1.0,
                key="overage_premium_input",
                help="10 means emergency units cost 10% more than the contracted unit price.",
            )
            premium_columns = st.columns(4)
            monthly_premium = premium_columns[0].number_input(
                "Monthly flexibility premium",
                min_value=0.0,
                max_value=200.0,
                step=1.0,
                key="monthly_premium_input",
            )
            quarterly_premium = premium_columns[1].number_input(
                "3-month premium",
                min_value=0.0,
                max_value=200.0,
                step=1.0,
                key="quarterly_premium_input",
            )
            semiannual_premium = premium_columns[2].number_input(
                "6-month premium",
                min_value=0.0,
                max_value=200.0,
                step=1.0,
                key="semiannual_premium_input",
            )
            annual_premium = premium_columns[3].number_input(
                "Annual premium",
                min_value=0.0,
                max_value=200.0,
                step=1.0,
                key="annual_premium_input",
            )
            true_down_premium = st.number_input(
                "Additional premium for true-down rights",
                min_value=0.0,
                max_value=200.0,
                step=1.0,
                key="true_down_premium_input",
            )
            simulations = st.select_slider(
                "Planning scenarios",
                options=[250, 500, 1_000, 2_000],
                key="simulations_input",
                help="500 is suitable for planning. Use 2,000 for a more stable final memo.",
            )

        submitted = st.form_submit_button(
            "Build my procurement plan",
            type="primary",
            width="stretch",
        )

    if not submitted:
        return None, False
    if day_one_units > target_units:
        st.error("Day-one licences cannot exceed the total planned requirement.")
        return None, True
    if rollout_complete_month > contract_months:
        st.error("Rollout completion must fall within the selected contract term.")
        return None, True

    monthly_price = quoted_price / 12 if price_basis.endswith("year") else quoted_price
    try:
        inputs = PlannerInputs(
            deal_name=deal_name,
            currency=currency,
            target_units=int(target_units),
            day_one_units=int(day_one_units),
            unit_price_month=float(monthly_price),
            contract_months=int(contract_months),
            rollout_complete_month=int(rollout_complete_month),
            rollout_confidence=CONFIDENCE_OPTIONS[confidence_label],
            risk_posture=RISK_OPTIONS[risk_label],
            overage_premium_pct=float(overage_premium) / 100,
            frequency_premium_pct={
                1: float(monthly_premium) / 100,
                3: float(quarterly_premium) / 100,
                6: float(semiannual_premium) / 100,
                12: float(annual_premium) / 100,
            },
            true_down_premium_pct=float(true_down_premium) / 100,
            simulations=int(simulations),
        )
    except ValueError as exc:
        st.error(str(exc))
        return None, True
    return inputs, True


def _render_recommendation(result: PlannerResult) -> None:
    inputs = result.inputs
    option = result.optimized.option
    recommendation = result.optimized.summary
    baseline = result.baseline_summary
    start_units = recommended_start_units(result)
    start_share = start_units / inputs.target_units
    frequency = review_frequency_label(option.adjustment_frequency_months)
    assumed_premium = option.unit_price_multiplier - 1.0

    st.divider()
    st.header("Your procurement recommendation")
    if start_units >= inputs.target_units:
        st.success(
            f"The model supports committing the planned {inputs.target_units:,} licences "
            "at contract start under the assumptions entered."
        )
    else:
        st.success(
            f"Start with {start_units:,} licences—not the full {inputs.target_units:,}. "
            f"Review the commitment {frequency} and add licences as verified usage grows."
        )

    metric_columns = st.columns(3)
    metric_columns[0].metric(
        "Order at contract start",
        f"{start_units:,} licences",
        f"{start_share:.1%} of planned need",
    )
    metric_columns[1].metric(
        "Quantity review",
        frequency.capitalize(),
        f"{option.buffer_pct:.0%} usage buffer",
    )
    if result.break_even_premium is None:
        ceiling_label = "No positive ceiling"
        ceiling_context = "Full commitment currently prices better"
    else:
        ceiling_price = inputs.unit_price_month * (1 + result.break_even_premium)
        ceiling_label = f"{result.break_even_premium:.1%} premium"
        ceiling_context = f"Up to {_price(inputs.currency, ceiling_price)} / licence / month"
    metric_columns[2].metric(
        "Maximum flexibility price",
        ceiling_label,
        ceiling_context,
        help=(
            "The phased structure loses its modelled risk-adjusted advantage above this "
            "premium relative to the full-commitment quote."
        ),
    )

    true_down_text = (
        "The selected plan includes a right to reduce quantities at review dates."
        if option.allow_true_down
        else "The selected plan only increases quantities; it does not assume true-down rights."
    )
    st.write(
        f"At each {frequency} review, measure actual active usage and reset the next "
        f"commitment to usage plus a {option.buffer_pct:.0%} buffer. {true_down_text} "
        f"The model assumes that this flexibility adds {assumed_premium:.1%} to the "
        "full-commitment unit price."
    )

    st.subheader("1. What to procure and when")
    schedule = pd.DataFrame(procurement_schedule(result)).rename(
        columns={
            "timing": "Timing",
            "expected_active_units": "Expected active licences",
            "planned_committed_units": "Planned committed licences",
            "planned_change_units": "Planned change",
            "action": "Procurement action",
        }
    )
    st.dataframe(
        schedule[
            [
                "Timing",
                "Expected active licences",
                "Planned committed licences",
                "Planned change",
                "Procurement action",
            ]
        ],
        width="stretch",
        hide_index=True,
        column_config={
            column: st.column_config.NumberColumn(format="%,d")
            for column in (
                "Expected active licences",
                "Planned committed licences",
                "Planned change",
            )
        },
    )
    st.caption(
        "This is a planning schedule, not a fixed order calendar. At each review, replace "
        "the forecast quantity with measured active usage before issuing the next order."
    )

    months = list(range(1, inputs.contract_months + 1))
    ramp_chart = go.Figure()
    ramp_chart.add_trace(
        go.Scatter(
            x=months,
            y=recommendation.monthly_expected_demand,
            name="Expected active licences",
            line={"color": "#2F5D62", "width": 3},
        )
    )
    ramp_chart.add_trace(
        go.Scatter(
            x=months,
            y=recommendation.monthly_expected_commitment,
            name="Recommended commitment",
            line={"color": "#D08C60", "width": 3, "dash": "dash"},
        )
    )
    ramp_chart.update_layout(
        title="Expected active usage and recommended committed quantity",
        xaxis_title="Contract month",
        yaxis_title="Licence units",
        legend_title_text="",
    )
    st.plotly_chart(ramp_chart, width="stretch")

    st.subheader("2. Financial comparison")
    expected_difference = baseline.expected_total_cost - recommendation.expected_total_cost
    comparison = pd.DataFrame(
        [
            {
                "Buying approach": "Commit all licences at contract start",
                "Expected total cost": baseline.expected_total_cost,
                "High-cost scenario (P90)": baseline.p90_total_cost,
                "Expected unused-licence spend": baseline.expected_unused_cost,
                "Expected utilization": baseline.expected_utilization_pct,
            },
            {
                "Buying approach": "Recommended phased plan",
                "Expected total cost": recommendation.expected_total_cost,
                "High-cost scenario (P90)": recommendation.p90_total_cost,
                "Expected unused-licence spend": recommendation.expected_unused_cost,
                "Expected utilization": recommendation.expected_utilization_pct,
            },
        ]
    )
    st.dataframe(
        comparison,
        width="stretch",
        hide_index=True,
        column_config={
            column: st.column_config.NumberColumn(
                label=column,
                format=f"{inputs.currency} %,.0f",
            )
            for column in (
                "Expected total cost",
                "High-cost scenario (P90)",
                "Expected unused-licence spend",
            )
        }
        | {
            "Expected utilization": st.column_config.NumberColumn(format="%.1f%%")
        },
    )
    st.info(
        f"Under the assumptions entered, the recommended structure has an expected cost "
        f"difference of {_money(inputs.currency, expected_difference)} versus committing "
        "all planned licences at signing. This is a modelled planning difference—not "
        "realized savings or a supplier quote."
    )

    st.subheader("3. Terms to request from the supplier")
    true_down_clause = (
        "Permit quantity reductions at each review, subject to the agreed committed floor."
        if option.allow_true_down
        else "Permit true-up at each review without retroactive repricing."
    )
    if result.break_even_premium is None:
        pricing_clause = (
            "Request phased pricing, but rerun the plan because the current assumptions do "
            "not support paying a premium over the full-commitment price."
        )
    else:
        ceiling_monthly = inputs.unit_price_month * (1 + result.break_even_premium)
        pricing_clause = (
            f"Keep the phased unit price at or below {_price(inputs.currency, ceiling_monthly)} "
            "per licence per month "
            f"({result.break_even_premium:.1%} above the full-commitment quote)."
        )
    st.markdown(
        f"""
1. **Initial committed floor:** {start_units:,} licence units.
2. **Formal quantity review:** {frequency.capitalize()} using measured active usage.
3. **Quantity formula:** active usage plus a {option.buffer_pct:.0%} operating buffer.
4. **Adjustment right:** {true_down_clause}
5. **Pricing guardrail:** {pricing_clause}
6. **Overage protection:** cap emergency units at {inputs.overage_premium_pct:.0%}
   above the contracted unit price and prohibit retroactive repricing.
7. **Billing:** invoice added quantities only from their activation date.
8. **Operational rights:** require usage reporting and preserve reassignment or
   transfer rights where the licence metric permits.
"""
    )

    st.subheader("4. What to do before issuing the PO")
    st.markdown(
        """
1. Reconcile the eligible population with HR, identity, device, or application records.
2. Confirm rollout milestones and dependencies with the project or implementation owner.
3. Ask bidders for two comparable prices: full commitment and the recommended phased structure.
4. Replace the optional premium assumptions with the supplier quotes and rerun this plan.
5. Put the activation schedule, review dates, quantity formula, and pricing
   protections in the order form.
6. Assign an owner to review actual usage before every scheduled quantity adjustment.
"""
    )

    download_columns = st.columns(2)
    download_columns[0].download_button(
        "Download procurement plan",
        procurement_plan_markdown(result),
        "software-procurement-plan.md",
        "text/markdown",
        width="stretch",
    )
    full_payload = {
        "notice": "Model outputs under user-controlled assumptions; not realized savings.",
        "inputs": asdict(inputs),
        "recommended_option": option.to_dict(),
        "recommended_summary": recommendation.to_dict(),
        "full_commitment_summary": baseline.to_dict(),
        "break_even_flexibility_premium_pct": (
            None
            if result.break_even_premium is None
            else result.break_even_premium * 100
        ),
        "procurement_schedule": procurement_schedule(result),
    }
    download_columns[1].download_button(
        "Download model details",
        json.dumps(full_payload, indent=2),
        "software-procurement-model.json",
        "application/json",
        width="stretch",
    )

    with st.expander("Advanced model details"):
        details = pd.DataFrame(
            [
                {
                    "Measure": "Expected total cost",
                    "Recommended plan": recommendation.expected_total_cost,
                    "Full commitment": baseline.expected_total_cost,
                },
                {
                    "Measure": "P90 total cost",
                    "Recommended plan": recommendation.p90_total_cost,
                    "Full commitment": baseline.p90_total_cost,
                },
                {
                    "Measure": "CVaR total cost",
                    "Recommended plan": recommendation.cvar_total_cost,
                    "Full commitment": baseline.cvar_total_cost,
                },
                {
                    "Measure": "Risk-adjusted cost used for selection",
                    "Recommended plan": recommendation.risk_adjusted_cost,
                    "Full commitment": baseline.risk_adjusted_cost,
                },
            ]
        )
        st.dataframe(
            details,
            width="stretch",
            hide_index=True,
            column_config={
                column: st.column_config.NumberColumn(format=f"{inputs.currency} %,.0f")
                for column in ("Recommended plan", "Full commitment")
            },
        )
        st.write(
            f"The optimizer evaluated {result.optimized.candidates_evaluated} auditable "
            f"policies; {result.optimized.candidates_feasible} met the selected overage "
            "guardrail. CVaR is the average cost in the most expensive 10% of modelled outcomes."
        )


def _render_how_to_use() -> None:
    st.header("How to use the planner")
    st.write(
        "The planner separates information your organization should know from commercial "
        "terms you need to obtain from the supplier."
    )
    input_guide = pd.DataFrame(
        [
            {
                "Input": "Total licences after rollout",
                "What it means": "Expected steady-state requirement",
                "Where to get it": (
                    "HR, IAM, device inventory, application owner, or demand forecast"
                ),
            },
            {
                "Input": "Day-one licences",
                "What it means": "Units that can actually use the software at contract start",
                "Where to get it": "Deployment wave 1 or confirmed go-live population",
            },
            {
                "Input": "Full-commitment unit price",
                "What it means": "Supplier price if all planned units are committed now",
                "Where to get it": "Quote, pricing sheet, reseller response, or incumbent renewal",
            },
            {
                "Input": "Rollout completion month",
                "What it means": "When the intended population should be substantially live",
                "Where to get it": "Approved project plan or implementation workplan",
            },
            {
                "Input": "Rollout confidence",
                "What it means": "Likelihood that dates and dependencies will hold",
                "Where to get it": (
                    "Joint assessment by IT, security, project, change, and business owners"
                ),
            },
        ]
    )
    st.dataframe(input_guide, width="stretch", hide_index=True)
    st.subheader("How to read the answer")
    st.markdown(
        """
- **Order at contract start** is the proposed initial committed floor.
- **Quantity review** is how often you should validate usage before adding or reducing licences.
- **Procurement schedule** is a forecast-based planning calendar; actual orders
  should use measured usage.
- **Maximum flexibility price** is the highest modelled premium to consider for staged activation.
- **P90 cost** is a prudent budget figure exceeded in only about 10% of simulated outcomes.
- **Negotiation terms** translate the selected policy into an order-form and RFP position.
"""
    )
    st.warning(
        "The planner does not validate licence metrics, bundle entitlements, technical "
        "architecture, legal enforceability, supplier willingness, or confidential discounts."
    )


def _render_toronto_case() -> None:
    case = load_case(CASE_PATH)
    st.header("Public example: City of Toronto M365 audit")
    st.write(case.decision_question)
    st.warning(case.simulation_notice)
    facts = pd.DataFrame(case.published_facts)
    st.dataframe(
        facts[["fact", "value", "unit", "source_page"]],
        width="stretch",
        hide_index=True,
    )
    for source in case.sources:
        st.markdown(f"- [{source['title']}]({source['url']})")
    st.info(
        "Loading these quantities creates a new guided planning scenario using the "
        "planner's confidence assumptions and 500 scenarios. It does not replace or "
        "exactly reproduce the checked-in 2,000-scenario publication run."
    )
    st.button(
        "Use the audit quantities in a new guided plan",
        on_click=_load_toronto_example,
    )


def main() -> None:
    st.set_page_config(
        page_title="Software Licence Procurement Planner",
        page_icon="🧭",
        layout="wide",
    )
    _set_generic_defaults()

    st.title("Software Licence Procurement Planner")
    st.caption(
        "Turn a software rollout forecast and supplier price into an initial order, "
        "phased buying schedule, pricing guardrail, and negotiation plan."
    )
    planner_tab, guide_tab, example_tab = st.tabs(
        ["Build a procurement plan", "How to use it", "Toronto public example"]
    )

    with planner_tab:
        inputs, submitted = _build_inputs()
        if submitted and inputs is not None:
            try:
                with st.spinner(
                    "Testing rollout scenarios and building the procurement schedule…"
                ):
                    st.session_state["planner_result"] = run_procurement_plan(inputs)
            except (RuntimeError, ValueError) as exc:
                st.error(f"The plan could not be generated: {exc}")
        result = st.session_state.get("planner_result")
        if isinstance(result, PlannerResult):
            _render_recommendation(result)
        elif not submitted:
            st.caption(
                "No plan has been generated yet. Replace the example values and select "
                "**Build my procurement plan**."
            )

    with guide_tab:
        _render_how_to_use()

    with example_tab:
        _render_toronto_case()


if __name__ == "__main__":
    main()
