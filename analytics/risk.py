def assess_risk(snapshot: dict, metrics: dict) -> dict:
    factors, missing = [], []
    score = 0.0
    liquidity=snapshot.get("liquidity_usd"); volatility=metrics.get("volatility_percent"); concentration=snapshot.get("top_10_percent")
    if liquidity is None: missing.append("liquidity")
    elif liquidity < 10000: score+=30; factors.append("Liquidez baja")
    if volatility is None: missing.append("volatility")
    elif volatility > 20: score+=25; factors.append("Volatilidad elevada")
    if concentration is None: missing.append("holder_concentration")
    elif concentration > 50: score+=30; factors.append("Concentracion elevada en top holders")
    if metrics.get("volume_liquidity_ratio") is None: missing.append("volume_liquidity_ratio")
    elif metrics["volume_liquidity_ratio"] > 10: score+=15; factors.append("Volumen relativo anormal")
    confidence="LOW" if len(missing)>=2 else "MEDIUM" if missing else "HIGH"
    category="DATA_INSUFFICIENT" if len(missing)>=2 else "HIGH" if score>=60 else "MEDIUM" if score>=30 else "LOW"
    return {"risk_score":min(score,100),"category":category,"confidence":confidence,"factors":factors,"missing_data":missing}
