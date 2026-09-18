from analytics.metrics import calculate_metrics
from analytics.risk import assess_risk
from analytics.scoring import calculate_score

def run_backtest(snapshots):
    results = []
    for index, current in enumerate(snapshots):
        history = snapshots[:index + 1]
        metrics = calculate_metrics([r.get("price_usd") for r in history], [r.get("volume_24h_usd") for r in history], [r.get("liquidity_usd") for r in history])
        risk = assess_risk(current, metrics)
        results.append({"timestamp": current.get("captured_at"), "metrics": metrics, "risk": risk, "score": calculate_score(current, metrics, risk)})
    return results
