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
        version: "0.4.0",
        status: "alpha",
        mcp_endpoint: "/mcp",
        deterministic: true,
        internal_ai_calls: false,
        national_census_geography: "out_of_scope",
      });
    }
    if (url.pathname === "/provenance/mics7") {
      return Response.json({
        source_title: "UNICEF MICS7 standard questionnaires and response categories",
        source_version: "MICS7 responses 7.1",
        custodian: "UNICEF Multiple Indicator Cluster Surveys",
        retrieved_at: "2026-09-26",
        upstream_urls: [
          "https://mics.unicef.org/tools/MICS7",
          "https://mics.unicef.org/news/mics7-questionnaires-now-available-mics-website",
        ],
        access_note: "UNICEF's MICS website may return HTTP 403 to automated clients. This stable registry-hosted record preserves the exact upstream identity and version; UNICEF remains authoritative.",
        scope: "Curated question-specific response codelists only; no analytical indicators.",
      });
    }
    // Bump the stable instance name when the bundled immutable registry changes,
    // so an already-running Container cannot continue serving the previous image.
    const id = env.MCP_CONTAINER.idFromName("international-classifications-v7-codelists");
    return env.MCP_CONTAINER.get(id).fetch(request);
  },
} satisfies ExportedHandler<Env>;
