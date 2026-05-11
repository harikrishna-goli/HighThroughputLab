# HighThroughputLab

A hands-on performance engineering project to understand what it actually takes to move a backend API toward high-throughput goals under real load.

This repository focuses on a read-heavy financial use case (`POST /read/balance`) and incrementally improves architecture, runtime tuning, and CI-based benchmarking.

## Why this project exists

A common interview question is: _"How would you design a system for very high RPS?"_

Most answers stop at architecture diagrams (gateway, sharding, horizontal scaling, cache). This project goes one step further by validating those ideas through implementation, load testing, bottleneck analysis, and iterative tuning.

## Current scope

- FastAPI service with a read-only balance endpoint
- Sharded PostgreSQL backend (4 shards)
- Redis cache for account read acceleration
- Nginx reverse proxy with upstream retry and timeout tuning
- Gunicorn + Uvicorn workers for process-level concurrency
- Locust load testing (headless and UI modes)
- GitHub Actions workflow for repeatable cloud-based benchmark runs

> Note: Authentication hardening, encryption, and full write-path correctness are intentionally deferred while the project focuses on throughput and stability learning.

## Architecture at a glance

- **API layer**: FastAPI app (`FinancialApp-1MRps/app/main.py`)
- **Database layer**: 4 PostgreSQL shard containers (`postgres-shard-1` ... `postgres-shard-4`)
- **Shard routing**: deterministic routing by `user_unique_id` range in `database.py`
- **Cache layer**: Redis async client (`cache.py`) for hot account reads
- **Edge/proxy layer**: Nginx (`nginx.conf`) with health endpoint and upstream failover settings
- **Load generation**: Locust (`locustfile.py`)

## Repository structure

```text
.
├── FinancialApp-1MRps/
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── cache.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── init_db.py
│   ├── Dockerfile
│   └── requirements.txt
├── .github/workflows/loadtest.yml
├── compose.yaml
├── nginx.conf
├── locustfile.py
├── Dockerfile.loadtest
└── requirements-loadtest.txt
```

## API contract

### Health

- `GET /health`
- Response:

```json
{
  "status": "ok"
}
```

### Read balance

- `POST /read/balance`
- Request body:

```json
{
  "user_unique_id": "USER-0001",
  "PINCode": "000001"
}
```

- Success response:

```json
{
  "user_unique_id": "USER-0001",
  "balance": 1001.0
}
```

- Failure response: `401 Unauthorized` for invalid user/PIN combinations.

## Getting started (local)

### Prerequisites

- Docker + Docker Compose
- Git

### 1) Clone and configure

```bash
git clone https://github.com/harikrishna-goli/HighThroughputLab.git
cd HighThroughputLab
cp .env .env.local 2>/dev/null || true
```

This project already includes a default `.env` with required values:

- `DB_USER`
- `DB_PASSWORD`
- `DB_NAME`
- `REDIS_URL`
- `ACCOUNT_CACHE_TTL_SECONDS`

### 2) Start the stack

```bash
docker compose up -d --build
```

### 3) Verify readiness

```bash
curl -fsS http://localhost:8000/nginx-health
curl -fsS http://localhost:8000/health
```

### 4) Test the endpoint

```bash
curl -fsS -X POST http://localhost:8000/read/balance \
  -H "Content-Type: application/json" \
  -d '{"user_unique_id":"USER-0001","PINCode":"000001"}'
```

### 5) Stop everything

```bash
docker compose down
```

## Run load tests locally

### Headless mode

```bash
docker compose --profile loadtest run --rm locust \
  locust -f locustfile.py \
    --host http://nginx \
    --headless \
    --users 5000 \
    --spawn-rate 1000 \
    --run-time 1m \
    --csv /loadtest/results/loadtest \
    --html /loadtest/results/loadtest-report.html \
    --exit-code-on-error 1
```

Generated reports are saved under `results/`.

### UI mode

```bash
docker compose --profile loadtest up -d locust
```

Open `http://localhost:8089`.

## Run load tests in GitHub Actions

This repository includes a manual workflow: `.github/workflows/loadtest.yml`.

- Trigger with **Run workflow** in GitHub Actions
- Inputs:
  - `users`
  - `spawn_rate`
  - `run_time`
  - `api_replicas`
- Workflow behavior:
  - builds images
  - starts stack with scalable API replicas
  - runs stack stabilization checks
  - executes Locust headless
  - uploads artifacts (CSV, HTML report, logs)

## Performance tuning knobs

### API container (Gunicorn/Uvicorn)

Configured via `compose.yaml` and `FinancialApp-1MRps/Dockerfile`:

- `WEB_CONCURRENCY`
- `WORKER_CONNECTIONS`
- `MAX_REQUESTS`
- `MAX_REQUESTS_JITTER`
- `GUNICORN_TIMEOUT`
- `GUNICORN_KEEP_ALIVE`

### Database pool

Configured via environment variables used in `database.py`:

- `DB_POOL_SIZE`
- `DB_MAX_OVERFLOW`
- `DB_POOL_TIMEOUT`

### Nginx upstream behavior

Configured in `nginx.conf`:

- `proxy_next_upstream`
- `proxy_next_upstream_tries`
- `proxy_next_upstream_timeout`
- `proxy_connect_timeout`
- `proxy_send_timeout`
- `proxy_read_timeout`

## Milestones

Target roadmap:

- `1k RPS`
- `2k RPS`
- `5k RPS`
- `10k RPS`
- `16k RPS` (1,000,000 requests/min)

Current progress includes moving from a low initial baseline to stable multi-thousand RPS runs, with active work on reducing residual 504s and long-tail latency spikes under burst conditions.

## Known limitations (current phase)

- Single endpoint focus (`/read/balance`)
- Read-heavy benchmark profile only (write-path still pending)
- No advanced auth/security hardening in benchmark path yet
- CI environment constraints can influence absolute throughput numbers

## Future milestones

- Add write APIs with idempotency and correctness checks
- Improve backpressure, admission control, and graceful degradation
- Deep-tune DB pools and shard balancing under mixed traffic
- Extend observability (metrics, tracing, bottleneck attribution)
- Move toward stable `16k+ RPS` in CI and larger environments

## Contributing

Issues and suggestions are welcome. If you are experienced in performance engineering or distributed systems, feedback on architecture trade-offs, benchmark methodology, and tuning strategy is especially valuable.

## License

No license file is currently defined in this repository.

