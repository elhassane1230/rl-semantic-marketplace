"""Plot the learning curves: how agreement rate, welfare and the surplus split
evolve as the agents learn over training episodes."""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from .simulation import learning_curve  # noqa: E402


def plot_learning(records, out_path: str | Path, window: int = 300) -> Path:
    lc = learning_curve(records, window=window)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    ax1.plot(lc["episodes"], lc["agreement_rate"], color="#2ecc71", marker="o", ms=3)
    ax1.set_title("Agreement rate over training")
    ax1.set_xlabel("matched episodes")
    ax1.set_ylabel("deals / matched episodes")
    ax1.set_ylim(0, 1.02)
    ax1.grid(alpha=0.3)

    ax2.plot(lc["episodes"], lc["welfare"], label="total welfare", color="#34495e", lw=2)
    ax2.plot(lc["episodes"], lc["buyer_surplus"], label="buyer surplus", color="#4c8dff")
    ax2.plot(lc["episodes"], lc["seller_surplus"], label="seller surplus", color="#e67e22")
    ax2.set_title("Surplus over training")
    ax2.set_xlabel("matched episodes")
    ax2.set_ylabel("average surplus")
    ax2.legend()
    ax2.grid(alpha=0.3)

    fig.suptitle("Multi-agent negotiation — reinforcement learning", fontsize=14)
    fig.tight_layout()
    out_path = Path(out_path)
    fig.savefig(out_path, dpi=130, bbox_inches="tight")
    plt.close(fig)
    return out_path
