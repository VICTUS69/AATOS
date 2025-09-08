from openai import OpenAI
import json

client = OpenAI(api_key="your_api_key")

def llm_decision(car_counts):
    prompt = f"""
    You are a smart traffic signal AI.
    Based on these counts: {car_counts}
    Decide green durations in JSON.
    Rules:
    - More cars = longer green
    - No cars = skip
    - Min = 4s, Max = 60s
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return json.loads(response.choices[0].message.content)
