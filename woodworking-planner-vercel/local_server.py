"""Local demo server. No third-party Python packages are required."""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from planner import CATALOG, TOOLS, PlanError, build_plan


ROOT = Path(__file__).resolve().parent / "public"
MIME = {".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".svg": "image/svg+xml"}


def oci_settings():
    region = os.getenv("OCI_GENAI_REGION", "us-chicago-1").strip()
    model = os.getenv("OCI_GENAI_MODEL", "openai.gpt-oss-120b").strip()
    if not re.fullmatch(r"[a-z][a-z0-9-]{2,40}", region):
        raise RuntimeError("OCI_GENAI_REGION must be an OCI region identifier.")
    if not re.fullmatch(r"[A-Za-z0-9._:-]{2,100}", model):
        raise RuntimeError("OCI_GENAI_MODEL has invalid characters.")
    return {"region": region, "model": model, "configured": bool(os.getenv("OCI_GENAI_API_KEY"))}


def get_oci_note(plan):
    settings = oci_settings()
    key = os.getenv("OCI_GENAI_API_KEY", "")
    if not key:
        raise RuntimeError("OCI is not configured. Set OCI_GENAI_API_KEY on the server, or choose sample preview.")
    url = f"https://inference.generativeai.{settings['region']}.oci.oraclecloud.com/20231130/actions/v1/chat/completions"
    inputs = plan["inputs"]
    prompt = (
        "You are assisting with a prototype indoor dining-table plan. "
        "In 2-3 short sentences, interpret the user's idea and explain the order of the prescribed steps: "
        "measure, cut, dry fit, fasten the apron frame, attach the top, finish. "
        "Do not introduce new dimensions, parts, tools, cuts, load ratings, or claims of structural safety. "
        "Do not change or replace the deterministic plan. "
        f"User idea: {inputs['idea']}. Confirmed size: {inputs['length']:g} by {inputs['width']:g} inches. "
        f"Instruction detail: {inputs['skill']}."
    )
    body = json.dumps({"model": settings["model"], "messages": [{"role": "user", "content": prompt}], "temperature": 0.2, "max_tokens": 180}).encode()
    request = urllib.request.Request(url, data=body, headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            data = json.load(response)
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"OCI returned HTTP {exc.code}. Check the API key, region, model, and access policy.") from None
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError(f"OCI could not be reached: {exc.reason if hasattr(exc, 'reason') else 'request timed out'}. Retry without losing your inputs.") from None
    except json.JSONDecodeError:
        raise RuntimeError("OCI returned an invalid response. Retry the request.") from None
    try:
        note = data["choices"][0]["message"]["content"]
        if isinstance(note, list):
            note = " ".join(part.get("text", "") for part in note if isinstance(part, dict))
        note = " ".join(str(note).split())[:700]
        if not note:
            raise ValueError()
    except (KeyError, IndexError, TypeError, ValueError):
        raise RuntimeError("OCI returned no usable explanation. Retry the request.") from None
    return {"source": "OCI Generative AI", "model": settings["model"], "text": note}


class Handler(BaseHTTPRequestHandler):
    server_version = "WoodworkingPlanner/0.1"

    def _send(self, code, data, content_type="application/json; charset=utf-8"):
        body = json.dumps(data).encode() if isinstance(data, (dict, list)) else data
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' blob: data:; object-src 'none'; base-uri 'none'; form-action 'self'")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/config":
            self._send(200, {**oci_settings(), "tools": TOOLS, "catalog": CATALOG})
            return
        if path == "/api/health":
            self._send(200, {"ok": True})
            return
        name = "index.html" if path == "/" else path.lstrip("/")
        file = (ROOT / name).resolve()
        if not file.is_relative_to(ROOT) or not file.is_file() or file.suffix not in MIME:
            self._send(404, {"error": "Page not found."})
            return
        self._send(200, file.read_bytes(), MIME[file.suffix])

    def do_POST(self):
        if urlparse(self.path).path != "/api/plan":
            self._send(404, {"error": "Endpoint not found."})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length < 2 or length > 65536:
                raise PlanError("Plan request is empty or too large.")
            data = json.loads(self.rfile.read(length))
            plan = build_plan(data)
            mode = data.get("mode", "sample")
            if mode == "oci":
                plan["ai"] = get_oci_note(plan)
            elif mode == "sample":
                plan["ai"] = {"source": "Sample preview", "model": None, "text": "This preview uses the fixed plan steps and has not made an OCI request. Choose Live OCI when a Generative AI key is configured."}
            else:
                raise PlanError("Choose sample preview or live OCI mode.", "mode")
            self._send(200, plan)
        except json.JSONDecodeError:
            self._send(400, {"error": "Invalid JSON request."})
        except PlanError as exc:
            self._send(422, exc.as_dict())
        except RuntimeError as exc:
            self._send(502, {"error": str(exc), "field": "mode"})


def main():
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"Woodworking planner at http://{host}:{port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
