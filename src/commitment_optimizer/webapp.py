"""Organization-ready Streamlit workflow for software commitment decisions."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from .case_analysis import usage_aligned_counterfactual
from .case_loader import load_case
from .monitoring import UsageReviewResult, UsageSnapshot, review_usage
from .planner import (
    PlannerInputs,
    PlannerResult,
    procurement_plan_markdown,
    procurement_schedule,
    recommended_start_units,
    review_frequency_label,
    run_procurement_plan,
)
from .quotes import (
    SupplierQuote,
    SupplierQuoteEvaluation,
    evaluate_supplier_quotes,
    supplier_pricing_request_csv,
    supplier_pricing_request_rows,
)
from .readiness import (
    CONFIRMED,
    HOLD_FULL_COMMITMENT,
    IN_PROGRESS,
    NOT_APPLICABLE,
    NOT_ASSESSED,
    PHASE_WITH_CONDITIONS,
    ReadinessInputs,
)

ROOT = Path(__file__).resolve().parents[2]
CASE_PATH = ROOT / "case_studies" / "toronto" / "toronto_m365.json"

CONFIDENCE_OPTIONS = {
    "High – dates, funding, and dependencies are largely confirmed": "High",
    "Medium – the plan is credible, but some dates or dependencies may move": "Medium",
    "Low – major dependencies, approvals, or adoption dates remain uncertain": "Low",
}
RISK_OPTIONS = {
    "Balanced – weigh expected cost and downside risk": "Balanced",
    "Conservative – favour coverage and lower overage exposure": "Conservative",
    "Cost focused – accept more overage risk to avoid unused capacity": "Cost focused",
}
PRICE_BASIS_OPTIONS = ("Per unit per month", "Per unit per year")
REQUIRED_STATUS_OPTIONS = (NOT_ASSESSED, IN_PROGRESS, CONFIRMED)


def _money(currency: str, value: float) -> str:
    return f"{currency} {value:,.0f}"


def _price(currency: str, value: float) -> str:
    return f"{currency} {value:,.2f}"


def _set_generic_defaults() -> None:
    defaults = {
        "deal_name_input": "My software licence procurement",
        "unit_label_input": "users",
        "currency_input": "CAD",
        "target_units_input": 1_000,
        "day_one_units_input": 100,
        "unit_price_input": 25.0,
        "price_basis_input": PRICE_BASIS_OPTIONS[0],
        "contract_months_input": 36,
        "rollout_month_input": 18,
        "confidence_input": list(CONFIDENCE_OPTIONS)[1],
        "risk_input": list(RISK_OPTIONS)[0],
        "demand_status_input": NOT_ASSESSED,
        "technical_status_input": NOT_ASSESSED,
        "plan_status_input": NOT_ASSESSED,
        "dependency_status_input": NOT_ASSESSED,
        "usage_status_input": NOT_ASSESSED,
        "pilot_status_input": "No pilot required",
        "phased_pricing_input": "Not yet",
        "decision_owner_input": "",
        "project_owner_input": "",
        "usage_owner_input": "",
        "demand_reference_input": "",
        "overage_premium_input": 10.0,
        "monthly_premium_input": 20.0,
        "quarterly_premium_input": 12.0,
        "semiannual_premium_input": 6.0,
        "annual_premium_input": 0.0,
        "true_down_premium_input": 8.0,
        "simulations_input": 500,
        "usage_committed_input": 1_000,
        "usage_active_input": 700,
        "usage_inactive_input": 50,
        "usage_price_input": 25.0,
        "usage_buffer_input": 10.0,
        "usage_true_down_input": False,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def _load_toronto_example() -> None:
    st.session_state.update(
        {
            "deal_name_input": "Toronto M365 public audit example",
            "unit_label_input": "subscription licence equivalents",
            "currency_input": "CAD",
            "target_units_input": 30_000,
            "day_one_units_input": 2_250,
            "unit_price_input": 14.28,
            "price_basis_input": PRICE_BASIS_OPTIONS[0],
            "contract_months_input": 36,
            "rollout_month_input": 24,
            "confidence_input": list(CONFIDENCE_OPTIONS)[2],
            "risk_input": list(RISK_OPTIONS)[0],
            "demand_status_input": IN_PROGRESS,
            "technical_status_input": NOT_ASSESSED,
            "plan_status_input": IN_PROGRESS,
            "dependency_status_input": IN_PROGRESS,
            "usage_status_input": NOT_ASSESSED,
            "pilot_status_input": "Pilot required and complete",
            "phased_pricing_input": "Not yet",
            "decision_owner_input": "City technology and procurement leadership",
            "project_owner_input": "M365 rollout program",
            "usage_owner_input": "",
            "demand_reference_input": "Public audit, pages 8–9",
            "overage_premium_input": 10.0,
            "monthly_premium_input": 20.0,
            "quarterly_premium_input": 12.0,
            "semiannual_premium_input": 6.0,
            "annual_premium_input": 0.0,
            "true_down_premium_input": 8.0,
            "simulations_input": 500,
        }
    )
    for key in (
        "planner_result",
        "supplier_quote_editor",
        "quote_evaluations",
        "quote_plan_signature",
    ):
        st.session_state.pop(key, None)


def _build_readiness_inputs(
    demand_status: str,
    technical_status: str,
    plan_status: str,
    dependency_status: str,
    usage_status: str,
    pilot_status: str,
    phased_pricing_status: str,
    decision_owner: str,
    project_owner: str,
    usage_owner: str,
    demand_reference: str,
) -> ReadinessInputs:
    pilot_required = pilot_status != "No pilot required"
    pilot_complete = pilot_status != "Pilot required but not complete"
    return ReadinessInputs(
        demand_evidence_status=demand_status,
        technical_capacity_status=technical_status,
        implementation_plan_status=plan_status,
        critical_dependencies_status=dependency_status,
        usage_reporting_status=usage_status,
        pilot_required=pilot_required,
        pilot_complete=pilot_complete,
        phased_pricing_requested=phased_pricing_status == "Yes",
        decision_owner=decision_owner,
        project_owner=project_owner,
        usage_review_owner=usage_owner,
        demand_evidence_reference=demand_reference,
    )


def _build_inputs() -> tuple[PlannerInputs | None, bool]:
    st.subheader("Create an approval-ready buying plan")
    st.write(
        "Enter the commercial facts, then complete five evidence checks. The model can "
        "calculate a quantity even when evidence is weak; the readiness gate prevents "
        "that quantity from being mistaken for an approved purchase."
    )

    with st.form("procurement_planner_form"):
        st.markdown("#### 1. What are you buying?")
        identity_columns = st.columns(2)
        deal_name = identity_columns[0].text_input(
            "Software or project name",
            key="deal_name_input",
        )
        unit_label = identity_columns[1].text_input(
            "What does one licence unit represent?",
            key="unit_label_input",
            help="Examples: users, devices, cores, sites, or subscription equivalents.",
        )

        demand_columns = st.columns(2)
        target_units = demand_columns[0].number_input(
            "Total units required after rollout",
            min_value=1,
            step=100,
            key="target_units_input",
            help="Use the maximum credible steady-state need, not a supplier target.",
        )
        day_one_units = demand_columns[1].number_input(
            "Units that can actually be active on day one",
            min_value=0,
            step=50,
            key="day_one_units_input",
            help="Use the named first wave, not technical capacity or total population.",
        )

        price_columns = st.columns(3)
        currency = price_columns[0].selectbox(
            "Currency",
            ("CAD", "USD", "EUR", "GBP", "AUD"),
            key="currency_input",
        )
        quoted_price = price_columns[1].number_input(
            "Full-commitment price per unit",
            min_value=0.01,
            step=1.0,
            key="unit_price_input",
            help="The supplier price if the full target quantity is committed now.",
        )
        price_basis = price_columns[2].selectbox(
            "Price basis",
            PRICE_BASIS_OPTIONS,
            key="price_basis_input",
        )

        rollout_columns = st.columns(2)
        contract_months = rollout_columns[0].selectbox(
            "Contract term",
            (12, 24, 36, 48, 60),
            format_func=lambda value: f"{value} months",
            key="contract_months_input",
        )
        rollout_complete_month = rollout_columns[1].number_input(
            "Contract month when rollout should be substantially complete",
            min_value=2,
            max_value=60,
            step=1,
            key="rollout_month_input",
        )
        confidence_label = st.selectbox(
            "Confidence in the rollout dates",
            tuple(CONFIDENCE_OPTIONS),
            key="confidence_input",
        )
        risk_label = st.selectbox(
            "Planning posture",
            tuple(RISK_OPTIONS),
            key="risk_input",
        )

        st.markdown("#### 2. Can the organization approve a commitment?")
        st.caption(
            "Use Confirmed only when an accountable owner can point to evidence. "
            "These answers drive a hold/proceed gate; they do not change the simulation."
        )
        gate_columns = st.columns(2)
        demand_status = gate_columns[0].selectbox(
            "Demand: named day-one users/devices and steady-state population",
            REQUIRED_STATUS_OPTIONS,
            key="demand_status_input",
        )
        technical_status = gate_columns[1].selectbox(
            "Architecture: capacity tested for the first deployment wave",
            REQUIRED_STATUS_OPTIONS,
            key="technical_status_input",
        )
        plan_status = gate_columns[0].selectbox(
            "Delivery: approved deployment plan with dated waves and owners",
            REQUIRED_STATUS_OPTIONS,
            key="plan_status_input",
        )
        dependency_status = gate_columns[1].selectbox(
            "Dependencies: security, privacy, integration, data, and change",
            (*REQUIRED_STATUS_OPTIONS, NOT_APPLICABLE),
            key="dependency_status_input",
        )
        usage_status = gate_columns[0].selectbox(
            "Control: monthly active-usage reporting is available",
            REQUIRED_STATUS_OPTIONS,
            key="usage_status_input",
        )
        pilot_status = gate_columns[1].selectbox(
            "Pilot or proof of concept",
            (
                "No pilot required",
                "Pilot required and complete",
                "Pilot required but not complete",
            ),
            key="pilot_status_input",
        )
        phased_pricing_status = st.selectbox(
            "Have suppliers been asked to price both full and phased commitments?",
            ("Not yet", "Yes"),
            key="phased_pricing_input",
        )

        with st.expander("Recommended: record the evidence and accountable owners"):
            owner_columns = st.columns(3)
            decision_owner = owner_columns[0].text_input(
                "Decision owner",
                key="decision_owner_input",
            )
            project_owner = owner_columns[1].text_input(
                "Project or rollout owner",
                key="project_owner_input",
            )
            usage_owner = owner_columns[2].text_input(
                "Monthly usage-review owner",
                key="usage_owner_input",
            )
            demand_reference = st.text_input(
                "Demand evidence reference",
                key="demand_reference_input",
                help="Example: IAM export dated 2026-08-01 and approved wave plan v4.",
            )

        with st.expander("Optional: replace commercial assumptions with market feedback"):
            st.caption(
                "Leave these defaults for pre-market planning. After bids arrive, use the "
                "Compare offers tab to evaluate actual quoted terms."
            )
            overage_premium = st.number_input(
                "Emergency overage uplift (%)",
                min_value=0.0,
                max_value=200.0,
                step=1.0,
                key="overage_premium_input",
            )
            premium_columns = st.columns(4)
            monthly_premium = premium_columns[0].number_input(
                "Monthly review premium (%)",
                min_value=0.0,
                max_value=200.0,
                key="monthly_premium_input",
            )
            quarterly_premium = premium_columns[1].number_input(
                "3-month premium (%)",
                min_value=0.0,
                max_value=200.0,
                key="quarterly_premium_input",
            )
            semiannual_premium = premium_columns[2].number_input(
                "6-month premium (%)",
                min_value=0.0,
                max_value=200.0,
                key="semiannual_premium_input",
            )
            annual_premium = premium_columns[3].number_input(
                "Annual review premium (%)",
                min_value=0.0,
                max_value=200.0,
                key="annual_premium_input",
            )
            true_down_premium = st.number_input(
                "Additional true-down premium (%)",
                min_value=0.0,
                max_value=200.0,
                key="true_down_premium_input",
            )
            simulations = st.select_slider(
                "Planning scenarios",
                options=[250, 500, 1_000, 2_000],
                key="simulations_input",
            )

        submitted = st.form_submit_button(
            "Build approval and procurement plan",
            type="primary",
            width="stretch",
        )

    if not submitted:
        return None, False
    if day_one_units > target_units:
        st.error("Day-one units cannot exceed the steady-state requirement.")
        return None, True
    if rollout_complete_month > contract_months:
        st.error("Rollout completion must fall within the contract term.")
        return None, True

    monthly_price = quoted_price / 12 if price_basis.endswith("year") else quoted_price
    try:
        readiness = _build_readiness_inputs(
            demand_status,
            technical_status,
            plan_status,
            dependency_status,
            usage_status,
            pilot_status,
            phased_pricing_status,
            decision_owner,
            project_owner,
            usage_owner,
            demand_reference,
        )
        inputs = PlannerInputs(
            deal_name=deal_name,
            currency=currency,
            target_units=int(target_units),
            day_one_units=int(day_one_units),
            unit_price_month=float(monthly_price),
            contract_months=int(contract_months),
            rollout_complete_month=int(rollout_complete_month),
            unit_label=unit_label,
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
            readiness=readiness,
        )
    except ValueError as exc:
        st.error(str(exc))
        return None, True
    return inputs, True


def _render_readiness_gate(result: PlannerResult) -> None:
    assessment = result.readiness_assessment
    if assessment.decision == HOLD_FULL_COMMITMENT:
        st.error(
            "HOLD THE FULL COMMITMENT. The financial model is available for planning, "
            "but the current evidence does not support approval of the target quantity."
        )
    elif assessment.decision == PHASE_WITH_CONDITIONS:
        st.warning(
            "PROCEED ONLY WITH A PHASED COMMITMENT. Close the conditions below and "
            "preserve a contractual right to align billing with verified deployment."
        )
    else:
        st.success(
            "READY FOR COMMERCIAL COMPARISON. The core evidence is confirmed; compare "
            "full and phased supplier offers before approving the PO."
        )

    issue_columns = st.columns(3)
    with issue_columns[0]:
        st.markdown("**Blocking items**")
        if assessment.blockers:
            for item in assessment.blockers:
                st.write(f"• {item}")
        else:
            st.write("None identified")
    with issue_columns[1]:
        st.markdown("**Conditions before award**")
        if assessment.conditions:
            for item in assessment.conditions:
                st.write(f"• {item}")
        else:
            st.write("None identified")
    with issue_columns[2]:
        st.markdown("**Decision-record gaps**")
        if assessment.record_gaps:
            for item in assessment.record_gaps:
                st.write(f"• {item}")
        else:
            st.write("Record is complete")


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
    st.header("Decision and buying recommendation")
    _render_readiness_gate(result)

    if result.readiness_assessment.decision == HOLD_FULL_COMMITMENT:
        st.info(
            f"Conditional model output: once the blockers are closed, the modelled phased "
            f"starting point is {start_units:,} {inputs.unit_label}. Do not treat this as "
            "a current PO approval."
        )
    elif start_units >= inputs.target_units:
        st.success(
            f"Under the confirmed inputs and quoted assumptions, the model supports the "
            f"planned {inputs.target_units:,} {inputs.unit_label} at contract start."
        )
    else:
        st.success(
            f"Start with {start_units:,} {inputs.unit_label}—not the full "
            f"{inputs.target_units:,}. Review {frequency} and add units only after "
            "verified usage."
        )

    difference = baseline.risk_adjusted_cost - recommendation.risk_adjusted_cost
    metric_columns = st.columns(4)
    metric_columns[0].metric(
        "Modelled initial floor",
        f"{start_units:,}",
        f"{start_share:.1%} of steady-state need",
    )
    metric_columns[1].metric(
        "Formal quantity review",
        frequency.capitalize(),
        f"{option.buffer_pct:.0%} operating buffer",
    )
    metric_columns[2].metric(
        "P90 budget",
        _money(inputs.currency, recommendation.p90_total_cost),
        "Recommended structure",
    )
    metric_columns[3].metric(
        "Risk-adjusted difference",
        _money(inputs.currency, difference),
        "Versus full upfront commitment",
    )

    st.caption(
        "The difference is modelled commitment exposure under your assumptions. It is "
        "not realized savings and should not be booked as a benefit."
    )

    st.subheader("1. Deployment-aligned order plan")
    schedule = pd.DataFrame(procurement_schedule(result)).rename(
        columns={
            "timing": "Timing",
            "expected_active_units": f"Expected active {inputs.unit_label}",
            "planned_committed_units": f"Planned committed {inputs.unit_label}",
            "planned_change_units": "Planned change",
            "action": "Procurement action",
        }
    )
    displayed_quantity_columns = [
        f"Expected active {inputs.unit_label}",
        f"Planned committed {inputs.unit_label}",
        "Planned change",
    ]
    st.dataframe(
        schedule[["Timing", *displayed_quantity_columns, "Procurement action"]],
        width="stretch",
        hide_index=True,
        column_config={
            column: st.column_config.NumberColumn(format="%,d")
            for column in displayed_quantity_columns
        },
    )
    st.caption(
        "This is a planning calendar. Before each order, replace forecast demand with "
        "measured active usage and retain the evidence with the PO record."
    )

    months = list(range(1, inputs.contract_months + 1))
    ramp_chart = go.Figure()
    ramp_chart.add_trace(
        go.Scatter(
            x=months,
            y=recommendation.monthly_expected_demand,
            name=f"Expected active {inputs.unit_label}",
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
        title="Expected active usage and recommended commitment",
        xaxis_title="Contract month",
        yaxis_title=inputs.unit_label.capitalize(),
        legend_title_text="",
    )
    st.plotly_chart(ramp_chart, width="stretch")

    st.subheader("2. Financial decision")
    comparison = pd.DataFrame(
        [
            {
                "Buying approach": "Full upfront commitment",
                "Expected total cost": baseline.expected_total_cost,
                "P90 budget": baseline.p90_total_cost,
                "Expected unused-capacity cost": baseline.expected_unused_cost,
                "Expected utilization": baseline.expected_utilization_pct,
            },
            {
                "Buying approach": "Recommended phased structure",
                "Expected total cost": recommendation.expected_total_cost,
                "P90 budget": recommendation.p90_total_cost,
                "Expected unused-capacity cost": recommendation.expected_unused_cost,
                "Expected utilization": recommendation.expected_utilization_pct,
            },
        ]
    )
    st.dataframe(
        comparison,
        width="stretch",
        hide_index=True,
        column_config={
            column: st.column_config.NumberColumn(format=f"{inputs.currency} %,.0f")
            for column in (
                "Expected total cost",
                "P90 budget",
                "Expected unused-capacity cost",
            )
        }
        | {"Expected utilization": st.column_config.NumberColumn(format="%.1f%%")},
    )

    if result.break_even_premium is None:
        st.warning(
            "No positive flexibility premium is supported under the current assumptions. "
            "Ask for phased pricing, but do not pay more without rerunning the comparison."
        )
    else:
        ceiling_price = inputs.unit_price_month * (1 + result.break_even_premium)
        st.info(
            f"Negotiation ceiling: the phased structure retains its modelled advantage "
            f"up to {result.break_even_premium:.1%} above the full-commitment unit price "
            f"({_price(inputs.currency, ceiling_price)} per unit per month)."
        )

    st.subheader("3. Supplier pricing request")
    request_rows = supplier_pricing_request_rows(result)
    st.dataframe(pd.DataFrame(request_rows), width="stretch", hide_index=True)
    st.write(
        f"The optimizer currently assumes a {assumed_premium:.1%} premium for its selected "
        "flexibility. Replace that assumption with actual offers in the Compare offers tab."
    )

    st.subheader("4. Contract and PO controls")
    true_down_clause = (
        "Permit quantity reductions at each review, subject to the agreed floor."
        if option.allow_true_down
        else "Permit true-up at each review without retroactive repricing."
    )
    st.markdown(
        f"""
