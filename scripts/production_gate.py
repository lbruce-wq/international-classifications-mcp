from __future__ import annotations

import argparse
import asyncio
import json
import time
from pathlib import Path

from jsonschema import validate
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


async def run(url: str) -> dict:
    calls = successes = expected_errors = 0
    latencies = []
    async with streamable_http_client(url) as (read, write, _):  # noqa: SIM117
        async with ClientSession(read, write) as session:
            initialized = await session.initialize()
            tools = (await session.list_tools()).tools
            schemas = {tool.name: tool.outputSchema for tool in tools}

            async def call(name: str, arguments: dict, expect_error: bool = False):
                nonlocal calls, successes, expected_errors
                calls += 1
                started = time.perf_counter()
                result = await session.call_tool(name, arguments)
                latencies.append((time.perf_counter() - started) * 1000)
                if result.isError:
                    if expect_error:
                        expected_errors += 1
                        return None
                    raise AssertionError(f"Unexpected {name} error: {result.content}")
                if expect_error:
                    raise AssertionError(f"Expected {name} to reject {arguments}")
                validate(result.structuredContent, schemas[name])
                successes += 1
                return result.structuredContent

            catalogue = (await call("list_classifications", {}))["result"]
            for classification in catalogue:
                cid = classification["id"]
                await call("get_classification", {"classification_id": cid})
                roots = await call("browse_hierarchy", {"classification_id": cid, "limit": 500})
                await call(
                    "search_codes",
                    {"query": classification["acronym"], "classification_ids": [cid], "limit": 5},
                )
                codelists = (await call("list_codelists", {"classification_id": cid}))["result"]
                for codelist in codelists:
                    list_id = codelist["codelist_id"]
                    await call("get_code_definition", {"classification_id": cid, "code": list_id})
                    await call("validate_codes", {"classification_id": cid, "codes": [list_id]})
                    children = await call(
                        "browse_hierarchy",
                        {"classification_id": cid, "parent_code": list_id, "limit": 500},
                    )
                    await call(
                        "export_choice_list",
                        {"classification_id": cid, "codelist_id": list_id, "format": "simple"},
                    )
                    await call(
                        "export_choice_list",
                        {"classification_id": cid, "codelist_id": list_id, "format": "xlsform"},
                    )
                    first = children["result"][0]
                    await call(
                        "get_code_definition",
                        {"classification_id": cid, "code": first["code"]},
                    )
                    await call(
                        "validate_codes", {"classification_id": cid, "codes": [first["code"]]}
                    )
                    if len(roots["result"]) > 0:
                        assert any(item["code"] == list_id for item in roots["result"])

            routing = {
                "birth registration status": "BR.STATUS",
                "institutional sector of the agricultural holding": "WCA.HOLDING_SECTOR",
                "vaccination evidence source": "WHO.VAX.EVIDENCE",
                "child functioning difficulty scale": "WG.DIFFICULTY",
            }
            for prompt, expected in routing.items():
                response = await call(
                    "recommend_classifications", {"question_text": prompt, "limit": 20}
                )
                assert expected in {item.get("codelist_id") for item in response["recommendations"]}

            for name, arguments in (
                ("get_classification", {"classification_id": "not_real"}),
                ("search_codes", {"query": "x", "classification_ids": ["not_real"]}),
                ("search_codes", {"query": "x", "limit": 0}),
                ("browse_hierarchy", {"classification_id": "not_real"}),
                ("validate_codes", {"classification_id": "isic5", "codes": []}),
                (
                    "map_codes",
                    {
                        "source_classification_id": "isic4",
                        "target_classification_id": "isic5",
                        "codes": [],
                    },
                ),
            ):
                await call(name, arguments, expect_error=True)

    ordered = sorted(latencies)
    percentile = lambda p: ordered[min(int(len(ordered) * p), len(ordered) - 1)]
    return {
        "server_version": initialized.serverInfo.version,
        "calls": calls,
        "successful_schema_validated": successes,
        "expected_errors": expected_errors,
        "unexpected_errors": 0,
        "families": len(catalogue),
        "tools": len(tools),
        "latency_ms": {
            "median": round(percentile(0.50), 1),
            "p95": round(percentile(0.95), 1),
            "p99": round(percentile(0.99), 1),
            "maximum": round(max(ordered), 1),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="https://classifications.impactengines.ai/mcp")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = asyncio.run(run(args.url))
    rendered = json.dumps(result, indent=2)
    print(rendered)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
