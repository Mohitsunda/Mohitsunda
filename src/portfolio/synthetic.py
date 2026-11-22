"""Seeded artificial demo inputs. No records are copied from actual customers."""

import numpy as np
import pandas as pd

from portfolio.common import SEED


def retail_demo(seed: int = SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    for number in range(3000):
        customer = int(rng.integers(1_000_001, 1_000_451)) if rng.random() > 0.12 else None
        date = pd.Timestamp("2025-01-01") + pd.Timedelta(days=int(rng.integers(0, 360)))
        country = rng.choice(["United Kingdom", "Ireland", "France"], p=[0.8, 0.12, 0.08])
        credit = rng.random() < 0.07
        for _ in range(int(rng.integers(1, 8))):
            item = int(rng.integers(1, 101))
            rows.append(
                {
                    "InvoiceNo": ("C" if credit else "") + f"SYN-{number:06d}",
                    "StockCode": f"SYN-SKU-{item:03d}",
                    "Description": f"Simulated item {item}",
                    "Quantity": int(rng.integers(1, 9)) * (-1 if credit else 1),
                    "InvoiceDate": date,
                    "UnitPrice": round(1 + item * 0.23, 2),
                    "CustomerID": customer,
                    "Country": country,
                }
            )
    frame = pd.DataFrame(rows)
    # Deliberate quality defects exercise the same audit path as full sources.
    frame = pd.concat([frame, frame.head(30)], ignore_index=True)
    frame.loc[100:104, "UnitPrice"] = 0
    return frame


def churn_demo(seed: int = SEED, rows: int = 1500) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    complaint = rng.binomial(1, 0.14, rows)
    seconds = rng.gamma(2, 1500, rows).astype(int)
    failures = rng.poisson(5, rows)
    probability = 1 / (1 + np.exp(-(-1.8 + complaint * 2.5 - seconds / 4500 + failures * 0.12)))
    return pd.DataFrame(
        {
            "Call Failure": failures,
            "Complains": complaint,
            "Subscription Length": rng.integers(1, 61, rows),
            "Charge Amount": rng.integers(0, 10, rows),
            "Seconds of Use": seconds,
            "Frequency of use": rng.poisson(200, rows),
            "Frequency of SMS": rng.poisson(70, rows),
            "Distinct Called Numbers": rng.integers(1, 100, rows),
            "Tariff Plan": rng.choice([1, 2], rows),
            "Churn": rng.binomial(1, probability),
        }
    )
