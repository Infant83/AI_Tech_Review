#!/usr/bin/env python3
"""Draw selected reported SI Table 2 times. Does not run any scientific model."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Patch


def main() -> None:
    base = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=base / "artifacts/workflow-cost-data.json")
    parser.add_argument("--output", type=Path, default=base / "artifacts/catalyst-workflow-cost.png")
    parser.add_argument("--font", type=Path, help="Optional font file; otherwise use installed Nanum Gothic")
    args = parser.parse_args()
    data = json.loads(args.data.read_text(encoding="utf-8"))
    if args.font:
        font_manager.fontManager.addfont(str(args.font))
        family = font_manager.FontProperties(fname=str(args.font)).get_name()
    else:
        family = "Nanum Gothic"
        font_manager.findfont(font_manager.FontProperties(family=family), fallback_to_default=False)
    plt.rcParams.update({"font.family": family, "font.size": 13, "axes.unicode_minus": False,
                         "figure.facecolor": "white", "savefig.facecolor": "white"})
    colors = {"geometry": "#2f7c8c", "energy": "#d49b3c"}
    fig, axes = plt.subplots(2, 1, figsize=(11.8, 8.6))
    fig.subplots_adjust(left=0.29, right=0.94, top=0.765, bottom=0.24, hspace=0.92)
    fig.text(0.055, 0.945, "구조 준비와 에너지 평가에 드는 시간", fontsize=22, weight="bold", color="#19374a")
    fig.text(0.055, 0.90, "Catalysis-Hub의 동일 1,000개 구조 · 논문 보고값 · 단위: 초/구조", fontsize=14, color="#425d6f")
    fig.legend(handles=[Patch(color=colors["geometry"], label="구조 생성·완화"),
                        Patch(color=colors["energy"], label="별도 단일점 에너지 평가 (SP)")],
               loc="upper left", bbox_to_anchor=(0.055, 0.88), frameon=False, ncol=2, fontsize=13)
    for ax, panel in zip(axes, data["panels"]):
        ax.set_title(panel["title_ko"], loc="left", fontsize=16, weight="bold", pad=18, color="#19374a")
        labels = []
        for y, row in zip([1, 0], panel["rows"]):
            geometry = row["geometry_time_s"]
            sp = row["separate_energy_SP_time_s"]
            total = row["total_time_s"]
            assert abs(geometry + (sp or 0) - total) < 1e-9
            ax.barh(y, geometry, height=0.29, color=colors["geometry"], zorder=3)
            if sp is not None:
                ax.barh(y, sp, left=geometry, height=0.29, color=colors["energy"], zorder=3)
            ax.text(total + panel["xlim_s"][1] * 0.012, y, f"{total:.4f} s", va="center", fontsize=13, weight="bold")
            if sp is None:
                detail = "완화 및 UMA 에너지: 8.0996 s"
            else:
                detail = f"생성·완화 {geometry:g} + SP {sp:.4f} s"
            ax.text(0, y - 0.28, detail, va="top", fontsize=12, color="#435d6c")
            label = row["workflow"].replace("UMA-OC20 relaxation + DFT-SP", "UMA-OC20 완화\n+ DFT-SP")
            label = label.replace("UMA-OC20 relaxation", "UMA-OC20 완화")
            labels.append(label)
        ax.set_yticks([1, 0], labels=labels, fontsize=13)
        ax.tick_params(axis="y", length=0, pad=14)
        ax.tick_params(axis="x", labelsize=12)
        ax.set_xlim(*panel["xlim_s"])
        ax.set_ylim(-0.58, 1.40)
        ax.set_xlabel("시간 (초/구조)", fontsize=13, labelpad=8)
        ax.set_axisbelow(True)
        ax.grid(axis="x", color="#dbe4e9", linewidth=0.7)
        for spine in ("top", "right", "left"):
            ax.spines[spine].set_visible(False)
        ax.spines["bottom"].set_color("#9babb4")
    axes[0].set_xticks([0, 2, 4, 6, 8])
    axes[1].set_xticks([0, 40, 80, 120, 160])
    fig.text(0.055, 0.17, "두 패널은 범위가 다른 선형 시간축을 사용한다.", fontsize=13, color="#19374a", weight="bold")
    fig.text(0.055, 0.127, "UMA 완화 시간에는 최종 UMA 에너지가 포함된다. 아래 패널의 DFT는 단일점 평가이며,", fontsize=12, color="#435d6c")
    fig.text(0.055, 0.101, "구조 준비 단계는 각각 DBCata 생성과 UMA 완화다.", fontsize=12, color="#435d6c")
    fig.text(0.055, 0.058, "리뷰 재구성 | Huo·Cao, DOI 10.1038/s41467-026-79243-9, SI Table 2 보고값 | 재실행하지 않음", fontsize=11, color="#536c7b")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=220, metadata={"Software": "AEDAUT / Matplotlib; reported-value reconstruction"})
    plt.close(fig)


if __name__ == "__main__":
    main()
