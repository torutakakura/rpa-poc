# Repository Guidelines

## Project Structure & Module Organization
- `rpa-electron/` hosts the Electron shell and React UI; `src/` holds feature screens, `electron/` wraps the main process, and distribution artifacts land in `release/` and `dist-electron/`.
- `rpa-backend/` is the FastAPI service exposing automation endpoints; reusable step definitions live under `steps/`.
- `rpa-agent/` contains the Python JSON-RPC bridge executed by the desktop app; JSON templates stay in `rpa_operations.json` and sample workflows are under `workflow-samples/`.
- `rpa-mcp/` provides the Model Context Protocol tool surface for generating steps; refer to `docs/` for architecture and schema notes.

## Build, Test, and Development Commands
- Backend: `cd rpa-backend && uv sync` installs deps and `uv run uvicorn main:app --reload --host 127.0.0.1 --port 8000` serves APIs locally.
- Agent: `./rpa-agent/setup.sh` prepares the virtualenv; run `python rpa_agent.py --debug` for verbose stdio logs; bundle with `pyinstaller --onefile --name rpa_agent rpa_agent.py`.
- Electron client: `cd rpa-electron && pnpm dev` launches the Vite dev server alongside the Electron main process; `pnpm build` emits production assets and `pnpm dist` packages installers.
- Docker stack: `docker-compose up -d` starts Postgres, backend, and UI images; use `docker-compose exec backend python -m alembic upgrade head` to apply migrations.

## Coding Style & Naming Conventions
- Python modules use 4-space indentation, `snake_case` filenames, and type hints; format with `uv run black .` and lint via `uv run ruff check`.
- Frontend code follows TypeScript strictness, React components in `PascalCase`, hooks in `camelCase`; run `pnpm exec prettier --check .` and `pnpm exec eslint .`.
- Tailwind utility ordering should follow class-merge defaults; keep shared UI in `rpa-electron/src/components/`.

## Testing Guidelines
- Backend automation tests are manual today; validate `GET /healthz` and workflow endpoints after changes and capture logs in PRs.
- The MCP tool ships an integration harness: `cd rpa-mcp && python test_json_integration.py` verifies template generation.
- Use `workflow-samples/*.json` to replay end-to-end flows through the agent; document scenario coverage in PR notes until automated suites arrive.

## Commit & Pull Request Guidelines
- Recent history uses concise lowercase `wip` or `wip: detail` messages; prefer `wip: <scope>` during iterative work and squash to descriptive titles before merging.
- Open PRs with context, reproduction steps, and configuration snippets; attach screenshots or terminal traces for UI and automation changes.
- Link Notion tasks or GitHub issues when available, and flag downstream impacts (agent binary rebuild, workflow schema changes).
