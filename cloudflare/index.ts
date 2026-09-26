import { Container } from "@cloudflare/containers";

interface Env {
  MCP_CONTAINER: DurableObjectNamespace<ClassificationsContainer>;
}

export class ClassificationsContainer extends Container<Env> {
  defaultPort = 8000;
  sleepAfter = "10m";
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);
    if (url.pathname === "/" || url.pathname === "/health") {
      return Response.json({
        name: "International Classifications MCP",
        version: "0.1.0",
        status: "alpha",
        mcp_endpoint: "/mcp",
        deterministic: true,
        internal_ai_calls: false,
        national_census_geography: "out_of_scope",
      });
    }
    const id = env.MCP_CONTAINER.idFromName("international-classifications-v2");
    return env.MCP_CONTAINER.get(id).fetch(request);
  },
} satisfies ExportedHandler<Env>;
