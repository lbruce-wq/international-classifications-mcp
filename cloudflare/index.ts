import { Container } from "@cloudflare/containers";

interface Env {
  MCP_CONTAINER: DurableObjectNamespace<ClassificationsContainer>;
}

export class ClassificationsContainer extends Container<Env> {
  defaultPort = 8000;
  sleepAfter = "1m";
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);
    if (url.pathname === "/" || url.pathname === "/health") {
      return Response.json({
        name: "International Classifications MCP",
        version: "0.3.1",
        status: "alpha",
        mcp_endpoint: "/mcp",
        deterministic: true,
        internal_ai_calls: false,
        national_census_geography: "out_of_scope",
      });
    }
    // Bump the stable instance name when the bundled immutable registry changes,
    // so an already-running Container cannot continue serving the previous image.
    const id = env.MCP_CONTAINER.idFromName("international-classifications-v6-hardening");
    return env.MCP_CONTAINER.get(id).fetch(request);
  },
} satisfies ExportedHandler<Env>;
