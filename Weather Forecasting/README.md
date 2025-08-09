# 🌌 Dark-Weather Chat — The Sarcastic Meteorologist in Your Pocket

> “Rain or shine, it’ll throw shade at the clouds. Because meteorology without mockery is just… math.”

---

## 📜 Table of Contents

1. [✨ Introduction](#-introduction)  
2. [⚙️ Setup & Run](#-setup--run)  
3. [🧠 Overview](#-overview)  
4. [🛠️ Tech Stack](#tech-stack)  
5. [🎩 Usage & Features](#-usage--features)  
6. [🖼️ Workspace Layout](#workspace-layout)  
7. [📚 References](#-references)  
8. [🤝 Contribute & Flex](#-contribute--flex)

---

## ✨ Introduction

Welcome to **Dark-Weather Chat** — a moody, snarky, AI-powered weather assistant that speaks fluent sarcasm and never forgets an umbrella.  
Built with **Groq LLMs**, **OpenWeatherMap**, and **Gradio**, it fetches hyper-local forecasts and serves them with a side of sass.  
Ask **“evening plans in Goa?”** and get back a 70-word roast + actionable advice.
Ask for **time**, **weather**, or **existential climate dread**—get back a 70-word roast, a table of doom, or both.

- **Two tools**, one sass  
- **Dark UI** darker than your Monday mood  
- **0 hallucination policy** (we roast clouds, not sanity)

---

## ⚙️ Setup & Run

### 🚀 One-Line UV Guide for `Dark-Weather Chat`

> Zero-dependency installs, zero `requirements.txt` drama.

### 1️⃣ Clone & Enter
```bash
git clone https://github.com/vishnupouley/Function-Calling.git
cd Function-Calling/Weather\ Forecasting
```

### 2️⃣ Create & Activate Virtual Environment with UV
```bash
uv venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

### 3️⃣ Install All Locked Dependencies
```bash
uv sync        # installs everything recorded in uv.lock
```
> `uv sync` is the new `pip install -r requirements.txt`.  
> It respects `pyproject.toml` *and* the lock file.


### 4️⃣ Configure Secrets
Create `.env` in the same folder as `main.py`:
```bash
echo "GROQ_API_KEY=sk-..." > .env
echo "OPENWEATHER_API_KEY=your_owm_key" >> .env
```

### 5️⃣ Launch the Dark Oracle
```bash
python main.py
```
Your browser will open at `http://localhost:7860` with the moody chat UI ready to roast the weather.


### 🧹 Quick Cleanup (Optional)
```bash
deactivate
```

That’s it — pure **UV** magic, no `pip` required.

---

## 🧠 Overview

| Component | Purpose |
|-----------|---------|
| `get_time_weather()`  | local clock + live weather in a table with emojis |
| `get_weather_window()` | Pulls 3-hour slices for **morning / afternoon / evening / night / full-day**. |
| `chat_fn()` | Converts tuple history → dict → sarcastic 70–90-word reply. |
| `Gradio UI` | Dark theme, live chat, clickable examples. |

---

<h2 id="tech-stack">🛠️ Tech Stack</h2>

- **Python 3.10+**
- **Groq LLM**  (llama-3.1-8b-instant) – answers faster than your ex texts back
- **OpenWeatherMap API** - free tier, still delivers more accuracy than your horoscope
- **Gradio** (dark, responsive UI) - dark theme, zero CSS tears
- **Requests** (HTTP client)
- **python-dotenv** (secret management)
- **Tabulate** (table formatting)
- **Pytz** (timezone handling) - time zones without the existential dread

---

## 🎩 Usage & Features

| Feature | Example Prompt | Bot Response |
|---------|----------------|--------------|
| **Morning** | *“morning in Helsinki—mittens or sarcasm?”* | *“3 °C, fog thicker than your jokes. Grab gloves.”* |
| **Afternoon** | *“afternoon in Cairo—roast or simmer?”* | *“36 °C, sun’s flexing. Sunscreen now, regrets later.”* |
| **Evening** | *“evening drizzle in Seattle—umbrella?”* | *“Light rain at 19 °C. Umbrella: optional, ego: required.”* |
| **Night** | *“night in Rio—jacket or vibes?”* | *“24 °C, humid breeze. Jacket is just extra luggage.”* |
| **weather** | *“What’s the weather in New York?”* | *“📍 **New York** right now:\n36 °C, sun’s flexing. Sunscreen now, regrets later.”* |
| **time** | *“What’s the time in Dublin?”* | *“🕒 Local Time: 12:34 — 25 Aug”* |

- **Zero Hallucination Policy**  
  - Empty slice? → *“I couldn’t find weather data for <location>.”*  
  - Impossible period? → *“Please ask for a valid period.”*

- **70–90 Word Limit** – long enough to roast, short enough to tweet.

- **Dark UI** – because weather is already gloomy enough.

---
<h2 id="workspace-layout">🖼️ Workspace Layout</h2>

```
Weather Forecasting/
├── .env                 # secrets (never commit)
├── main.py              # full app logic
├── README.md            # this beauty
├── .gitignore
└── uv.lock / pyproject.toml  # optional uv setup
```

---

## 📚 References

- [Groq Docs](https://console.groq.com/docs)  
- [OpenWeatherMap API](https://openweathermap.org/api)  
- [Gradio Docs](https://gradio.app/docs)

---

## 🤝 Contribute & Flex

1. Fork → star ⭐
2. Add a new snarky prompt
3. Submit PR with emoji commit (git commit -m "add more shade ☁️")

---

<p align="center">
  <img src="https://readme-typing-svg.herokuapp.com/?font=Fira+Code&size=22&duration=3000&color=7f5af0&center=true&vCenter=true&width=600&lines=Stay+dry,+stay+sarcastic!"/>
</p>

