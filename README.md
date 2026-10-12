# Q&A Agent deployable

Project FastAPI cho agent hỏi đáp sử dụng Google ADK + Gemini.

## Cài đặt

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Chạy local

```bash
python main.py
```

Server sẽ chạy trên http://localhost:8000

## API

### Health check

```bash
curl http://localhost:8000/health
```

### Chat

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Xin chào","user_id":"demo"}'
```

## Docker

```bash
docker build -t qa-agent .
docker run -p 8000:8000 --env-file .env qa-agent
```
