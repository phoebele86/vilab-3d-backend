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
python -m scripts.seed_curriculum   # 195 bài lớp 6–9 và các mô hình 3D gắn với bài
python -m scripts.seed_molecules    # danh mục phân tử, tọa độ 3D sinh bằng RDKit
```

Hai script seed chạy lại nhiều lần không bị trùng dữ liệu. Sửa `data/curriculum/grade-*.yaml` hoặc
`data/molecules_catalog.csv` rồi chạy lại script tương ứng.

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
| `http://localhost:8000/api/assets/biology/heart.glb` | File mô hình từ repo `vilab-3d-assets` |

| API | Chức năng |
|---|---|
| `GET /api/v1/lessons?grade=&subject=&has_models=` | Danh sách bài học |
| `GET /api/v1/lessons/{slug}` | Chi tiết bài học kèm mô hình 3D, ví dụ `9-physics-8` |
| `GET /api/v1/molecules`, `GET /api/v1/molecules/{formula}` | Danh mục và dữ liệu 3D của phân tử |
| `POST /api/v1/chemistry/reaction` | Cân bằng phương trình, trả tọa độ hai vế và cách ghép nguyên tử |

Mã môn học: `physics`, `chemistry`, `biology`, `general`. Slug bài học có dạng `<lớp>-<môn>-<số bài>`,
ví dụ `8-biology-33`.

Mọi nội dung hiển thị cho học sinh (tên bài, tên chương, tên mô hình, tên bộ phận, tên chất) được lưu dạng
`{"vi": "...", "en": "..."}` để frontend chọn ngôn ngữ. Tiếng Việt là bắt buộc, các ngôn ngữ khác là bản dịch.

Lỗi nghiệp vụ trả về `{"detail": {"code": ...}}` (`invalid_formula`, `invalid_equation`, `unbalanceable`,
`unknown_molecule`, `unknown_lesson`) để frontend tự hiển thị thông báo tiếng Việt.

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
├── models/          # lessons, models_3d, molecules, reactions, problems
├── schemas/         # Pydantic request/response models
├── api/v1/          # routers: health, lessons, molecules, chemistry
└── services/        # lessons.py, llm.py, chemistry/ (parser, balancer, structure, reaction)
alembic/             # migrations
data/                # curriculum/grade-*.yaml, molecules_catalog.csv
scripts/             # seed_curriculum.py, seed_molecules.py
tests/
```

`requirements.txt` ghi tên thư viện, `requirements.lock.txt` ghi phiên bản chính xác đã cài
(`pip freeze > requirements.lock.txt` mỗi khi thêm thư viện).
