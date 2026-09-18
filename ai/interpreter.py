import json
from config import OPENAI_API_KEY, OPENAI_MODEL

async def interpret_analysis(analysis: dict) -> str | None:
    """Interpreta datos disponibles sin inventar información ni dar órdenes financieras."""
    if not OPENAI_API_KEY:
        return None
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    response = await client.chat.completions.create(
        model=OPENAI_MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": "Interpreta únicamente el JSON recibido. No inventes datos. Si faltan datos, indica DATA_INSUFFICIENT. No des órdenes de compra o venta."},
            {"role": "user", "content": json.dumps(analysis, ensure_ascii=False)},
        ],
    )
    return response.choices[0].message.content
