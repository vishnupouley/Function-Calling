"""
Dark-Weather Chat  🌌
Simple, stable Gradio chat with tuple history & function-calling
"""

import os
import json
import requests
from datetime import datetime, timezone

import gradio as gr
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# --------------------------------------------------
# 1️⃣  Tool definition
# --------------------------------------------------
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_today_forecast",
            "description": "Fetch today’s 3-hourly weather forecast for a given city",
            "parameters": {
                "type": "object",
                "properties": {"location": {"type": "string"}},
                "required": ["location"],
            },
        }
    }
]

# --------------------------------------------------
# 2️⃣  Core forecast fetcher
# --------------------------------------------------
def get_today_forecast(location: str) -> dict:
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENWEATHER_API_KEY missing")

    geo = requests.get(
        "http://api.openweathermap.org/geo/1.0/direct",
        params={"q": location, "limit": 1, "appid": api_key},
        timeout=5,
    ).json()
    if not geo:
        raise ValueError("City not found")
    lat, lon = geo[0]["lat"], geo[0]["lon"]

    fc = requests.get(
        "https://api.openweathermap.org/data/2.5/forecast",
        params={"lat": lat, "lon": lon, "units": "metric", "appid": api_key},
        timeout=5,
    ).json()

    today = datetime.now(tz=timezone.utc).date()
    entries = [
        {
            "time": datetime.strptime(e["dt_txt"], "%Y-%m-%d %H:%M:%S")
            .replace(tzinfo=timezone.utc)
            .strftime("%H:%M"),
            "temp": e["main"]["temp"],
            "desc": e["weather"][0]["description"],
        }
        for e in fc["list"]
        if datetime.strptime(e["dt_txt"], "%Y-%m-%d %H:%M:%S")
        .replace(tzinfo=timezone.utc)
        .date()
        == today
    ]
    if not entries:
        raise ValueError("No data for today")
    return {"city": fc["city"]["name"], "entries": entries}

# --------------------------------------------------
# 3️⃣  Chat logic (tuple history, Groq messages)
# --------------------------------------------------
def chat_fn(history, user_message):
    """
    history: list of [user_str, bot_str] tuples
    returns updated list of tuples
    """
    # Build clean OpenAI-style messages
    messages = [{"role": "system", "content": "You are a sarcastic, yet gentle meteorologist."}]
    for human, bot in history:
        messages.append({"role": "user", "content": human})
        if bot:
            messages.append({"role": "assistant", "content": bot})
    messages.append({"role": "user", "content": user_message})

    # Call Groq with tools
    llm = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
        temperature=0.4,
        max_tokens=200,
    )

    # Handle function call
    if llm.choices[0].message.tool_calls:
        call = llm.choices[0].message.tool_calls[0]
        city = json.loads(call.function.arguments)["location"]
        try:
            data = get_today_forecast(city)
        except Exception as e:
            assistant_text = f"Oops! {e}"
        else:
            snapshot = (
                f"Today’s weather for {data['city']}:\n"
                + "\n".join(f"{e['time']} – {e['temp']:.1f} °C, {e['desc']}" for e in data["entries"])
            )
            # Ask LLM to speak nicely
            nice_prompt = (
                "Summarise the following in one warm, polished sentence:\n\n"
                f"{snapshot}"
            )
            nice = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": nice_prompt}],
                temperature=0.3,
                max_tokens=140,
            )
            assistant_text = nice.choices[0].message.content.strip()
    else:
        assistant_text = llm.choices[0].message.content.strip()

    # Append to tuple history
    history.append([user_message, assistant_text])
    return history

# --------------------------------------------------
# 4️⃣  Gradio GUI (tuple history, no ChatInterface)
# --------------------------------------------------
css = """
body {background: linear-gradient(135deg, #0f0f1e, #1e1e2f);}
.gradio-container {color: #e0e0e0;}
.message {background: #2b2b44 !important; border-radius: 12px !important;}
.message.user {background: #2b2b44 !important; border-radius: 12px !important;}
.message.bot {background: #2b2b44 !important; border-radius: 12px !important;}
"""

with gr.Blocks(css=css, theme=gr.themes.Soft(primary_hue="purple")) as demo:
    gr.Markdown("# 🌌 Dark-Weather Chat")
    chatbot = gr.Chatbot(height=450, bubble_full_width=False)
    msg = gr.Textbox(
        placeholder="Ask me about the weather anywhere...",
        container=False,
        scale=8,
    )
    clear = gr.Button("🗑️ Clear", scale=1)

    def user(user_message, history):
        return "", history + [[user_message, None]]

    def bot(history):
        history = chat_fn(history[:-1], history[-1][0])
        return history

    msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False).then(
        bot, chatbot, chatbot
    )
    clear.click(lambda: None, None, chatbot, queue=False)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", share=False, server_port=7860)