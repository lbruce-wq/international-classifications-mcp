# Production operations

The server logs every tool completion and failure with tool name, generated request ID and elapsed milliseconds. Cloudflare container logs are the operational source for per-tool p50, p95 and p99 aggregation and session/connection investigations.

Service objectives for warmed requests:

- availability: 99.9% monthly;
- p95 tool execution below 750 ms;
- p99 tool execution below 2 seconds;
- no unexpected MCP tool errors in the production regression sweep.

Container cold starts are tracked separately, with an objective below 8 seconds. Alert when the warmed p95 exceeds 750 ms for 15 minutes, the error rate exceeds 1% for five minutes, or a source-link check reports HTTP 404/5xx.

Clients may retry one failed read-only call after a connection reset with short randomized backoff. They must not retry malformed input or deterministic MCP errors. All tools are read-only and idempotent, so a single transport retry cannot duplicate an external action.

The scheduled source-link workflow runs weekly. HTTP 401/403 is reported as access-controlled; HTTP 404 and 5xx fail the check.
