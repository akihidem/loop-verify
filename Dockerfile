# loop-verify MCP server (HTTP transport).
#
# Note: the codex backend needs the `codex` CLI, which is NOT in this image — set a
# key-based backend for containers:
#   docker build -t loop-verify .
#   docker run --rm -p 8000:8000 \
#     -e LOOP_VERIFY_BACKEND=openai -e OPENAI_API_KEY=sk-... \
#     loop-verify
# The MCP endpoint is then reachable at http://localhost:8000/mcp
#
# Host-header note: this image binds 0.0.0.0 (below), which makes FastMCP disable the
# DNS-rebinding Host check by default — i.e. the container accepts ANY Host header. To
# restrict it to the host(s) clients actually use, set an allowlist:
#     -e LOOP_VERIFY_ALLOWED_HOSTS=myhost:8000   (or "*" to be explicit about open)
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
# Install the server deps plus the key-based backends (codex CLI isn't containerizable).
RUN pip install --no-cache-dir -r requirements.txt openai google-genai

COPY loop_verify ./loop_verify

ENV LOOP_VERIFY_HOST=0.0.0.0 \
    LOOP_VERIFY_PORT=8000 \
    LOOP_VERIFY_BACKEND=openai

EXPOSE 8000

CMD ["python", "-m", "loop_verify.server", "--transport", "http"]
