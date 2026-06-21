"""
GitHub Webhook Handler for Airtop AI Repository
Handles GitHub events and triggers automations:
- Discord/Slack notifications
- Airtop Agent triggers
- Auto-labeling and contributor welcome messages
"""

import os
import json
import hmac
import hashlib
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import httpx
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Airtop AI GitHub Webhook Handler")

# Environment variables
GITHUB_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "your-secret-key")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")
AIRTOP_API_KEY = os.getenv("AIRTOP_API_KEY", "")
AIRTOP_AGENT_ID = os.getenv("AIRTOP_AGENT_ID", "")
AIRTOP_WEBHOOK_ID = os.getenv("AIRTOP_WEBHOOK_ID", "")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

# Repository info
REPO_OWNER = "jonesiiiedwin0-ops"
REPO_NAME = "airtop-ai"


def verify_github_signature(request_body: bytes, signature: str) -> bool:
    """Verify GitHub webhook signature for security."""
    if not signature.startswith("sha256="):
        return False
    
    expected_signature = hmac.new(
        GITHUB_SECRET.encode(),
        request_body,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(
        signature[7:],  # Remove 'sha256=' prefix
        expected_signature
    )


async def send_discord_notification(embed: Dict[str, Any]) -> None:
    """Send notification to Discord webhook."""
    if not DISCORD_WEBHOOK_URL:
        logger.warning("Discord webhook URL not configured")
        return
    
    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                DISCORD_WEBHOOK_URL,
                json={"embeds": [embed]}
            )
        logger.info("Discord notification sent successfully")
    except Exception as e:
        logger.error(f"Failed to send Discord notification: {e}")


async def send_slack_notification(text: str, blocks: Optional[list] = None) -> None:
    """Send notification to Slack webhook."""
    if not SLACK_WEBHOOK_URL:
        logger.warning("Slack webhook URL not configured")
        return
    
    try:
        payload = {"text": text}
        if blocks:
            payload["blocks"] = blocks
        
        async with httpx.AsyncClient() as client:
            await client.post(SLACK_WEBHOOK_URL, json=payload)
        logger.info("Slack notification sent successfully")
    except Exception as e:
        logger.error(f"Failed to send Slack notification: {e}")


