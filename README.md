# ConvoMind 🧠

> **ConvoMind** = **Conversation** + **Mind**
> 
> A concept representing the transformation of human conversations into structured, searchable, and actionable knowledge using Artificial Intelligence and UI automation.

---

## Overview

**ConvoMind** is a lightweight Streamlit-based application designed to extract active chat conversations from **Microsoft Teams** (via Windows UIA automation) and convert them into clean, structured tabular data and Markdown reports.

Developed by **Dewan Dinata Tarigan**.

---

## Features

- **Automated Chat Harvesting:** Automatically connects to the running Microsoft Teams desktop application.
- **Dynamic Auto-Scrolling:** Smoothly scrolls up to retrieve complete conversation history.
- **Deduplication & Parsing:** Cleans and formats messages by sender and content, removing duplicates.
- **Structured Export:** Export conversations instantly as Markdown reports (`convomind_report.md`) or view them in interactive tabular views.
- **Light & Dark Mode Support:** Seamlessly adapts to Streamlit's light and dark themes.

---

## Prerequisites

- **OS:** Windows (Microsoft Teams Desktop app utilizes Windows UIA backend).
- **Python:** Version 3.8 or higher.

---

## Installation & Setup

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/your-username/ConvoMind.git
   cd ConvoMind
   ```

2. **Create and Activate a Virtual Environment (Recommended):**
   ```bash
   python -m venv venv
   # On Windows (PowerShell):
   .\venv\Scripts\Activate.ps1
   # On Windows (Command Prompt):
   venv\Scripts\activate.bat
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

1. Open **Microsoft Teams** on your Windows desktop and navigate to the chat or channel you want to extract.
2. Run the Streamlit application:
   ```bash
   streamlit run app.py
   ```
3. Open your browser at `http://localhost:8501`.
4. Click **Extract Active Chat** to harvest messages and export your Markdown report.

---

## Project Structure

```
ConvoMind/
├── app.py              # Main Streamlit application
├── inspect_teams.py    # UI inspection utility for debugging Teams elements
├── test_scroll.py      # Scroll behavior test script
├── debug_ui.py         # UI structure debugging script
├── requirements.txt    # Python package dependencies
├── .gitignore          # Git ignore rules
└── README.md           # Project documentation
```

---

## Author

Developed by **Dewan Dinata Tarigan**.
