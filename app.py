"""Interactive Streamlit dashboard for the commitment optimizer."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from commitment_optimizer.analysis import find_break_even_premium
from commitment_optimizer.case_loader import CaseStudy, load_case
from commitment_optimizer.forecast import generate_demand_scenarios
from commitment_optimizer.models import CommercialOption, PriceTier
from commitment_optimizer.optimizer import OptimizationResult, optimize_policy
from commitment_optimizer.reporting import monthly_rows, summary_rows
from commitment_optimizer.simulation import compare_options

ROOT = Path(__file__).resolve().parent
CASE_PATH = ROOT / "case_studies" / "toronto" / "toronto_m365.json"


def _option_editor_rows(case: CaseStudy) -> pd.DataFrame:
    rows = []
    for option in case.commercial_options:
        rows.append(
            {
                "Option": option.name,
                "Base price / unit / month": option.price_tiers[0].unit_price_month,
                "Price multiplier": option.unit_price_multiplier,
                "Initial commitment %": option.initial_commitment_pct * 100,
                "Review months": option.adjustment_frequency_months,
                "True-down": option.allow_true_down,
                "Minimum units": option.minimum_commitment_units,
                "Buffer %": option.buffer_pct * 100,
                "Overage multiplier": option.overage_multiplier,
                "Annual escalation %": option.annual_escalation_pct * 100,
                "One-time fee": option.one_time_fee,
                "Monthly fixed fee": option.monthly_fixed_fee,
            }
        )
    return pd.DataFrame(rows)


def _options_from_editor(frame: pd.DataFrame, case: CaseStudy) -> tuple[CommercialOption, ...]:
    original = {option.name: option for option in case.commercial_options}
    options = []
    for row in frame.to_dict(orient="records"):
        name = str(row["Option"]).strip()
        source = original.get(name)
        options.append(
            CommercialOption(
                name=name,
                price_tiers=(
                    PriceTier(0, float(row["Base price / unit / month"])),
                ),
                initial_commitment_pct=float(row["Initial commitment %"]) / 100,
                adjustment_frequency_months=int(row["Review months"]),
                allow_true_down=bool(row["True-down"]),
                minimum_commitment_units=int(row["Minimum units"]),
                buffer_pct=float(row["Buffer %"]) / 100,
                overage_multiplier=float(row["Overage multiplier"]),
                one_time_fee=float(row["One-time fee"]),
                monthly_fixed_fee=float(row["Monthly fixed fee"]),
                annual_escalation_pct=float(row["Annual escalation %"]) / 100,
                unit_price_multiplier=float(row["Price multiplier"]),
                description=source.description if source else "User-entered scenario",
                evidence_class=(source.evidence_class if source else "user_entered"),
            )
        )
    return tuple(options)


def _run_analysis(
    case: CaseStudy,
    options: tuple[CommercialOption, ...],
    forecast_updates: dict[str, float | int],
    risk_aversion: float,
    max_overage_share: float,
    frequency_premium_pct: dict[int, float],
    true_down_premium_pct: float,
) -> tuple[list, OptimizationResult, float | None]:
    forecast = replace(case.forecast, **forecast_updates)
    scenarios = generate_demand_scenarios(forecast)
    optimization_template = replace(
        case.optimization_template,
        price_tiers=options[0].price_tiers,
        overage_multiplier=options[0].overage_multiplier,
        one_time_fee=options[0].one_time_fee,
        monthly_fixed_fee=options[0].monthly_fixed_fee,
        annual_escalation_pct=options[0].annual_escalation_pct,
    )
    config = replace(
        case.optimization,
        risk_aversion=risk_aversion,
        max_expected_overage_share=max_overage_share,
        frequency_premium_pct=frequency_premium_pct,
        true_down_premium_pct=true_down_premium_pct,
    )
    summaries = compare_options(
        scenarios,
        options,
        forecast.target_units,
        risk_aversion=risk_aversion,
        cvar_confidence=case.optimization.cvar_confidence,
    )
    optimized = optimize_policy(
        scenarios,
        optimization_template,
        forecast.target_units,
        config,
    )
    summaries = sorted(
        summaries + [optimized.summary],
        key=lambda item: item.risk_adjusted_cost,
    )
    unpriced_flexibility = replace(
        optimized.option,
        unit_price_multiplier=optimization_template.unit_price_multiplier,
    )
    premium = find_break_even_premium(
        scenarios,
        options[0],
        unpriced_flexibility,
        forecast.target_units,
        risk_aversion=risk_aversion,
        cvar_confidence=case.optimization.cvar_confidence,
    )
    return summaries, optimized, premium


def _currency(value: float) -> str:
    return f"${value:,.0f}"


def main() -> None:
    st.set_page_config(
        page_title="Software Commitment & Ramp Optimizer",
        page_icon="📈",
        layout="wide",
    )
    case = load_case(CASE_PATH)

    st.title("Software Commitment & Ramp Optimizer")
    st.caption(
        "Pre-award decision support for comparing upfront commitments, staged ramps, "
        "and negotiated flexibility under uncertain software adoption."
    )
    st.warning(
        "Evidence boundary: the Toronto audit figures below are public facts. Rollout "
        "distributions and alternative commercial terms are explicit modelling "
        "assumptions—not disclosed Toronto or Microsoft offers."
    )

    with st.sidebar:
        st.header("Forecast and risk")
        simulations = st.select_slider(
            "Monte Carlo scenarios",
            options=[250, 500, 1_000, 2_000],
            value=500,
            help="Use 2,000 to reproduce the publication run; smaller values respond faster.",
        )
        midpoint = st.slider(
            "Expected rollout midpoint (month)",
            3.0,
            30.0,
            float(case.forecast.midpoint_month),
            0.5,
        )
        growth = st.slider(
            "Adoption speed",
            0.10,
            0.80,
            float(case.forecast.growth_rate),
            0.01,
        )
        delay_probability = st.slider(
            "Chance of material delay",
            0,
            100,
            int(case.forecast.delay_probability * 100),
            5,
        )
        target_volatility = st.slider(
            "Final demand uncertainty",
            0,
            40,
            int(case.forecast.target_volatility_pct * 100),
            1,
        )
        growth_volatility = st.slider(
            "Adoption-speed uncertainty",
            0,
            40,
            int(case.forecast.growth_volatility_pct * 100),
            1,
        )
        risk_aversion = st.slider(
            "Tail-risk weight",
            0.0,
            1.0,
            float(case.optimization.risk_aversion),
            0.05,
            help="Adds a share of the CVaR-to-expected-cost gap to the objective.",
        )
        max_overage = st.slider(
            "Maximum expected overage share",
            0,
            50,
            int((case.optimization.max_expected_overage_share or 0) * 100),
            1,
            help="Rejects optimizer candidates that rely excessively on emergency usage.",
        )
        with st.expander("Negotiation premiums"):
            st.caption(
                "Illustrative additions to the base unit price. Replace them with bids."
            )
            monthly_premium = st.number_input(
                "Monthly review premium %",
                0.0,
                200.0,
                case.optimization.frequency_premium_pct.get(1, 0) * 100,
                1.0,
            )
            quarterly_premium = st.number_input(
                "Quarterly review premium %",
                0.0,
                200.0,
                case.optimization.frequency_premium_pct.get(3, 0) * 100,
                1.0,
            )
            semiannual_premium = st.number_input(
                "Six-month review premium %",
                0.0,
                200.0,
                case.optimization.frequency_premium_pct.get(6, 0) * 100,
                1.0,
            )
            annual_premium = st.number_input(
                "Annual review premium %",
                0.0,
                200.0,
                case.optimization.frequency_premium_pct.get(12, 0) * 100,
                1.0,
            )
            true_down_premium = st.number_input(
                "Additional true-down premium %",
                0.0,
                200.0,
                case.optimization.true_down_premium_pct * 100,
                1.0,
            )

    facts_tab, model_tab, method_tab = st.tabs(
        ["Published evidence", "Model and results", "How to interpret"]
    )

    with facts_tab:
        st.subheader(case.title)
        st.write(case.decision_question)
        facts = pd.DataFrame(case.published_facts)
        st.dataframe(
            facts[["fact", "value", "unit", "source_page"]],
            width="stretch",
            hide_index=True,
        )
        for source in case.sources:
            st.markdown(f"- [{source['title']}]({source['url']})")
        st.info(case.simulation_notice)

    with model_tab:
        st.subheader("1. Edit the commercial scenarios")
        st.write(
            "All price multipliers, commitment floors, review rights, buffers, and fees "
            "are editable. Keep the first row as the locked baseline for the break-even test."
        )
        edited = st.data_editor(
            _option_editor_rows(case),
            width="stretch",
            hide_index=True,
            disabled=["Option"],
            key="commercial_options",
        )
        run = st.button("Run risk-adjusted comparison", type="primary")

        forecast_updates = {
            "simulations": simulations,
            "midpoint_month": midpoint,
            "growth_rate": growth,
            "delay_probability": delay_probability / 100,
            "target_volatility_pct": target_volatility / 100,
            "growth_volatility_pct": growth_volatility / 100,
        }
        frequency_premiums = {
            1: monthly_premium / 100,
            3: quarterly_premium / 100,
            6: semiannual_premium / 100,
            12: annual_premium / 100,
        }
        current_inputs = {
            "forecast": forecast_updates,
            "risk_aversion": risk_aversion,
            "max_expected_overage_share": max_overage / 100,
            "frequency_premium_pct": frequency_premiums,
            "true_down_premium_pct": true_down_premium / 100,
            "commercial_options": json.loads(edited.to_json(orient="records")),
        }
        current_signature = json.dumps(current_inputs, sort_keys=True)

        if run or "analysis_result" not in st.session_state:
            try:
                options = _options_from_editor(edited, case)
                with st.spinner("Generating adoption paths and testing negotiation policies…"):
                    result = _run_analysis(
                        case,
                        options,
                        forecast_updates,
                        risk_aversion,
                        max_overage / 100,
                        frequency_premiums,
                        true_down_premium / 100,
                    )
                st.session_state["analysis_result"] = result
                st.session_state["analysis_inputs"] = current_inputs
                st.session_state["analysis_signature"] = current_signature
            except (ValueError, RuntimeError) as exc:
                st.error(f"The model could not run: {exc}")
                st.stop()
        elif st.session_state.get("analysis_signature") != current_signature:
            st.info(
                "Inputs have changed. The results below still reflect the last run; "
                "select **Run risk-adjusted comparison** to refresh them."
            )

        summaries, optimized, premium = st.session_state["analysis_result"]
        baseline = next(
            item
            for item in summaries
            if item.option_name == case.commercial_options[0].name
        )
        lowest = summaries[0]
        modelled_difference = baseline.risk_adjusted_cost - lowest.risk_adjusted_cost

        st.subheader("2. Compare the outcomes")
        metric_columns = st.columns(4)
        metric_columns[0].metric(
            "Lowest risk-adjusted scenario",
            lowest.option_name,
        )
        metric_columns[1].metric(
            "Risk-adjusted cost",
            _currency(lowest.risk_adjusted_cost),
        )
        metric_columns[2].metric(
            "Difference vs locked proxy",
            _currency(modelled_difference),
            help="A simulated difference under assumptions—not realized savings.",
        )
        metric_columns[3].metric(
            "Break-even flexibility premium",
            "Not positive" if premium is None else f"{premium:.1%}",
            help=(
                "Maximum modelled price premium before the optimized structure "
                "loses its risk-adjusted advantage."
            ),
        )

        result_frame = pd.DataFrame(summary_rows(summaries))
        display = result_frame.rename(
            columns={
                "option": "Option",
                "expected_total_cost": "Expected cost",
                "p90_total_cost": "P90 cost",
                "cvar_total_cost": "CVaR cost",
                "risk_adjusted_cost": "Risk-adjusted cost",
                "expected_unused_cost": "Expected unused cost",
                "expected_overage_cost": "Expected overage cost",
                "expected_utilization_pct": "Utilization %",
                "expected_overage_share_pct": "Overage share %",
            }
        )
        st.dataframe(
            display[
                [
                    "Option",
                    "Expected cost",
                    "P90 cost",
                    "CVaR cost",
                    "Risk-adjusted cost",
                    "Expected unused cost",
                    "Expected overage cost",
                    "Utilization %",
                    "Overage share %",
                ]
            ],
            width="stretch",
            hide_index=True,
            column_config={
                column: st.column_config.NumberColumn(format="$%,.0f")
                for column in [
                    "Expected cost",
                    "P90 cost",
                    "CVaR cost",
                    "Risk-adjusted cost",
                    "Expected unused cost",
                    "Expected overage cost",
                ]
            },
        )

        chart_frame = display.melt(
            id_vars="Option",
            value_vars=["Expected cost", "P90 cost", "Risk-adjusted cost"],
            var_name="Measure",
            value_name="Cost",
        )
        cost_chart = px.bar(
            chart_frame,
            x="Option",
            y="Cost",
            color="Measure",
            barmode="group",
            title="Expected and tail-risk cost by commercial structure",
            color_discrete_sequence=["#2F5D62", "#D08C60", "#5E548E"],
        )
        cost_chart.update_layout(yaxis_tickprefix="$", yaxis_tickformat=",.0f")
        st.plotly_chart(cost_chart, width="stretch")

        selected = st.selectbox(
            "Commitment profile to inspect",
            [item.option_name for item in summaries],
        )
        profile = next(item for item in summaries if item.option_name == selected)
        months = list(range(1, len(profile.monthly_expected_demand) + 1))
        ramp_chart = go.Figure()
        ramp_chart.add_trace(
            go.Scatter(
                x=months,
                y=profile.monthly_expected_demand,
                name="Expected active demand",
                line={"color": "#2F5D62", "width": 3},
            )
        )
        ramp_chart.add_trace(
            go.Scatter(
                x=months,
                y=profile.monthly_expected_commitment,
                name="Expected committed capacity",
                line={"color": "#D08C60", "width": 3, "dash": "dash"},
            )
        )
        ramp_chart.update_layout(
            title=f"Demand and commitment ramp: {selected}",
            xaxis_title="Contract month",
            yaxis_title="Licence-equivalent units",
        )
        st.plotly_chart(ramp_chart, width="stretch")

        st.caption(
            f"Optimizer evaluated {optimized.candidates_evaluated} candidates; "
            f"{optimized.candidates_feasible} met the overage guardrail. The selected "
            "policy is a negotiation scenario, not evidence that a supplier offered it."
        )

        export_columns = st.columns(3)
        export_columns[0].download_button(
            "Download option summary",
            result_frame.to_csv(index=False),
            "option_summary.csv",
            "text/csv",
        )
        export_columns[1].download_button(
            "Download monthly profiles",
            pd.DataFrame(monthly_rows(summaries)).to_csv(index=False),
            "monthly_profile.csv",
            "text/csv",
        )
        export_payload = {
            "notice": "Model outputs under user-controlled assumptions; not realized savings.",
            "inputs": st.session_state.get("analysis_inputs", {}),
            "summaries": [item.to_dict() for item in summaries],
            "optimized_option": optimized.option.to_dict(),
            "break_even_premium_pct": None if premium is None else premium * 100,
        }
        export_columns[2].download_button(
            "Download full analysis",
            json.dumps(export_payload, indent=2),
            "analysis.json",
            "application/json",
        )

    with method_tab:
        st.subheader("Read the result as a sourcing boundary, not a forecast promise")
        st.markdown(
            """
1. **Demand engine:** creates monotonic adoption paths and varies rollout delay,
   final demand, and adoption speed.
2. **Commercial engine:** calculates committed capacity, unused capacity, emergency
   overage, escalation, and fees month by month.
3. **Risk engine:** reports expected cost, P90, and conditional value at risk (CVaR).
4. **Policy search:** tests an explicit grid of initial commitment, review cadence,
   buffer, and true-down combinations, with configurable flexibility premiums.
5. **Feasibility guardrail:** rejects candidates that source too much consumption as
   emergency overage.
6. **Break-even test:** tells the buyer how much extra unit price the flexible structure
   could absorb before losing its modeled advantage.

The model cannot know confidential bundle value, supplier approval thresholds,
implementation dependencies, security constraints, or future demand. Those belong in
the sourcing team's negotiation memo alongside—not inside—the numerical output.
"""
        )


if __name__ == "__main__":
    main()