async def trigger_airtop_agent(config_vars: Dict[str, Any]) -> None:
    """Trigger Airtop Agent via webhook."""
    if not all([AIRTOP_API_KEY, AIRTOP_AGENT_ID, AIRTOP_WEBHOOK_ID]):
        logger.warning("Airtop configuration incomplete")
        return
    
    try:
        url = f"https://api.airtop.ai/api/hooks/agents/{AIRTOP_AGENT_ID}/webhooks/{AIRTOP_WEBHOOK_ID}"
        headers = {
            "Authorization": f"Bearer {AIRTOP_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "configVars": config_vars,
            "callbackConfig": {
                "url": "https://your-domain.com/airtop-callback",
                "headers": {"Authorization": f"Bearer {AIRTOP_API_KEY}"}
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
        
        logger.info("Airtop agent triggered successfully")
    except Exception as e:
        logger.error(f"Failed to trigger Airtop agent: {e}")


async def auto_label_issue(issue_number: int, labels: list) -> None:
    """Auto-label GitHub issues."""
    if not GITHUB_TOKEN:
        logger.warning("GitHub token not configured")
        return
    
    try:
        url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues/{issue_number}/labels"
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        async with httpx.AsyncClient() as client:
            await client.post(url, json=labels, headers=headers)
        
        logger.info(f"Issue #{issue_number} labeled with {labels}")
    except Exception as e:
        logger.error(f"Failed to label issue: {e}")


async def post_welcome_comment(issue_number: int, is_pr: bool = False) -> None:
    """Post welcome message to new issues/PRs."""
    if not GITHUB_TOKEN:
        logger.warning("GitHub token not configured")
        return
    
    endpoint_type = "pulls" if is_pr else "issues"
    welcome_message = """
## Welcome! 👋

Thank you for contributing to **Airtop AI**! We appreciate your interest in our project.

### Quick Links:
- 📖 [Documentation](https://docs.airtop.ai)
- 🐛 [Bug Report Template](https://github.com/airtop-ai/airtop-ai/issues/new?template=bug_report.md)
- ✨ [Feature Request Template](https://github.com/airtop-ai/airtop-ai/issues/new?template=feature_request.md)
- 📋 [Contributing Guidelines](https://github.com/airtop-ai/airtop-ai/blob/main/CONTRIBUTING.md)

We aim to respond to all issues and PRs within 72 hours. Happy coding! 🚀
"""
    
    try:
        url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/{endpoint_type}/{issue_number}/comments"
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        async with httpx.AsyncClient() as client:
            await client.post(url, json={"body": welcome_message}, headers=headers)
        
        logger.info(f"Welcome comment posted to {endpoint_type}#{issue_number}")
    except Exception as e:
        logger.error(f"Failed to post welcome comment: {e}")


@app.post("/webhook/github")
async def handle_github_webhook(request: Request):
    """Main GitHub webhook handler."""
    
    # Verify signature
    signature = request.headers.get("X-Hub-Signature-256", "")
    body = await request.body()
    
    if not verify_github_signature(body, signature):
        logger.warning("Invalid GitHub webhook signature")
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    event_type = request.headers.get("X-GitHub-Event", "")
    payload = json.loads(body)
    
    logger.info(f"Received GitHub event: {event_type}")
    
    # Handle different event types
    if event_type == "watch":
        await handle_star_event(payload)
    elif event_type == "fork":
        await handle_fork_event(payload)
    elif event_type == "pull_request":
        await handle_pr_event(payload)
    elif event_type == "issues":
        await handle_issue_event(payload)
    elif event_type == "issue_comment":
        await handle_comment_event(payload)
    
    return JSONResponse({"status": "received"})


async def handle_star_event(payload: Dict[str, Any]) -> None:
    """Handle repository star event."""
    action = payload.get("action", "")
    sender = payload.get("sender", {})
    repo = payload.get("repository", {})
    
    if action == "started":
        # Create Discord embed
        embed = {
            "title": "⭐ New Star!",
            "description": f"**{sender.get('login')}** starred the repository",
            "url": sender.get("html_url"),
            "color": 16776960,  # Yellow
            "thumbnail": {"url": sender.get("avatar_url")},
            "fields": [
                {
                    "name": "Repository",
                    "value": f"[{repo.get('full_name')}]({repo.get('html_url')})",
                    "inline": False
                },
                {
                    "name": "Total Stars",
                    "value": str(repo.get("stargazers_count", 0)),
                    "inline": True
                },
                {
                    "name": "Timestamp",
                    "value": datetime.now().isoformat(),
                    "inline": True
                }
            ]
        }
        
        await send_discord_notification(embed)
        
        # Trigger Airtop agent to analyze new stargazer
        await trigger_airtop_agent({
            "event": "new_star",
            "user": sender.get("login"),
            "user_url": sender.get("html_url"),
            "repo": repo.get("full_name")
        })


async def handle_fork_event(payload: Dict[str, Any]) -> None:
    """Handle repository fork event."""
    sender = payload.get("sender", {})
    repo = payload.get("repository", {})
    fork_repo = payload.get("forkee", {})
    
    embed = {
        "title": "🍴 New Fork!",
        "description": f"**{sender.get('login')}** forked the repository",
        "url": sender.get("html_url"),
        "color": 16711680,  # Red
        "thumbnail": {"url": sender.get("avatar_url")},
        "fields": [
            {
                "name": "Original Repository",
                "value": f"[{repo.get('full_name')}]({repo.get('html_url')})",
                "inline": False
            },
            {
                "name": "Fork Repository",
                "value": f"[{fork_repo.get('full_name')}]({fork_repo.get('html_url')})",
                "inline": False
            },
            {
                "name": "Total Forks",
                "value": str(repo.get("forks_count", 0)),
                "inline": True
            }
        ]
    }
    
    await send_discord_notification(embed)


async def handle_pr_event(payload: Dict[str, Any]) -> None:
    """Handle pull request event."""
    action = payload.get("action", "")
    pr = payload.get("pull_request", {})
    sender = payload.get("sender", {})
    
    if action == "opened":
        # Post welcome comment
        await post_welcome_comment(pr.get("number"), is_pr=True)
        
        # Auto-label as PR
        await auto_label_issue(pr.get("number"), ["pull-request"])
        
        embed = {
            "title": "🔀 New Pull Request",
            "description": pr.get("title"),
            "url": pr.get("html_url"),
            "color": 65280,  # Green
            "fields": [
                {
                    "name": "Author",
                    "value": sender.get("login"),
                    "inline": True
                },
                {
                    "name": "Branch",
                    "value": pr.get("head", {}).get("ref"),
                    "inline": True
                }
            ]
        }
        
        await send_discord_notification(embed)


async def handle_issue_event(payload: Dict[str, Any]) -> None:
    """Handle issue event."""
    action = payload.get("action", "")
    issue = payload.get("issue", {})
    sender = payload.get("sender", {})
    
    if action == "opened":
        # Post welcome comment
        await post_welcome_comment(issue.get("number"), is_pr=False)
        
        # Auto-label based on keywords
        labels = []
        title_lower = issue.get("title", "").lower()
        body_lower = issue.get("body", "").lower()
        
        if any(word in title_lower for word in ["bug", "error", "crash", "fail"]):
            labels.append("bug")
        if any(word in title_lower for word in ["feature", "enhancement", "request"]):
            labels.append("enhancement")
        if any(word in title_lower for word in ["question", "help", "how"]):
            labels.append("question")
        
        if labels:
            await auto_label_issue(issue.get("number"), labels)
        
        embed = {
            "title": "📝 New Issue",
            "description": issue.get("title"),
            "url": issue.get("html_url"),
            "color": 16711680,  # Red
            "fields": [
                {
                    "name": "Author",
                    "value": sender.get("login"),
                    "inline": True
                },
                {
                    "name": "Labels",
                    "value": ", ".join(labels) if labels else "None",
                    "inline": True
                }
            ]
        }
        
        await send_discord_notification(embed)


async def handle_comment_event(payload: Dict[str, Any]) -> None:
    """Handle issue/PR comment event."""
    action = payload.get("action", "")
    comment = payload.get("comment", {})
    sender = payload.get("sender", {})
    issue = payload.get("issue", {})
    
    if action == "created":
        embed = {
            "title": "💬 New Comment",
            "description": comment.get("body", "")[:200] + "...",
            "url": comment.get("html_url"),
            "color": 16776960,  # Yellow
            "fields": [
                {
                    "name": "Author",
                    "value": sender.get("login"),
                    "inline": True
                },
                {
                    "name": "Issue/PR",
                    "value": f"#{issue.get('number')}",
                    "inline": True
                }
            ]
        }
        
        await send_discord_notification(embed)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.post("/airtop-callback")
async def airtop_callback(request: Request):
    """Handle Airtop agent execution callback."""
    payload = await request.json()
    logger.info(f"Airtop callback received: {payload}")
    
    # Process callback results
    invocation_id = payload.get("invocationId")
    result = payload.get("result")
    
    logger.info(f"Airtop invocation {invocation_id} completed with result: {result}")
    
    return JSONResponse({"status": "processed"})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
