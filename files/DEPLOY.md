# ShieldSpam AI — Web Version Deploy Guide

Ye folder ek self-contained web version hai: ek FastAPI backend jo scoring bhi
karta hai aur `static/index.html` (browser UI) bhi serve karta hai. Ek hi
service deploy karne se ek hi public link mil jata hai.

## Local test (deploy se pehle check karne ke liye)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --host 127.0.0.1 --port 8000
```

Browser mein kholein: http://127.0.0.1:8000

## Free public link — Render.com (recommended, sabse aasan)

1. Ye poora `shieldspam-web/` folder ek GitHub repo mein push karen.
2. https://render.com par account banayen (GitHub se sign in kar sakte hain).
3. **New +** → **Web Service** → apni repo select karen.
4. Render `render.yaml` khud detect kar lega (Docker environment).
   Agar manually set karna ho:
   - Environment: **Docker**
   - Dockerfile path: `./Dockerfile`
5. **Create Web Service** dabayen. 2–3 minute mein build ho ke ek link mil
   jayega, jaisay: `https://shieldspam-ai.onrender.com`

Free plan par service thodi der (15 min) idle rehne par so jati hai aur agli
request par 30-50 second mein wake hoti hai — ye normal hai.

## Alternatives

- **Railway.app** — GitHub repo connect karen, "Deploy from Dockerfile"
  select karen, similarly ek public URL milta hai.
- **Fly.io** — `fly launch` chalayen is folder ke andar (Dockerfile
  auto-detect ho jayega), phir `fly deploy`.

## Aage kya

- Scoring ab poori tarah server-side hai (`backend/model.py`) — browser sirf
  UI dikhata hai aur `/api/score` ko call karta hai. Ye asal README wale
  architecture (MAUI client → FastAPI backend) se match karta hai, sirf
  MAUI ki jagah browser UI hai.
- Agar aap ka asal `model.py` ya C++ engine (`cpp_engine/parser.cpp`) ka
  logic use karna hai (jaise trained ML model), to wo files share karen —
  main unhe isi backend ke andar wire kar dunga.
