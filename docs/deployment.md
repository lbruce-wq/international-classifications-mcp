# Deployment

## Local container

```bash
docker build -t international-classifications-mcp .
docker run --rm -p 8000:8000 international-classifications-mcp
```

The MCP endpoint is `http://localhost:8000/mcp`.

## Cloudflare

Requirements:

- a Cloudflare account with Workers and Containers enabled;
- Wrangler authenticated interactively or through a scoped `CLOUDFLARE_API_TOKEN` environment variable;
- a custom domain if desired.

Review `wrangler.jsonc`, particularly the Worker name and custom-domain route, before deploying a fork.

```bash
npm install
npm run check
npm run deploy
```

Never commit Cloudflare tokens or account credentials. Repository CI does not deploy automatically; production deployment remains an explicit operator action.

After deployment, run the production gate three times:

```bash
python scripts/production_gate.py --url https://your-host.example/mcp
```
