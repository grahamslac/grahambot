from pathlib import Path

def create_market_chart(snapshots, output_path, title="Graham market history"):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    rows = [r for r in snapshots if r.get("price_usd") is not None]
    if not rows: return None
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot([r.get("captured_at") for r in rows], [r["price_usd"] for r in rows])
    ax.set_title(title); ax.set_ylabel("USD"); ax.tick_params(axis="x", rotation=30)
    fig.tight_layout(); fig.savefig(output_path, dpi=150); plt.close(fig)
    return str(output_path)
