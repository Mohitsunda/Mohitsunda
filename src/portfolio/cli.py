"""Command-line interface for acquisition, full builds and batch inference."""

from __future__ import annotations

import argparse
from pathlib import Path

from portfolio.common import ROOT, fetch_dataset, save_json


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description="Build Mohit Sunda's analytics portfolio")
    commands = parser.add_subparsers(dest="command", required=True)
    download = commands.add_parser("download", help="Fetch and verify UCI source datasets")
    download.add_argument("--dataset", choices=["all", "retail", "churn"], default="all")
    build = commands.add_parser("build", help="Build all three projects and decision reports")
    build.add_argument("--source", choices=["demo", "full"], default="demo")
    build.add_argument("--output", type=Path)
    score = commands.add_parser(
        "score", help="Score a CSV with a locally built, trusted churn model"
    )
    score.add_argument("--model", type=Path, required=True)
    score.add_argument("--input", type=Path, required=True)
    score.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == "download":
        names = ["retail", "churn"] if args.dataset == "all" else [args.dataset]
        for name in names:
            print(fetch_dataset(name))
    elif args.command == "score":
        from portfolio.churn import score_customers

        score_customers(args.model, args.input, args.output)
        print(f"Scored customers: {args.output}")
    else:
        from portfolio.churn import build_churn
        from portfolio.logistics import build_logistics
        from portfolio.reporting import render_reports
        from portfolio.retail import build_retail

        output = (args.output or ROOT / "artifacts" / args.source).resolve()
        output.mkdir(parents=True, exist_ok=True)
        print(f"Building {args.source} retail data…", flush=True)
        retail = build_retail(args.source, output)
        print("Training and evaluating retention models…", flush=True)
        churn = build_churn(args.source, output)
        print("Evaluating synthetic logistics scenarios…", flush=True)
        logistics = build_logistics(output)
        save_json(
            output / "run_manifest.json",
            {
                "source_mode": args.source,
                "seed": 42,
                "retail_input_rows": retail["input_rows"],
                "churn_rows": churn["rows"],
                "logistics_rows": logistics["shipments"],
                "command": f"portfolio build --source {args.source}",
            },
        )
        render_reports(output, retail, churn, logistics)
        print(f"Complete: {output}")
