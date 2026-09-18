from statistics import mean, pstdev

def calculate_metrics(prices=None, volumes=None, liquidities=None):
    prices=[float(v) for v in (prices or []) if v is not None and float(v)>0]; volumes=[float(v) for v in (volumes or []) if v is not None and float(v)>=0]; liquidities=[float(v) for v in (liquidities or []) if v is not None and float(v)>=0]
    out={}
    if len(prices)>=2:
        out["price_change_percent"]=(prices[-1]/prices[0]-1)*100; out["momentum_percent"]=(prices[-1]/prices[-min(4,len(prices))]-1)*100
        changes=[prices[i]/prices[i-1]-1 for i in range(1,len(prices)) if prices[i-1]]
        if len(changes)>=2: out["volatility_percent"]=pstdev(changes)*100
    if volumes and liquidities and liquidities[-1]>0: out["volume_liquidity_ratio"]=volumes[-1]/liquidities[-1]
    if len(liquidities)>=2 and liquidities[0]>0: out["liquidity_change_percent"]=(liquidities[-1]/liquidities[0]-1)*100
    if len(volumes)>=2 and volumes[0]>0: out["volume_change_percent"]=(volumes[-1]/volumes[0]-1)*100
    if prices: out["distance_from_high_percent"]=(prices[-1]/max(prices)-1)*100; out["distance_from_low_percent"]=(prices[-1]/min(prices)-1)*100
    return out

def sma(values, period): return mean(values[-period:]) if len(values)>=period else None

def ema(values, period):
    if len(values)<period: return None
    value=mean(values[:period]); alpha=2/(period+1)
    for current in values[period:]: value=(current-value)*alpha+value
    return value

def rsi(values, period=14):
    if len(values)<=period: return None
    changes=[values[i]-values[i-1] for i in range(1,len(values))][-period:]; gains=[max(c,0) for c in changes]; losses=[abs(min(c,0)) for c in changes]
    return 100.0 if mean(losses)==0 else 100-(100/(1+mean(gains)/mean(losses)))