1. **Initial committed floor:** {start_units:,} {inputs.unit_label} after readiness approval.
2. **Formal review:** {frequency.capitalize()} using buyer-accessible active-usage evidence.
3. **Quantity formula:** measured active usage plus a {option.buffer_pct:.0%} buffer.
4. **Adjustment right:** {true_down_clause}
5. **Billing:** charge added units only from activation; prohibit retroactive repricing.
6. **Overage:** cap emergency units at {inputs.overage_premium_pct:.0%} above contracted price.
7. **Operational rights:** require usage reports, reassignment, pooling, and profile swaps.
8. **Delay control:** allow activation dates and volumes to move when approved project dates move.
9. **Governance:** no next-wave PO without Project, IT/Architecture,
   Procurement, and Finance sign-off.
"""
    )

    download_columns = st.columns(3)
    download_columns[0].download_button(
        "Download approval plan",
        procurement_plan_markdown(result),
        "software-commitment-decision.md",
        "text/markdown",
        width="stretch",
    )
    download_columns[1].download_button(
        "Download supplier pricing template",
        supplier_pricing_request_csv(result),
        "supplier-pricing-request.csv",
        "text/csv",
        width="stretch",
    )
    full_payload = {
        "notice": "Model output under user-controlled assumptions; not realized savings.",
        "inputs": asdict(inputs),
        "readiness_assessment": asdict(result.readiness_assessment),
        "recommended_option": option.to_dict(),
        "recommended_summary": recommendation.to_dict(),
        "full_commitment_summary": baseline.to_dict(),
        "break_even_flexibility_premium_pct": (
            None if result.break_even_premium is None else result.break_even_premium * 100
        ),
        "procurement_schedule": procurement_schedule(result),
    }
    download_columns[2].download_button(
        "Download model record",
        json.dumps(full_payload, indent=2),
        "software-commitment-model.json",
        "application/json",
        width="stretch",
    )

    with st.expander("Advanced model details"):
        st.write(
            f"The optimizer evaluated {result.optimized.candidates_evaluated} auditable "
            f"policies; {result.optimized.candidates_feasible} met the overage guardrail. "
            "CVaR is the average cost in the most expensive 10% of modelled outcomes."
        )


def _default_quote_rows(result: PlannerResult) -> pd.DataFrame:
    option = result.optimized.option
    start_units = recommended_start_units(result)
    return pd.DataFrame(
        [
            {
                "Offer": "Full commitment quote",
                "Unit price / month": result.inputs.unit_price_month,
                "Initial units": result.inputs.target_units,
                "Review months": result.inputs.contract_months,
                "True-down": False,
                "Minimum units": result.inputs.target_units,
                "Buffer %": 0.0,
                "Overage uplift %": result.inputs.overage_premium_pct * 100,
                "Annual escalation %": 0.0,
                "One-time fee": 0.0,
                "Monthly fixed fee": 0.0,
            },
            {
                "Offer": "Replace with supplier phased quote",
                "Unit price / month": (
                    result.inputs.unit_price_month * option.unit_price_multiplier
                ),
                "Initial units": start_units,
                "Review months": option.adjustment_frequency_months,
                "True-down": option.allow_true_down,
                "Minimum units": option.minimum_commitment_units,
                "Buffer %": option.buffer_pct * 100,
                "Overage uplift %": result.inputs.overage_premium_pct * 100,
                "Annual escalation %": 0.0,
                "One-time fee": 0.0,
                "Monthly fixed fee": 0.0,
            },
        ]
    )


def _quote_from_row(row: dict[str, object]) -> SupplierQuote:
    return SupplierQuote(
        offer_name=str(row["Offer"]).strip(),
        unit_price_month=float(row["Unit price / month"]),
        initial_commitment_units=int(row["Initial units"]),
        adjustment_frequency_months=int(row["Review months"]),
        allow_true_down=bool(row["True-down"]),
        minimum_commitment_units=int(row["Minimum units"]),
        buffer_pct=float(row["Buffer %"]) / 100,
        overage_premium_pct=float(row["Overage uplift %"]) / 100,
        annual_escalation_pct=float(row["Annual escalation %"]) / 100,
        one_time_fee=float(row["One-time fee"]),
        monthly_fixed_fee=float(row["Monthly fixed fee"]),
    )


def _render_quote_results(
    result: PlannerResult,
    evaluations: list[SupplierQuoteEvaluation],
) -> None:
    rows = []
    for rank, evaluation in enumerate(evaluations, start=1):
        rows.append(
            {
                "Rank": rank,
                "Offer": evaluation.quote.offer_name,
                "Initial units": evaluation.quote.initial_commitment_units,
                "Expected cost": evaluation.summary.expected_total_cost,
                "P90 budget": evaluation.summary.p90_total_cost,
                "Unused-capacity cost": evaluation.summary.expected_unused_cost,
                "Expected utilization": evaluation.summary.expected_utilization_pct,
                "Difference vs planner full baseline": (
                    evaluation.risk_adjusted_difference_vs_full_commitment
                ),
            }
        )
    frame = pd.DataFrame(rows)
    st.success(
        f"Lowest modelled risk-adjusted cost: {evaluations[0].quote.offer_name}. "
        "Confirm that every compared offer is technically and contractually compliant."
    )
    st.dataframe(
        frame,
        width="stretch",
        hide_index=True,
        column_config={
            column: st.column_config.NumberColumn(format=f"{result.inputs.currency} %,.0f")
            for column in (
                "Expected cost",
                "P90 budget",
                "Unused-capacity cost",
                "Difference vs planner full baseline",
            )
        }
        | {"Expected utilization": st.column_config.NumberColumn(format="%.1f%%")},
    )
    st.caption(
        "The difference column uses the full-upfront baseline from Plan & approve. "
        "Expected cost and P90 compare the supplier offers directly. Rebuild the plan "
        "if the baseline price or scope changes."
    )
    st.download_button(
        "Download offer comparison",
        frame.to_csv(index=False),
        "supplier-offer-comparison.csv",
        "text/csv",
    )


def _render_quote_comparison() -> None:
    st.header("Compare actual supplier offers")
    result = st.session_state.get("planner_result")
    if not isinstance(result, PlannerResult):
        st.info("Build a procurement plan first. The offers must use the same demand scenarios.")
        return

    st.write(
        "Replace the example rows with compliant supplier offers. All offers are evaluated "
        "against the exact same seeded demand scenarios, so a lower unit price cannot hide "
        "a costly upfront quantity obligation."
    )
    st.warning(
        "Use non-confidential or masked pricing on a public deployment. For live commercial "
        "data, run the app in your organization's controlled environment."
    )

    signature = (
        result.inputs.target_units,
        result.inputs.unit_price_month,
        result.inputs.contract_months,
    )
    if st.session_state.get("quote_plan_signature") != signature:
        st.session_state.pop("supplier_quote_editor", None)
        st.session_state["quote_plan_signature"] = signature

    with st.form("supplier_quote_form"):
        edited = st.data_editor(
            _default_quote_rows(result),
            num_rows="dynamic",
            width="stretch",
            hide_index=True,
            key="supplier_quote_editor",
        )
        submitted = st.form_submit_button(
            "Compare supplier offers",
            type="primary",
            width="stretch",
        )

    if submitted:
        try:
            quotes = [
                _quote_from_row(row)
                for row in edited.to_dict(orient="records")
                if str(row.get("Offer", "")).strip()
            ]
            st.session_state["quote_evaluations"] = evaluate_supplier_quotes(
                result,
                quotes,
            )
        except (TypeError, ValueError) as exc:
            st.error(f"The offers could not be compared: {exc}")

    evaluations = st.session_state.get("quote_evaluations")
    if isinstance(evaluations, list) and evaluations:
        _render_quote_results(result, evaluations)


def _usage_review_markdown(
    snapshot: UsageSnapshot,
    result: UsageReviewResult,
    currency: str,
) -> str:
    actions = "\n".join(f"- {item}" for item in result.follow_up_actions)
    return f"""# Software licence usage review

