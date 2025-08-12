"""
Dark-Weather Chat  🌌
Simple, stable Gradio chat with tuple history & function-calling
"""

import os
import pytz
import json
import requests
from tabulate import tabulate
from datetime import datetime, timezone

import gradio as gr
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# --------------------------------------------------
# 1️⃣  Tool definition
# --------------------------------------------------
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather_window",
            "description": (
                "Return 3-hourly weather for any part of the day "
                "(morning, afternoon, evening, night, or whole day)."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"},
                    "period": {
                        "type": "string",
                        "enum": ["morning", "afternoon", "evening", "night", "day"],
                    },
                },
                "required": ["location", "period"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_time_weather",
            "description": (
                "Return the exact local time, date and current weather for a city "
                "as a markdown table with emojis."
            ),
            "parameters": {
                "type": "object",
                "properties": {"location": {"type": "string"}},
                "required": ["location"],
            },
        },
    },
]


# --------------------------------------------------
# 2️⃣  Flexible weather window (morning / afternoon / evening / night / day)
# --------------------------------------------------
def get_weather_window(location: str, period: str) -> dict:
    """
    period ∈ {"morning", "afternoon", "evening", "night", "day"}
    """
    mapping = {
        "morning": (6, 12),
        "afternoon": (12, 17),
        "evening": (17, 21),
        "night": (21, 24),
        "day": (6, 24),
    }
    start_h, end_h = mapping.get(period.lower(), (0, 24))

    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENWEATHER_API_KEY missing")

    geo = requests.get(
        "http://api.openweathermap.org/geo/1.0/direct",
        params={"q": location, "limit": 1, "appid": api_key},
        timeout=5,
    ).json()
    # print(f"\ngeo = {json.dumps(geo, indent=4, sort_keys=True)}")
    if not geo:
        raise ValueError("City not found")
    lat, lon = geo[0]["lat"], geo[0]["lon"]

    fc = requests.get(
        "https://api.openweathermap.org/data/2.5/forecast",
        params={"lat": lat, "lon": lon, "units": "metric", "appid": api_key},
        timeout=5,
    ).json()

    # print(f"\nfc = {json.dumps(fc, indent=4, sort_keys=True)}")

    slices = []
    for e in fc["list"]:
        dt = datetime.strptime(e["dt_txt"], "%Y-%m-%d %H:%M:%S").replace(
            tzinfo=timezone.utc
        )
        # print(f"today: {datetime.now(tz=timezone.utc).date()}")
        # print(f"dt: {dt.date()}")
        if (
            start_h <= dt.hour < end_h or period == "day"
        ) and dt.date() == datetime.now(tz=timezone.utc).date():
            slices.append(
                {
                    "time": dt.strftime("%H:%M"),
                    "temp": e["main"]["temp"],
                    "weather": e["weather"][0]["description"],
                    "rain": e.get("rain", {}).get("3h", 0),
                    "wind": e["wind"]["speed"],
                }
            )
    # print(f"\nslices = {json.dumps(slices, indent=4, sort_keys=True)}")
    return {"city": fc["city"]["name"], "period": period, "slices": slices}


# --------------------------------------------------
# 3️⃣  Current time and weather (location)
# --------------------------------------------------
def get_time_weather(location: str) -> str:
    """Local clock + current weather in a pretty markdown table."""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    geo = requests.get(
        "http://api.openweathermap.org/geo/1.0/direct",
        params={"q": location, "limit": 1, "appid": api_key},
        timeout=5,
    ).json()
    if not geo:
        return f"❌ City **{location}** not found."

    lat, lon = geo[0]["lat"], geo[0]["lon"]
    city = geo[0]["name"]

    # current weather
    now = requests.get(
        "https://api.openweathermap.org/data/2.5/weather",
        params={"lat": lat, "lon": lon, "units": "metric", "appid": api_key},
        timeout=5,
    ).json()

    # local time
    tz_name = pytz.country_timezones.get(now["sys"]["country"], ["UTC"])[0]
    local_time = datetime.now(pytz.timezone(tz_name))

    # markdown table
    table = tabulate(
        [
            ["🕒 Local Time", local_time.strftime("%H:%M — %d %b")],
            ["🌡️  Temp", f"{now['main']['temp']} °C"],
            ["🌤️  Condition", now["weather"][0]["description"].title()],
            ["💧 Humidity", f"{now['main']['humidity']} %"],
            ["💨 Wind", f"{now['wind']['speed']} m/s"],
        ],
        headers=["Field", "Value"],
        tablefmt="github",
    )
    return f"📍 **{city}** right now:\n{table}"


