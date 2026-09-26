"""Stratified sampling utility for audit verification."""
import sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.pipeline import load_data, prepare_tickets

def generate_sample(n_per_category: int = 10, random_state: int = 42) -> pd.DataFrame:
    """Generate a reproducible stratified sample across all ticket categories."""
    tickets, agents, *_ = load_data()
    df = prepare_tickets(tickets, agents)
    sample = pd.concat([
        group.sample(min(len(group), n_per_category), random_state=random_state)
        for _, group in df.groupby("category")
    ], ignore_index=True)
    return sample

if __name__ == "__main__":
    s = generate_sample()
    print(f"Sampled {len(s)} tickets across {s['category'].nunique()} categories.")
