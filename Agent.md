# Maintainer reference

Local learning/demo app: Streamlit -> FastAPI -> Claude -> AWS Cloud Control API or CloudWatch Logs. See [README.md](README.md) for setup, limitations, and project origin.

## Source map

| File | Responsibility |
| --- | --- |
| [backend/api/main.py](backend/api/main.py) | `GET /` and `POST /chat`; unrestricted CORS. |
| [backend/core/processor.py](backend/core/processor.py) | Constructs an agent for each request and delegates processing. |
| [backend/core/aws_agent.py](backend/core/aws_agent.py) | Claude calls, tool dispatch, and result summaries. |
| [backend/config/aws_config.py](backend/config/aws_config.py) | dotenv loading, boto3 session, and STS identity check. |
| [backend/config/prompt.py](backend/config/prompt.py) | System instructions and summary template. |
| [backend/tools/tools.json](backend/tools/tools.json) | `aws_cloud_control` and `cloudwatch_logs` schemas. |
| [frontend/chat.py](frontend/chat.py) | Chat, session history, and requests to port 8000. |
| [requirements.txt](requirements.txt) | Runtime dependencies; no lockfile. |

## Execution flow

1. The frontend appends a user message and posts `message` and `history` to `/chat`.
2. The processor constructs an agent, initializes clients, and validates AWS through STS.
3. The agent appends the message again and calls `claude-haiku-4-5` with tool definitions.
4. Text blocks are collected; recognized tool blocks call AWS and then receive an additional Claude summary call.
5. Assistant text is appended to history; the API returns `response` and `updated_history`.

Both Claude call sites use `claude-haiku-4-5`, hardcoded in `backend/core/aws_agent.py`.

## Implemented tools

- `aws_cloud_control(operation, resource_type, identifier=None, properties=None, region="us-east-1")`: create, list, and read. Update/delete are in the schema but return a not-implemented error. Create returns a token without polling. Lists return up to five descriptions from the first page.
- `cloudwatch_logs(function_name, hours_back=1)`: filters `/aws/lambda/<function_name>` for `ERROR` in the session region and returns up to ten fetched events. No pagination or custom limit argument.

## Local commands

Run from the root after installing requirements and configuring `.env` from `.env.example`:

```bash
python -m uvicorn backend.api.main:app --reload --host 127.0.0.1 --port 8000
python -m streamlit run frontend/chat.py --server.address 127.0.0.1 --server.port 8501
```

Use separate terminals. Source checks: `python -m compileall -q backend frontend` and `python -m json.tool backend/tools/tools.json`.

## Boundaries

- `/chat` performs real provider calls and may create billable resources. Prefer mocks for development verification.
- Keep credentials, local assistant settings, environments, and caches out of Git.
- No authentication, enforced write approval, pagination, history trimming, or custom assume-role flow.
- Cloud Control's per-tool region defaults to `us-east-1`; CloudWatch uses `AWS_DEFAULT_REGION`. The system prompt hardcodes `us-east-1`.
- Cloud Control IAM actions use `cloudformation:`; resource handlers need underlying service permissions. See official guidance in the README.
- MCP integration is not implemented; `mcp` is not a current runtime dependency.