## Decision

**{result.status}**

{result.primary_action}

## Evidence snapshot

- Committed units: {snapshot.committed_units:,}
- Active units: {snapshot.active_units:,}
- Assigned but inactive: {snapshot.assigned_but_inactive_units:,}
- Utilization: {result.utilization_pct:.1f}%
- Current unused cost per month: {_money(currency, result.current_unused_cost_month)}
- Annualized unused-cost exposure: {_money(currency, result.annualized_unused_cost_exposure)}
- Recommended commitment: {result.recommended_commitment_units:,}

## Actions

{actions}
"""


def _render_usage_review() -> None:
    st.header("Run the recurring licence usage review")
    st.write(
        "Use this after award—monthly for material SaaS agreements and before every true-up, "
        "renewal, or additional PO. It converts usage evidence into an immediate contract action."
    )

    with st.form("usage_review_form"):
        quantity_columns = st.columns(3)
        committed = quantity_columns[0].number_input(
            "Units currently paid or committed",
            min_value=0,
            step=50,
            key="usage_committed_input",
        )
        active = quantity_columns[1].number_input(
            "Actively used units",
            min_value=0,
            step=50,
            key="usage_active_input",
        )
        inactive = quantity_columns[2].number_input(
            "Assigned but inactive units",
            min_value=0,
            step=10,
            key="usage_inactive_input",
        )
        commercial_columns = st.columns(3)
        unit_price = commercial_columns[0].number_input(
            "Price per unit per month",
            min_value=0.01,
            key="usage_price_input",
        )
        buffer_pct = commercial_columns[1].number_input(
            "Operating buffer (%)",
            min_value=0.0,
            max_value=100.0,
            key="usage_buffer_input",
        )
        true_down = commercial_columns[2].checkbox(
            "Contract permits true-down",
            key="usage_true_down_input",
        )
        submitted = st.form_submit_button(
            "Generate usage-review action",
            type="primary",
            width="stretch",
        )

    if submitted:
        try:
            snapshot = UsageSnapshot(
                committed_units=int(committed),
                active_units=int(active),
                assigned_but_inactive_units=int(inactive),
                unit_price_month=float(unit_price),
                buffer_pct=float(buffer_pct) / 100,
                true_down_allowed=bool(true_down),
            )
            st.session_state["usage_snapshot"] = snapshot
            st.session_state["usage_result"] = review_usage(snapshot)
        except ValueError as exc:
            st.error(str(exc))

    snapshot = st.session_state.get("usage_snapshot")
    result = st.session_state.get("usage_result")
    if not isinstance(snapshot, UsageSnapshot) or not isinstance(result, UsageReviewResult):
        return

    st.subheader(result.status)
    st.success(result.primary_action)
    metrics = st.columns(4)
    metrics[0].metric("Utilization", f"{result.utilization_pct:.1f}%")
    metrics[1].metric("Unused units", f"{result.unused_units:,}")
    metrics[2].metric(
        "Unused cost / month",
        _money(st.session_state.get("currency_input", "CAD"), result.current_unused_cost_month),
    )
    metrics[3].metric(
        "Annualized exposure",
        _money(
            st.session_state.get("currency_input", "CAD"),
            result.annualized_unused_cost_exposure,
        ),
    )
    st.markdown("**Required actions**")
    for action in result.follow_up_actions:
        st.write(f"• {action}")
    currency = st.session_state.get("currency_input", "CAD")
    st.download_button(
        "Download usage-review record",
        _usage_review_markdown(snapshot, result, currency),
        "software-licence-usage-review.md",
        "text/markdown",
    )


def _render_toronto_case() -> None:
    case = load_case(CASE_PATH)
    counterfactual = case.counterfactual
    st.header("City of Toronto: what this control would have changed")
    st.write(
        "The public audit provides unusually clear evidence of the failure mode: the "
        "quantity commitment was made before the deployment architecture was ready."
    )

    known_columns = st.columns(3)
    known_columns[0].metric(
        "Contracted users",
        f"{counterfactual['contracted_users']:,}",
        "30,000 subscription equivalents",
    )
    known_columns[1].metric(
        "Known network capacity",
        f"{counterfactual['known_network_capacity_users']:,} users",
        "Architecture review was still needed",
    )
    known_columns[2].metric(
        "Annual initial subscription",
        "CAD 5.14M",
        "Five-year commitment: CAD 25.7M",
    )

    st.subheader("The decision the improved tool would produce")
    decision_rows = [
        {
            "Evidence available before commitment": (
                "Network was estimated to support only 6,000 users; architecture "
                "scalability review was still required."
            ),
            "Tool control": "Technical-capacity readiness gate",
            "Practical decision": "Hold a 10,000-user full commitment.",
        },
        {
            "Evidence available before commitment": (
                "The purchase was justified partly by an upfront volume discount."
            ),
            "Tool control": "Mandatory full-versus-phased supplier pricing table",
            "Practical decision": (
                "Evaluate the discount against unused-capacity exposure, not unit price alone."
            ),
        },
        {
            "Evidence available before commitment": (
                "Deployment depended on architecture, staffing, and rollout timing."
            ),
            "Tool control": "Dated activation gates and usage-based next-wave POs",
            "Practical decision": "Buy the verified first wave, then activate by evidence.",
        },
        {
            "Evidence available before commitment": "Usage could be reconciled after award.",
            "Tool control": "Monthly licence reconciliation",
            "Practical decision": "Reclaim, reassign, and stop excess net-new purchases.",
        },
    ]
    st.dataframe(pd.DataFrame(decision_rows), width="stretch", hide_index=True)

    st.subheader("Retrospective boundary—not a savings claim")
    premium_pct = st.slider(
        "Illustrative premium for usage-aligned phased billing",
        min_value=0,
        max_value=200,
        value=15,
        step=5,
        format="%d%%",
    )
    retrospective = usage_aligned_counterfactual(
        float(counterfactual["examined_subscription_spend"]),
        float(counterfactual["reported_unused_cost"]),
        premium_pct / 100,
    )
    outcome_columns = st.columns(4)
    outcome_columns[0].metric(
        "Spend examined by audit",
        _money("CAD", retrospective.examined_spend),
        "Year 1 plus first 9 months of Year 2",
    )
    outcome_columns[1].metric(
        "Audit-reported unused cost",
        _money("CAD", retrospective.reported_unused_cost),
    )
    outcome_columns[2].metric(
        f"Usage-aligned proxy at +{premium_pct}%",
        _money("CAD", retrospective.phased_cost_proxy),
    )
    outcome_columns[3].metric(
        "Upper-bound difference",
        _money("CAD", retrospective.modelled_difference),
        "Not realized or guaranteed savings",
    )

    discount_gap = float(counterfactual["reported_unused_cost"]) - float(
        counterfactual["reported_five_year_bulk_discount"]
    )
    st.info(
        f"The audit reported CAD {counterfactual['reported_unused_cost']:,.0f} of unused "
        f"M365 subscription cost in the examined 21 months. Management's reported bulk "
        f"discount over the five-year term was approximately CAD "
        f"{counterfactual['reported_five_year_bulk_discount']:,.0f}. The early unused "
        f"cost exceeded that stated discount by about CAD {discount_gap:,.0f}."
    )
    st.warning(
        "The tool could not have guaranteed avoidance. The exact deployment path, supplier "
        "concessions, bundle value, and contract constraints were not public. If the gate "
        "had been completed honestly and enforced, however, it would have prevented an "
        "unqualified full-volume approval and required a documented exception or phased offer."
    )

    for source in case.sources:
        st.markdown(f"- [{source['title']}]({source['url']})")
    st.button(
        "Load the public Toronto quantities into the planner",
        on_click=_load_toronto_example,
    )


def _render_guide() -> None:
    st.header("Operating guide")
    workflow = pd.DataFrame(
        [
            {
                "Stage": "1. Intake",
                "Owner": "Procurement + business owner",
                "Evidence": "Licence metric, population, demand source, contract dates",
                "Output": "Validated decision record",
            },
            {
                "Stage": "2. Readiness gate",
                "Owner": "Project, architecture, security/privacy",
                "Evidence": "Wave plan, capacity test, cleared dependencies, POC",
                "Output": "Hold / phased / ready decision",
            },
            {
                "Stage": "3. Sourcing",
                "Owner": "Procurement + finance",
                "Evidence": "Comparable full and phased supplier offers",
                "Output": "Ranked TCO and P90 budget",
            },
            {
                "Stage": "4. Contract and PO",
                "Owner": "Procurement + legal + finance",
                "Evidence": "Activation schedule, adjustment formula, rights, approvals",
                "Output": "Controlled initial PO and order-form terms",
            },
            {
                "Stage": "5. Monthly control",
                "Owner": "SAM/ITAM + application owner",
                "Evidence": "Active use, inactive assignments, leavers, committed units",
                "Output": "Reclaim, true-up, true-down, or freeze action",
            },
        ]
    )
    st.dataframe(workflow, width="stretch", hide_index=True)

    st.subheader("What the tool is—and is not")
    st.write(
        "This release is an analyst-grade decision and control workflow. It can be used in "
        "a sourcing project today, especially when run internally and attached to the "
        "procurement record. It is not yet a multi-user enterprise system."
    )
    st.markdown(
        """
