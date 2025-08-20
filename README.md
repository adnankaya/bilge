# Your wise activity tracker


## ⚠️ Warning: This is a Pre-Release / Development Version

Bilge is an open-source project currently under active development. This version is intended for early adopters, developers, and testers. It may contain bugs, incomplete features, and is not yet optimized for daily use.

Your contributions and feedback are highly encouraged to help us improve the app.

## Overview: What is Bilge?

Bilge is a privacy-first, local-first AI wellness companion designed to help people build a healthier relationship with their computer use. Unlike traditional productivity or time-tracking apps that focus on surveillance, Bilge's core philosophy is centered on user well-being, using a wise and gentle approach to promote balanced digital habits.

The app runs quietly in the background on the user's machine, ensuring all sensitive data remains on-device and never leaves their control. By leveraging a local, open-source LLM, Bilge translates raw computer activity into meaningful insights about digital habits, all without sacrificing privacy.


## How It Works

- Usage Awareness — Logs active apps and time spent locally on-device.

- AI Categorization — local LLM/SLM classifies usage into categories (Work, Gaming, Browsing, Communication) and detects patterns like overworking or excessive screen time.

- Wellness Coaching — Provides context-aware, human-friendly notifications:
    - “You’ve been coding for 2.5 hours — let’s take a stretch break.”
    - “3 hours of gaming is fun, but how about a quick pause?”
    - “Today you’ve been online for 6+ hours — maybe it’s time for a walk.”

- Privacy First — All processing runs locally, ensuring sensitive usage data never leaves your machine.

## Impact

In a world where people struggle with burnout, digital addiction, and unhealthy work-life balance, Bilge agent empowers healthier habits. By combining open-source AI, local agents, and a focus on humanity, it promotes sustainable screen use that improves mental and physical well-being — without sacrificing privacy.

# Installations and Setup

## 1. Python
- use Python 3.12.11

```bash
python3.12 -m venv venv

source venv/bin/activate

pip install -r requirements.txt

```

## 2. Ollama
- install ollama
- run your LLM/SLM with ollama

## Running

```bash

python run.py gpt-oss:20b
# or
python run.py gemma3:4b
# or
python run.py llama3.2:1b

```

## Rules
- rules_config.json : for development and testing purposes I use seconds for duration.

```json

{
    "rules": [
        {
            "category": "Work",
            "duration_seconds": 30,
            "action_name": "short_work_session"
        },
        {
            "category": "Gaming",
            "duration_seconds": 10,
            "action_name": "short_gaming_session"
        },
        {
            "category": "Browsing",
            "duration_seconds": 90,
            "action_name": "short_browsing_session"
        },
        {
            "category": "Media",
            "duration_seconds": 20,
            "action_name": "short_media_session"
        },
        {
            "category": "Communication",
            "duration_seconds": 10,
            "action_name": "short_communication_session"
        },
        {
            "category": "Other",
            "duration_seconds": 10,
            "action_name": "short_other_session"
        }
    ]
}
```

