"""Studio render worker — HTTP so Railway app-sleep wakes it per job.

POST /render   header x-cevg-internal: <CEVG_INTERNAL_TOKEN>
  body: a scene spec (see scene.py). Optional "job" id and "audio" (a path
  under the shared volume). Renders to <CEVG_STORAGE>/studio/<job>.mp4.
GET  /health   -> 200, used to wake the service and for Railway healthchecks.
"""
import os, json, time, traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import render

STORAGE = os.environ.get("CEVG_STORAGE", "/data")
TOKEN = os.environ.get("CEVG_INTERNAL_TOKEN", "")
PORT = int(os.environ.get("PORT", "8080"))


class H(BaseHTTPRequestHandler):
    def _send(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            return self._send(200, {"ok": True, "service": "studio"})
        self._send(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/render":
            return self._send(404, {"error": "not found"})
        if TOKEN and self.headers.get("x-cevg-internal") != TOKEN:
            return self._send(403, {"error": "forbidden"})
        try:
            n = int(self.headers.get("content-length", "0"))
            spec = json.loads(self.rfile.read(n) or b"{}")
            job = spec.get("job", f"job_{int(time.time())}")
            outdir = os.path.join(STORAGE, "studio")
            os.makedirs(outdir, exist_ok=True)
            out = os.path.join(outdir, f"{job}.mp4")
            audio = spec.get("audio")
            res = render.render_job(spec, out, audio)
            res["job"] = job
            self._send(200, res)
        except Exception as e:
            self._send(500, {"error": str(e), "trace": traceback.format_exc()[-800:]})

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    print(f"studio worker on :{PORT}  storage={STORAGE}", flush=True)
    ThreadingHTTPServer(("0.0.0.0", PORT), H).serve_forever()