For production-wide deployment, an organization should add:

- single sign-on and role-based access;
- encrypted persistent storage and retention controls;
- integrations with IAM, HR, ITAM/SAM, ERP/PO, and vendor usage APIs;
- approval workflow, immutable audit history, and notification scheduling;
- SKU/bundle-level entitlement logic, taxes, FX, and accounting treatment; and
- organization-specific policies, risk thresholds, and legal clauses.
"""
    )
    st.warning(
        "Do not enter confidential supplier pricing into a public Streamlit deployment. "
        "Use masked values or deploy the repository inside the organization's environment."
    )


def main() -> None:
    st.set_page_config(
        page_title="Software Licence Commitment Planner",
        page_icon="🧭",
        layout="wide",
    )
    _set_generic_defaults()

    st.title("Software Licence Commitment Planner")
    st.caption("Plan the commitment • compare supplier structures • control post-award usage")
    planner_tab, quotes_tab, usage_tab, toronto_tab, guide_tab = st.tabs(
        [
            "1. Plan & approve",
            "2. Compare offers",
            "3. Review usage",
            "Toronto evidence",
            "Operating guide",
        ]
    )

    with planner_tab:
        inputs, submitted = _build_inputs()
        if submitted and inputs is not None:
            try:
                with st.spinner("Testing commitment structures and building the control plan…"):
                    st.session_state["planner_result"] = run_procurement_plan(inputs)
                st.session_state.pop("quote_evaluations", None)
            except (RuntimeError, TypeError, ValueError) as exc:
                st.error(f"The plan could not be generated: {exc}")
        result = st.session_state.get("planner_result")
        if isinstance(result, PlannerResult):
            _render_recommendation(result)
        elif not submitted:
            st.caption(
                "Complete the facts and evidence checks, then select "
                "**Build approval and procurement plan**."
            )

    with quotes_tab:
        _render_quote_comparison()

    with usage_tab:
        _render_usage_review()

    with toronto_tab:
        _render_toronto_case()

    with guide_tab:
        _render_guide()
