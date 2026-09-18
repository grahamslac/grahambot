def format_report(token, snapshot, metrics, risk, score, ai_summary=None, holder=None):
    global_score = score.get("global_score")
    lines = ["GRAHAM ANALYSIS", "", "Token: " + str(token.get("symbol") or "UNKNOWN"), "Address: " + str(token.get("token_address")), "", "Market"]
    for key in ("price_usd", "liquidity_usd", "volume_24h_usd", "market_cap_usd"):
        lines.append("- " + key + ": " + str(snapshot.get(key) if snapshot.get(key) is not None else "UNKNOWN"))
    lines.append(""); lines.append("Metrics")
    for key, value in metrics.items(): lines.append("- " + key + ": " + str(value))
    lines.extend(["", "Risk: " + str(risk.get("category")), "Confidence: " + str(score.get("confidence")), "Global Score: " + str(global_score if global_score is not None else "DATA_INSUFFICIENT")])
    if holder:
        lines.append(""); lines.append("Holders")
        for key in ("holder_count", "top_10_percent", "creator_percent", "snipers_percent", "insiders_percent", "bundlers_percent", "active_wallets"):
            lines.append("- " + key + ": " + str(holder.get(key) if holder.get(key) is not None else "UNKNOWN"))
    if risk.get("factors"): lines.append("Risk factors: " + "; ".join(risk["factors"]))
    if risk.get("missing_data"): lines.append("Missing: " + ", ".join(risk["missing_data"]))
    if ai_summary: lines.extend(["", "AI interpretation:", ai_summary])
    return "\n".join(lines)
