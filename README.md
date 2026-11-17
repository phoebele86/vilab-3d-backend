# vilab-3d-backend

API của **ViLab 3D**: FastAPI, PostgreSQL + pgvector, trợ giảng AI (RAG) và xử lý dữ liệu hóa học.

## Hệ thống gồm

- `vilab-3d-frontend`: giao diện React + Three.js
- `vilab-3d-backend`: API FastAPI, PostgreSQL + pgvector, RAG (repo này)
- `vilab-3d-assets`: file mô hình 3D `.glb`
- `vilab-3d-llm`: cấu hình model Qwen/bge-m3 qua Ollama và bộ đánh giá

## Yêu cầu

Python 3.12, Docker Desktop, Ollama (đã chạy `scripts/pull-models.sh` của repo `vilab-3d-llm`).
Clone repo `vilab-3d-assets` nằm cạnh repo này để backend phục vụ file 3D ở giai đoạn local.

## Cài đặt lần đầu

```bash
python3.12 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env               # đổi POSTGRES_PASSWORD, JWT_SECRET và DATABASE_URL cho khớp
docker compose up -d
alembic upgrade head
```

## Chạy

```bash
docker compose up -d
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

| Địa chỉ | Kết quả |
|---|---|
| `http://localhost:8000/docs` | Trang Swagger |
| `http://localhost:8000/api/v1/health` | `{"status": "ok"}` |
| `http://localhost:8000/api/assets/sinh/tim.glb` | File mô hình từ repo `vilab-3d-assets` |

## Kiểm tra code

```bash
ruff check .
ruff format --check .
pytest
```

## Cấu trúc

```
app/
├── main.py          # FastAPI app, CORS, local asset mount
├── core/            # config.py (settings from .env), database.py
├── models/          # SQLAlchemy models
├── api/v1/          # routers
└── services/        # llm.py (OpenAI-compatible client)
alembic/             # migrations
tests/
```

`requirements.txt` ghi tên thư viện, `requirements.lock.txt` ghi phiên bản chính xác đã cài
(`pip freeze > requirements.lock.txt` mỗi khi thêm thư viện).
