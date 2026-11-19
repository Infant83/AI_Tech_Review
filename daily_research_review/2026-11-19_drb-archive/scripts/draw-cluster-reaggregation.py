#!/usr/bin/env python3
"""Draw a new chart from attributed reported results; no paper art or model rerun.

The input contains a deterministic editorial reaggregation of the publisher's
Source Data Fig. 2 using the authors' openly supplied analysis recipe.
"""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--font", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path,
                        default=Path(__file__).resolve().parents[1] / "artifacts")
    parser.add_argument("--data", type=Path,
                        default=Path(__file__).resolve().parents[1] / "artifacts" / "cluster-figure-data.json")
    args = parser.parse_args()
    data = json.loads(args.data.read_text(encoding="utf-8"))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    font = FontProperties(fname=str(args.font))
    ink, muted, teal, blue, grey = "#193c50", "#526774", "#167c94", "#5a7397", "#7a8790"
    fig = plt.figure(figsize=(18, 8.5), dpi=100, facecolor="white")
    def text(x, y, value, size=27, color=ink, **kwargs):
        return fig.text(x, y, value, fontproperties=font, fontsize=size,
                        color=color, **kwargs)
    text(.035, .935, "Representative samples for a fixed material library", 36)
    text(.035, .865, "N = 100  |  46 tasks × 7 predictors × 10 seeds  |  Mean ± SEM", 27, muted)
    ax = fig.add_axes([.415, .285, .535, .445])
    ax.set_xlim(.845, .915)
    ax.set_ylim(-.48, 2.48)
    ax.set_yticks([])
    ax.set_xticks([.85, .87, .89, .91])
    ax.set_xticklabels(["0.85", "0.87", "0.89", "0.91"],
                       fontproperties=font, fontsize=26, color=muted)
    ax.tick_params(axis="x", length=7, width=1.4, pad=10)
    ax.grid(axis="x", color="#dae3e8", linewidth=1)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color(muted)
    ax.spines["bottom"].set_linewidth(1.4)
    labels = ["Cluster (k-medoids)", "Best tested AL", "Random"]
    colors = [teal, blue, grey]
    for row, y, label, color in zip(data["rows"], [2, 1, 0], labels, colors):
        ax.errorbar(row["mean"], y, xerr=row["sem"], fmt="o", markersize=14,
                    color=color, ecolor=color, elinewidth=3, capsize=8, capthick=3, zorder=3)
        py = .285 + .445 * ((y + .48) / 2.96)
        text(.035, py + .015, label, 29, color)
        text(.95, py + .045, f'{row["mean"]:.4f} ± {row["sem"]:.4f}', 27,
             color, ha="right")
        if y == 1:
            text(.035, py - .045, "NN + cluster-margin", 26, muted)
    text(.682, .18, "Normalized Spearman correlation  (higher is better)", 27,
         ha="center")
    text(.035, .105, "Evaluation: entire predefined candidate library, including training points.", 27, muted)
    text(.035, .046, "Editorial reaggregation of supplied results; no model training was rerun.  Gallagher et al. (2026)", 26, muted)
    output = args.output_dir / "ncs-cluster-reaggregation.png"
    fig.savefig(output, dpi=100, facecolor="white",
                metadata={"Title": "Fixed-library training-set selection",
                          "Description": "Original editorial chart of reaggregated source values; mean and SEM, not prediction accuracy.",
                          "Software": "Matplotlib"})
    plt.close(fig)
    print(output)

if __name__ == "__main__":
    main()
