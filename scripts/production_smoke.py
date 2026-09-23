import argparse
import json
import urllib.request


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("base_url", nargs="?")
    parser.add_argument("--base-url", dest="base_url_flag")
    args = parser.parse_args()
    value = args.base_url_flag or args.base_url
    if not value:
        parser.error("a base URL is required")
    base_url = value.rstrip("/")
    with urllib.request.urlopen(f"{base_url}/api/v1/health", timeout=10) as response:  # noqa: S310
        health = json.load(response)
    if health.get("status") != "ok" or not health.get("engine_version"):
        raise SystemExit("Health response is invalid")
    with urllib.request.urlopen(f"{base_url}/api/v1/health/ready", timeout=10) as response:  # noqa: S310
        readiness = json.load(response)
    if readiness.get("status") != "ready":
        raise SystemExit("Database schema is not ready")
    with urllib.request.urlopen(base_url, timeout=10) as response:  # noqa: S310
        if response.status != 200:
            raise SystemExit(f"Landing page returned {response.status}")
    print(json.dumps({"status": "ok", "checks": ["health", "database", "landing"]}))


if __name__ == "__main__":
    main()
