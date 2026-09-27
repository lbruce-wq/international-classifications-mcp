from __future__ import annotations

import urllib.error
import urllib.request

from international_classifications_mcp.registry import list_classifications


def check(url: str) -> int:
    request = urllib.request.Request(url, headers={"User-Agent": "Impact-Engines-source-check/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status
    except urllib.error.HTTPError as error:
        return error.code


def main() -> None:
    failed = []
    for item in list_classifications():
        status = check(item.source_url)
        access = "access-controlled" if status in {401, 403} else "reachable"
        print(f"{status}\t{access}\t{item.id}\t{item.source_url}")
        if status == 404 or status >= 500:
            failed.append((item.id, status, item.source_url))
    if failed:
        raise SystemExit(f"Broken authoritative source links: {failed}")


if __name__ == "__main__":
    main()