# --------------------------------------------------
# 4️⃣  Chat logic (tuple history, Groq messages)
# --------------------------------------------------
def chat_fn(history: list[list[str]], user_message: str) -> list[list[str]]:
    """
    history: tuple list (kept for backward compat)
    returns: updated tuple list
    """
    # build dict history
    dict_hist = [{"role": "user", "content": u} for u, _ in history] + [
        {"role": "assistant", "content": a} for _, a in history if a
    ]
    dict_hist.append({"role": "user", "content": user_message})

    # call the short, sarcastic logic that now lives in bot()
    messages = [
        {
            "role": "system",
            "content": (
                "You are a sarcastic weather friend. "
                "Decide which tool to use:"
                "- If the user asks for **time** OR **date** OR **current weather** for a specific location, call `get_time_weather`."
                "- If the user asks for a **period** (morning, afternoon, evening, night, day) " 
                    "or a **social scenario** for a specific location, call `get_weather_window`."
                "1. If the tool returns an empty slice OR the location is not found, "
                '   reply ONLY with: "I couldn\'t find weather data for <location>." '
                "2. If the period is impossible (e.g. morning when user asked evening), "
                '   reply ONLY with: "Please ask for a valid period." '
                "3. If data exists, Reply with short in 70 - 100 words"
                " simple words, one tiny jab, and one practical tip."
                "4. No big vocabulary in the answer itself."
                "5. Never insert Markdown, JSON, or `<function>` inside the function call."
            ),
        }
    ] + dict_hist

    llm = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
        max_tokens=130,
        temperature=0.45,
    )

    # same short-answer logic as in bot()
    if llm.choices[0].message.tool_calls:
        for call in llm.choices[0].message.tool_calls:
            name = call.function.name
            city = json.loads(call.function.arguments)["location"]

            if name == "get_time_weather":
                answer = get_time_weather(city)
            elif name == "get_weather_window":
                period = json.loads(call.function.arguments).get("period", "day")
                try:
                    data = get_weather_window(city, period)
                except Exception as e:
                    answer = f"Oops: {e}"
                else:
                    if data["slices"]:
                        snippet = ", ".join(
                            f"{s['time']} {s['temp']}°C {s['weather']}"
                            for s in data["slices"][:3]
                        )
                        prompt = (
                            f"Write a 70–90-word sarcastic forecast for {city} {period}. "
                            f"Data: {snippet}. "
                            "Return **only** the text—no tables, no JSON, no `<function>` tags."
                        )
                    else:
                        prompt = (
                            f"{city} {period}: Since the timing is wrong, "
                            "reply with a snarky tip that the timing is wrong."
                        )
                    short = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=100,
                        temperature=0.4,
                    )
                    answer = short.choices[0].message.content.strip()
    else:
        answer = llm.choices[0].message.content.strip()

    history.append([user_message, answer])
    return history


# --------------------------------------------------
# 4️⃣  Gradio GUI (tuple history, no ChatInterface)
# --------------------------------------------------
css = """
body {background: linear-gradient(135deg, #101027, #2A2A3B);}
.gradio-container {color: #E0E0E0EA;}
.message {background: #2b2b44 !important; border-radius: 12px !important;}
.message.user {background: #2b2b44 !important; border-radius: 12px !important;}
.message.bot {background: #2b2b44 !important; border-radius: 12px !important;}
"""

with gr.Blocks(css=css, theme=gr.themes.Soft(primary_hue="purple")) as demo:
    gr.Markdown("# 🌌 Dark-Weather Chat")
    chatbot = gr.Chatbot(height=630, type="messages")
    msg = gr.Textbox(
        placeholder="Ask me about the weather anywhere...",
        container=False,
        scale=8,
    )
    examples = gr.Examples(
        examples=[
            "Morning weather in Helsinki—do I need mittens or just sarcasm?",
            "Afternoon forecast in Cairo—will the sun roast my patience or just my coffee?",
            "Evening drizzle in Seattle—umbrella essential or can I wing it with sass?",
            "Night shenanigans in Rio—jacket or just vibes under the stars?",
            "What's the weather in New York City?",
            "Full-day weather rollercoaster in Melbourne—layers, sunscreen, or both?",
            "Planning a late-night barbecue in London—umbrella or not?",
            "Brunch under the Barcelona sun—will the afternoon sizzle or simply simmer?",
            "What's the time in Dublin?",
            "Tokyo twilight stroll—cardigan or courage?",
            "Berlin all-nighter—windbreaker or wishful thinking?",
            "Sydney sunrise hike—frostbite or flip-flops?",
            "What's the date and time in Singapore?",
        ],
        examples_per_page=5,
        inputs=msg,
        label="Try these examples",
    )
    clear_btn = gr.Button("🗑️ Clear", scale=1)

    # ----------------------------
    # 1️⃣  User step – just append the user dict
    # ----------------------------
    def user(user_message, history):
        return "", history + [{"role": "user", "content": user_message.strip()}]

    # ----------------------------
    # 2️⃣  Bot step – one-shot, no double history
    # ----------------------------
    def bot(history):
        # history is already dict-style; feed it straight to chat_fn
        tuple_history = [
            [h["content"], a["content"]] for h, a in zip(history[::2], history[1::2])
        ]
        updated_tuples = chat_fn(tuple_history, history[-1]["content"])
        # turn the returned tuples back into dict list
        new_history = []
        for u, a in updated_tuples:
            new_history.extend(
                [{"role": "user", "content": u}, {"role": "assistant", "content": a}]
            )
        return new_history

    msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False).then(
        bot, chatbot, chatbot
    )
    clear_btn.click(lambda: [], None, chatbot, queue=False)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", share=False, server_port=7860)
