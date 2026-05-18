# AI Hairstyle Service

AI‑powered virtual hairstyle try‑on API built with **FastAPI** and **Google Gemini 3.1 Flash Image** (Nano Banana 2).  
Upload a selfie, specify a hairstyle, and get a photorealistic transformed image in seconds.

[![Live Demo](https://img.shields.io/badge/Live_Demo-ai--haircut.onrender.com-0A66C2?style=flat-square)](https://ai-haircut.onrender.com/docs)
[![Docs](https://img.shields.io/badge/Swagger_Docs-85EA2D?style=flat-square&logo=swagger&logoColor=black)](https://ai-haircut.onrender.com/docs)
[![Python](https://img.shields.io/badge/Python-3.10_|_3.11-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.6-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Gemini](https://img.shields.io/badge/Gemini_3.1_Flash_Image-4285F4?style=flat-square&logo=google&logoColor=white)](https://deepmind.google/technologies/gemini/flash/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com/)

---

## ✨ Features

- **Single & Batch Mode** – Generate one hairstyle at a time or up to 6 in a single request.
- **Preserves Identity** – Gemini 3.1 Flash Image keeps face, skin tone, and background untouched.
- **OpenAPI Documentation** – Interactive Swagger UI at `/docs`.
- **Async & Concurrent** – Batch generation processes multiple styles in parallel.
- **Rate Limited** – Built‑in protection against abuse (adjustable via `.env`).
- **Docker Ready** – Deploy anywhere with a single command.


---

## 🚀 Live API

| Endpoint | Description |
|----------|-------------|
| `POST /api/v1/try-on` | Single hairstyle generation |
| `POST /api/v1/try-on-batch` | Generate multiple hairstyles (3–4 styles recommended) |
| `GET /api/v1/health` | Health check |
| `/docs` | Interactive Swagger UI |
| `/redoc` | ReDoc documentation |

**Base URL:** `https://ai-haircut.onrender.com`

---

## 🛠️ Tech Stack

| Layer          | Technology                                      |
|----------------|-------------------------------------------------|
| **Framework**  | FastAPI (Python 3.10+)                         |
| **AI Model**   | Google Gemini 3.1 Flash Image (Nano Banana 2)  |
| **Concurrency**| `asyncio` + `ThreadPoolExecutor`               |
| **Validation** | `Pillow` + `imghdr`                            |
| **Logging**    | `loguru` (coloured console + JSON support)     |
| **Rate Limit** | `slowapi` (per‑IP)                             |
| **Deployment** | Docker + Render.com (or any VPS)               |

---

## 📁 Project Structure

```
ai-hairstyle-service/
├── app/
│   ├── main.py                      # FastAPI entry point
│   ├── routers/
│   │   └── tryon.py                 # API endpoints
│   ├── services/
│   │   └── gemini_client.py         # Gemini API client
│   ├── models/
│   │   └── schemas.py               # Pydantic models
│   └── utils/
│       ├── validators.py            # Image validation
│       ├── rate_limiter.py          # Rate limiting
│       └── logging_config.py        # Loguru setup
├── config/
│   └── settings.py                  # Environment‑based config
├── tests/
│   ├── test_health.py
│   └── test_tryon.py
├── .env.example                     # Environment template
├── requirements.txt                 # Python dependencies
├── Dockerfile                       # Container definition
├── docker-compose.yml               # Local orchestration
└── README.md                        # This file
```

---

## 🔧 Quick Start (Local)

### 1. Clone & Enter

```bash
git clone https://github.com/maksudrakib44/ai-haircut.git
cd ai-haircut
```

### 2. Set Up Environment

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

### 3. Add Your Gemini API Key

Edit `.env` and set:
```ini
GEMINI_API_KEY=your_actual_gemini_key
```
> Get a key from [Google AI Studio](https://aistudio.google.com/).

### 4. Run the Server

```bash
uvicorn app.main:app --reload
```

API will be available at `http://localhost:8000`.

---

## 🐳 Docker (Easy Deploy)

```bash
docker build -t ai-haircut .
docker run -p 8000:8000 -e GEMINI_API_KEY=your_key ai-haircut
```

---

## 📡 Example API Calls

### Single Hairstyle

```bash
curl -X POST "http://localhost:8000/api/v1/try-on" \
  -F "image=@selfie.jpg" \
  -F "style=pixie cut" \
  --output result.jpg
```

### Batch Hairstyles (Short, Medium, Long)

```bash
curl -X POST "http://localhost:8000/api/v1/try-on-batch" \
  -F "image=@selfie.jpg" \
  -F "styles=short,medium,long" \
  --output results.json
```

Response:
```json
{
  "success": true,
  "message": "Generated 3 hairstyles",
  "generated_images": [
    {
      "style_key": "short",
      "style_description": "short hairstyle, cropped, pixie cut or bob",
      "image_base64": "/9j/4AAQSkZJRg...",
      "mime_type": "image/jpeg"
    }
  ],
  "total_processing_time_ms": 12500
}
```

Frontend can decode `image_base64` and display using `Image.memory()` (Flutter) or `<img src="data:image/jpeg;base64,...">`.

---

## ⚙️ Configuration (`.env`)

| Variable                   | Default              | Description                        |
|----------------------------|----------------------|------------------------------------|
| `GEMINI_API_KEY`           | `(required)`         | Your Google Gemini API key         |
| `ALLOWED_EXTENSIONS`       | `jpg,jpeg,png`       | Allowed image formats              |
| `MAX_IMAGE_SIZE_MB`        | `5`                  | Max upload size in megabytes       |
| `RATE_LIMIT_PER_MINUTE`    | `10`                 | Requests per minute per IP         |
| `LOG_LEVEL`                | `INFO`               | `DEBUG`, `INFO`, `WARNING`, `ERROR`|
| `LOG_FORMAT`               | `json`               | `json` or coloured console         |
| `API_HOST` / `API_PORT`    | `0.0.0.0` / `8000`   | Server binding                     |

Full template available in `.env.example`.

---

## 🌍 Deployment

### Render (Free Tier)

1. Push your code to GitHub.
2. Create a new **Web Service** on [Render](https://render.com).
3. Connect your repository.
4. Set `GEMINI_API_KEY` as an environment variable.
5. Deploy.

> Free instances spin down after 15 minutes of inactivity – the first request after a pause may take 30–50 seconds (cold start).

### Any VPS (Docker)

```bash
docker pull maksudrakib44/ai-haircut:latest
docker run -d -p 8000:8000 -e GEMINI_API_KEY="your_key" --restart unless-stopped maksudrakib44/ai-haircut:latest
```

### Traditional (Nginx + Gunicorn + Systemd)

See the detailed guide in the repository wiki or the deployment section below.

---

## 🧪 Testing

```bash
pytest tests/
```

Manual health check:
```bash
curl http://localhost:8000/api/v1/health
# Expected: {"status":"healthy","service":"ai-hairstyle","version":"2.0.0"}
```

---

## 🤝 Contribution Guide (For Teams)

This repository supports a **three‑role** workflow:

| Role       | Main Files/Folders                           |
|------------|----------------------------------------------|
| **AI** (You) | `app/services/`, `config/settings.py`, `app/routers/tryon.py` |
| **Backend**  | `app/routers/` (excluding `tryon.py`), `app/models/`, `database/` |
| **Frontend** | `mobile/`, `lib/`, `assets/`                 |


## 👤 Author

**Md. Maksudul Haque**  
[GitHub](https://github.com/maksudrakib44)  

---

## 🙏 Acknowledgments

- Google Gemini team for the image‑to‑image model.
- FastAPI and Uvicorn communities.
- Render for the generous free tier hosting.

---
## ⭐ Support

If this project helps you, please **star** the repository on GitHub and share it with others. Your support keeps the development going!
