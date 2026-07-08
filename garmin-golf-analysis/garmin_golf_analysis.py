#!/usr/bin/env python3
"""Analyze Garmin Golf scorecard data exported to JSON."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Any


@dataclass(frozen=True)
class Fraction:
    made: int
    total: int

    @property
    def pct(self) -> float:
        return 0.0 if self.total == 0 else self.made / self.total * 100


def load_rounds(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("Top-level JSON must be a list of rounds.")
    return data


def total_fraction(rounds: list[dict[str, Any]], hit_key: str, total_key: str) -> Fraction:
    return Fraction(
        made=sum(int(r.get(hit_key, 0)) for r in rounds),
        total=sum(int(r.get(total_key, 0)) for r in rounds),
    )


def hole_summary(rounds: list[dict[str, Any]]) -> list[dict[str, Any]]:
    holes: dict[int, dict[str, Any]] = defaultdict(lambda: {"scores": [], "putts": [], "par": None})
    for round_data in rounds:
        for hole in round_data.get("holes", []):
            hole_no = int(hole["hole"])
            holes[hole_no]["par"] = int(hole["par"])
            holes[hole_no]["scores"].append(int(hole["score"]))
            if "putts" in hole:
                holes[hole_no]["putts"].append(int(hole["putts"]))

    summary = []
    for hole_no, item in sorted(holes.items()):
        scores = item["scores"]
        putts = item["putts"]
        par = item["par"]
        summary.append(
            {
                "hole": hole_no,
                "par": par,
                "avg_score": mean(scores),
                "avg_over": mean(scores) - par,
                "avg_putts": mean(putts) if putts else None,
                "best": min(scores),
                "worst": max(scores),
            }
        )
    return summary


def markdown_report(rounds: list[dict[str, Any]]) -> str:
    if not rounds:
        return "No rounds found.\n"

    scores = [int(r["out"]) + int(r["in"]) for r in rounds]
    putts = [int(r["putts"]) for r in rounds if "putts" in r]
    fairways = total_fraction(rounds, "fairways_hit", "fairways_total")
    gir = total_fraction(rounds, "gir_hit", "gir_total")
    holes = hole_summary(rounds)
    hardest = sorted(holes, key=lambda h: h["avg_over"], reverse=True)[:5]
    easiest = sorted(holes, key=lambda h: h["avg_over"])[:5]

    lines = [
        "# Garmin Golf Analysis",
        "",
        f"- Rounds: {len(rounds)}",
        f"- Average score: {mean(scores):.1f}",
        f"- Best score: {min(scores)}",
        f"- Worst score: {max(scores)}",
        f"- Average putts: {mean(putts):.1f}" if putts else "- Average putts: n/a",
        f"- Fairways: {fairways.made}/{fairways.total} ({fairways.pct:.1f}%)",
        f"- GIR: {gir.made}/{gir.total} ({gir.pct:.1f}%)",
        "",
        "## Rounds",
        "",
        "| Date | Course | Green | Score | Out/In | Putts | FW | GIR |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]

    for r in rounds:
        score = int(r["out"]) + int(r["in"])
        lines.append(
            "| {date} | {course} | {green} | {score} | {out}/{in_} | {putts} | {fw_h}/{fw_t} | {gir_h}/{gir_t} |".format(
                date=r.get("date", ""),
                course=r.get("course", ""),
                green=r.get("green", ""),
                score=score,
                out=r.get("out", ""),
                in_=r.get("in", ""),
                putts=r.get("putts", ""),
                fw_h=r.get("fairways_hit", ""),
                fw_t=r.get("fairways_total", ""),
                gir_h=r.get("gir_hit", ""),
                gir_t=r.get("gir_total", ""),
            )
        )

    lines.extend(["", "## Hardest Holes", "", "| Hole | Par | Avg | Avg Over | Best | Worst |", "|---:|---:|---:|---:|---:|---:|"])
    for h in hardest:
        lines.append(
            f"| {h['hole']} | {h['par']} | {h['avg_score']:.2f} | {h['avg_over']:.2f} | {h['best']} | {h['worst']} |"
        )

    lines.extend(["", "## Easiest Holes", "", "| Hole | Par | Avg | Avg Over | Best | Worst |", "|---:|---:|---:|---:|---:|---:|"])
    for h in easiest:
        lines.append(
            f"| {h['hole']} | {h['par']} | {h['avg_score']:.2f} | {h['avg_over']:.2f} | {h['best']} | {h['worst']} |"
        )

    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze Garmin Golf scorecard JSON.")
    parser.add_argument("rounds_json", type=Path, help="Path to scorecard JSON data.")
    args = parser.parse_args()
    print(markdown_report(load_rounds(args.rounds_json)))


if __name__ == "__main__":
    main()
