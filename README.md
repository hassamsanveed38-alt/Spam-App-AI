# 🛡️ ShieldSpam AI

**AI-powered spam, scam, and phishing message detection system.**

ShieldSpam AI analyzes messages for suspicious links, phone numbers, spam keywords, phishing indicators, and other threat signals. It generates a **Risk Score**, **Verdict**, **Detection Reasons**, and **Extracted Signals**.

## ✨ Features

* 🔍 Spam and scam message detection
* 🎯 Risk Score from 0–100%
* 🚨 Spam / Suspicious / Safe verdict
* 🔗 Suspicious link detection
* 📱 Phone number analysis
* 🧠 Keyword and text-pattern analysis
* 📊 Extracted detection signals
* 🕒 Session scan history
* 🌐 Responsive web interface
* ⚡ FastAPI backend API

## 🏗️ Architecture

```text
User
 │
 ▼
ShieldSpam AI Web Interface
 │
 ▼
FastAPI Backend
 │
 ├── /api/score
 │       │
 │       ▼
 │   AI / Detection Model
 │       │
 │       ▼
 │   Risk Score + Analysis
 │
 └── /api/health
```

The web interface communicates with the FastAPI backend through the `/api/score` endpoint.

## 📁 Project Structure

```text
ShieldSpam-AI/
│
├── backend/
│   ├── app.py
│   ├── model.py
│   ├── requirements.txt
│   └── ...
│
├── static/
│   └── index.html
│
├── Dockerfile
├── render.yaml
└── README.md
```

The FastAPI application serves the web interface from the `static` directory.

## 🚀 Run Locally

### 1. Open the backend directory

```bash
cd backend
```

### 2. Create a virtual environment

**Windows:**

```cmd
python -m venv .venv
.venv\Scripts\activate
```

**Linux / macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the FastAPI server

```bash
uvicorn app:app --host 127.0.0.1 --port 8000
```

### 5. Open the website

```text
http://127.0.0.1:8000
```

## 🔌 API

### Score a message

**POST**

```text
/api/score
```

Request:

```json
{
  "text": "Your message here"
}
```

Response contains the analysis result, including the score, tier, reasons, and detection signals.

### Health Check

**GET**

```text
/api/health
```

Example response:

```json
{
  "status": "ok"
}
```

## 📊 Detection Result

ShieldSpam AI provides:

```text
Risk Score
    ↓
Verdict
    ↓
Detection Reasons
    ↓
Extracted Signals
```

Example:

```text
Risk Score: 92%

Verdict:
High Risk Spam

Reasons:
- Suspicious link
- Urgent language
- Spam keywords
- Phishing indicators
```

## 🌐 Deployment

ShieldSpam AI can be deployed as a single web service because the FastAPI backend serves both the API and the static web interface.

For a free deployment, the project can be connected to a hosting platform such as Render.

Typical deployment flow:

```text
GitHub Repository
       ↓
Render Web Service
       ↓
Docker Build
       ↓
FastAPI Backend
       ↓
Public ShieldSpam AI URL
```

Example:

```text
https://shieldspam-ai.onrender.com
```

> The actual URL will be provided by the hosting platform after deployment.

## 🔒 Privacy

Messages are sent to the backend only for scoring and analysis. The web interface is designed to display the analysis result without maintaining permanent scan history.

## 🛠️ Technologies

* Python
* FastAPI
* Uvicorn
* HTML
* CSS
* JavaScript
* Docker
* REST API

## 📌 Project Status

**Development / Testing**

ShieldSpam AI is currently being developed and tested as a cross-platform web-based spam and scam detection system.

## 📄 License

Add your preferred license here.

For example:

```text
MIT License
```

---

### ShieldSpam AI

**Detect suspicious messages before they become a threat.** 🛡️
