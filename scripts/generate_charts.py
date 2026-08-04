"""Generate publication charts from checked-in evidence and model outputs."""

from __future__ import annotations

import textwrap
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "outputs" / "toronto_m365"
IMAGES = ROOT / "docs" / "images"
FACTS = ROOT / "case_studies" / "toronto" / "audit_facts.csv"

COLORS = {
    "ink": "#243238",
    "teal": "#2F5D62",
    "sand": "#D08C60",
    "purple": "#5E548E",
    "grey": "#A8B0B3",
    "light": "#E8ECEC",
}


def _style() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "axes.titlesize": 15,
            "axes.titleweight": "bold",
            "axes.labelcolor": COLORS["ink"],
            "axes.edgecolor": COLORS["grey"],
            "xtick.color": COLORS["ink"],
            "ytick.color": COLORS["ink"],
            "text.color": COLORS["ink"],
            "figure.facecolor": "white",
            "axes.facecolor": "white",
        }
    )


def _money_millions(value: float) -> str:
    return f"${value / 1_000_000:.1f}M"


def option_cost_chart() -> None:
    frame = pd.read_csv(OUTPUT / "option_summary.csv")
    frame = frame.sort_values("risk_adjusted_cost")
    labels = [textwrap.fill(value, 24) for value in frame["option"]]
    x = np.arange(len(frame))
    width = 0.34

    fig, ax = plt.subplots(figsize=(9, 5.5))
    expected = ax.bar(
        x - width / 2,
        frame["expected_total_cost"] / 1_000_000,
        width,
        label="Expected cost",
        color=COLORS["teal"],
    )
    risk = ax.bar(
        x + width / 2,
        frame["risk_adjusted_cost"] / 1_000_000,
        width,
        label="Risk-adjusted cost",
        color=COLORS["sand"],
    )
    ax.bar_label(expected, fmt="$%.1fM", padding=3, fontsize=9)
    ax.bar_label(risk, fmt="$%.1fM", padding=3, fontsize=9)
    ax.set_title("Modelled 36-month cost under the Toronto scenario")
    ax.set_ylabel("CAD millions")
    ax.set_xticks(x, labels)
    ax.set_ylim(0, max(frame["risk_adjusted_cost"] / 1_000_000) * 1.18)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color=COLORS["light"], linewidth=0.8)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, ncol=2, loc="upper left")
    fig.text(
        0.01,
        0.01,
        "Model outputs under documented assumptions; not realized savings or vendor offers.",
        fontsize=8.5,
        color="#59666B",
    )
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(IMAGES / "option_cost_comparison.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def commitment_ramp_chart() -> None:
    frame = pd.read_csv(OUTPUT / "monthly_profile.csv")
    optimized_name = next(
        name for name in frame["option"].unique() if name.startswith("Optimized:")
    )
    choices = [
        "Published upfront commitment proxy",
        "Illustrative quarterly ramp",
        optimized_name,
    ]
    titles = ["Upfront proxy", "Quarterly ramp", "Optimized policy"]

    fig, axes = plt.subplots(3, 1, figsize=(9, 8.2), sharex=True, sharey=True)
    for ax, option, title in zip(axes, choices, titles, strict=True):
        subset = frame[frame["option"] == option]
        ax.plot(
            subset["month"],
            subset["expected_demand"],
            color=COLORS["teal"],
            linewidth=2.5,
            label="Expected active demand",
        )
        ax.step(
            subset["month"],
            subset["expected_commitment"],
            where="post",
            color=COLORS["sand"],
            linewidth=2.2,
            label="Expected commitment",
        )
        ax.fill_between(
            subset["month"],
            subset["expected_demand"],
            subset["expected_commitment"],
            where=(
                subset["expected_commitment"].to_numpy() >= subset["expected_demand"].to_numpy()
            ),
            color=COLORS["sand"],
            alpha=0.13,
        )
        ax.set_title(title, loc="left", fontsize=11)
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", color=COLORS["light"], linewidth=0.8)
        ax.set_axisbelow(True)
        ax.set_ylabel("Units")
    axes[0].legend(frameon=False, ncol=2, loc="upper left")
    axes[-1].set_xlabel("Contract month")
    fig.suptitle(
        "Expected demand versus committed licence capacity",
        y=0.99,
        fontsize=15,
        fontweight="bold",
    )
    fig.text(
        0.01,
        0.005,
        "Shaded area indicates expected commitment above active demand. "
        "Scenario assumptions are illustrative.",
        fontsize=8.5,
        color="#59666B",
    )
    fig.tight_layout(rect=(0, 0.035, 1, 0.97))
    fig.savefig(IMAGES / "monthly_ramp_comparison.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def published_evidence_chart() -> None:
    frame = pd.read_csv(FACTS)
    frame = frame[frame["published_unused_cost_cad"].notna()].copy()
    labels = [
        "M365\nYear 1",
        "M365\n9 months",
        "SAP S/4HANA\n16-month delay",
        "ForgeRock\nSept. 2024",
        "ForgeRock\ncumulative to 2026",
    ]
    values = frame["published_unused_cost_cad"].astype(float).to_numpy()

    fig, ax = plt.subplots(figsize=(9, 5.2))
    bars = ax.barh(
        np.arange(len(values)),
        values / 1_000_000,
        color=[COLORS["teal"], COLORS["teal"], COLORS["purple"], COLORS["sand"], COLORS["sand"]],
    )
    ax.set_yticks(np.arange(len(labels)), labels)
    ax.invert_yaxis()
    ax.set_xlabel("Published unused cost (CAD millions)")
    ax.set_title("Toronto audits documented material software under-use")
    ax.bar_label(
        bars,
        labels=[_money_millions(value) for value in values],
        padding=4,
        fontsize=9,
    )
    ax.set_xlim(0, max(values / 1_000_000) * 1.25)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.grid(axis="x", color=COLORS["light"], linewidth=0.8)
    ax.set_axisbelow(True)
    fig.text(
        0.01,
        0.005,
        "Periods and scopes differ; bars must not be summed or treated as directly "
        "comparable. Source: City of Toronto Auditor General.",
        fontsize=8.3,
        color="#59666B",
    )
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(IMAGES / "toronto_published_unused_costs.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    IMAGES.mkdir(parents=True, exist_ok=True)
    _style()
    option_cost_chart()
    commitment_ramp_chart()
    published_evidence_chart()
    print(f"Wrote charts to {IMAGES}")


if __name__ == "__main__":
    main()
