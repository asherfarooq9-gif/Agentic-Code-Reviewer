"""FastAPI app: GitHub webhook endpoint + health check + auto-review trigger."""
from __future__ import annotations

import json
import logging

from fastapi import BackgroundTasks, FastAPI, Request, Response
from fastapi.responses import HTMLResponse

from ..config import load_settings
from ..db.store import Store
from ..github.webhook import parse_pull_request_event, verify_signature
from .dashboard import DASHBOARD_HTML

logger = logging.getLogger("agentic_reviewer.api")


def process_pull_request(url: str) -> None:
    """Run a multi-agent review for a PR and post comments. Best-effort."""
    from ..agents.specialists import review_diff_multi
    from ..github.client import GitHubClient
    from ..github.diff_parser import parse_diff
    from ..github.review_poster import post_review
    from ..llm.ollama_client import OllamaClient

    try:
        settings = load_settings()
        gh = GitHubClient(settings.github_token)
        files = parse_diff(gh.fetch_diff(url))
        llm = OllamaClient(
            settings.ollama_host, settings.model_default, settings.model_deep
        )
        findings, _usage = review_diff_multi(files, llm)
        post_review(gh, url, findings)
        logger.info("Auto-review posted for %s (%d findings)", url, len(findings))
    except Exception:
        logger.exception("Auto-review failed for %s", url)


def create_app() -> FastAPI:
    app = FastAPI(title="Agentic Code Reviewer")

    @app.get("/healthz")
    def healthz() -> dict:
        return {"status": "ok"}

    @app.get("/", response_class=HTMLResponse)
    def dashboard() -> str:
        return DASHBOARD_HTML

    @app.get("/api/reviews")
    def api_reviews() -> dict:
        with Store(load_settings().db_path) as store:
            return {"reviews": store.list_reviews_with_counts()}

    @app.get("/api/reviews/{review_id}/findings")
    def api_findings(review_id: int) -> dict:
        with Store(load_settings().db_path) as store:
            findings = store.list_findings(review_id)
        return {
            "findings": [
                {
                    "file": f.file,
                    "line": f.line,
                    "severity": f.severity.value,
                    "category": f.category.value,
                    "message": f.message,
                    "suggested_fix": f.suggested_fix,
                    "confidence": f.confidence,
                }
                for f in findings
            ]
        }

    @app.get("/api/stats")
    def api_stats() -> dict:
        with Store(load_settings().db_path) as store:
            return {
                "total_reviews": store.count_reviews(),
                "total_findings": store.count_findings(),
                "by_severity": store.severity_distribution(),
            }

    @app.post("/webhook")
    async def webhook(request: Request, background: BackgroundTasks):
        settings = load_settings()
        body = await request.body()
        signature = request.headers.get("X-Hub-Signature-256")
        if not verify_signature(settings.webhook_secret, body, signature):
            return Response(status_code=401, content="invalid signature")

        if request.headers.get("X-GitHub-Event") != "pull_request":
            return {"status": "ignored", "reason": "not a pull_request event"}

        payload = json.loads(body or b"{}")
        event = parse_pull_request_event(payload)
        if event is None:
            return {"status": "ignored", "reason": "action not review-worthy"}

        background.add_task(process_pull_request, event["url"])
        return Response(status_code=202, content=f"review queued for {event['url']}")

    return app
