def calculate_score(snapshot: dict, metrics: dict, risk: dict) -> dict:
    components=[]
    def add(name,value,weight,explanation): components.append({"component":name,"value":max(0,min(100,value)),"weight":weight,"explanation":explanation})
    liquidity=snapshot.get("liquidity_usd"); add("LIQUIDITY",70 if liquidity and liquidity>=10000 else 20 if liquidity else 0,.2,"Liquidez observada o dato ausente")
    momentum=metrics.get("momentum_percent"); add("MOMENTUM",60 if momentum is not None and momentum>0 else 30 if momentum is not None else 0,.2,"Momentum calculado con snapshots")
    volume=metrics.get("volume_liquidity_ratio"); add("VOLUME",65 if volume is not None and .1<=volume<=5 else 25 if volume is not None else 0,.15,"Relacion volumen/liquidez")
    add("RISK",100-risk["risk_score"],.3,"Puntuacion inversa del Risk Engine")
    add("DATA_QUALITY",100 if not risk["missing_data"] else max(0,100-20*len(risk["missing_data"])),.15,"Completitud de datos")
    weight=sum(c["weight"] for c in components if c["value"]>0); global_score=sum(c["value"]*c["weight"] for c in components)/weight if weight else None
    confidence="HIGH" if not risk["missing_data"] else "LOW" if len(risk["missing_data"])>=2 else "MEDIUM"
    return {"global_score":global_score,"confidence":confidence,"components":components}
