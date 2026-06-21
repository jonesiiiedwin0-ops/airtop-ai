# GitHub Webhook Setup Guide for Airtop AI

This guide walks you through setting up GitHub webhooks to automate community engagement, notifications, and Airtop Agent triggers for your repository.

## Overview

The webhook handler enables:
- **Real-time Discord/Slack notifications** for stars, forks, PRs, and issues
- **Airtop Agent triggers** for automated workflows
- **Auto-labeling** of issues and PRs
- **Welcome messages** for new contributors
- **Community engagement tracking**

## Prerequisites

1. **GitHub Personal Access Token** (PAT)
   - Go to [GitHub Settings → Developer Settings → Personal Access Tokens](https://github.com/settings/tokens)
   - Create a new token with scopes: `repo`, `admin:repo_hook`
   - Save the token securely

2. **Deployment Environment** (choose one):
   - Docker + Docker Compose
   - Heroku, Railway, Render, or similar PaaS
   - Self-hosted VPS/Server

3. **Optional Integrations**:
   - Discord Webhook URL (for notifications)
   - Slack Webhook URL (for notifications)
   - Airtop API Key & Agent/Webhook IDs

## Step 1: Configure Environment Variables

Copy the example environment file and fill in your credentials:

```bash
cp .env.webhook.example .env.webhook
```

Edit `.env.webhook` with your values:

```env
GITHUB_WEBHOOK_SECRET=generate-a-random-secret-key
GITHUB_TOKEN=ghp_your_personal_access_token
DISCORD_WEBHOOK_URL=https://discordapp.com/api/webhooks/...
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
AIRTOP_API_KEY=your-airtop-api-key
AIRTOP_AGENT_ID=your-agent-uuid
AIRTOP_WEBHOOK_ID=your-webhook-uuid
```

### Generate a Webhook Secret

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

## Step 2: Deploy the Webhook Handler

### Option A: Docker Compose (Recommended)

```bash
docker-compose -f docker-compose.webhook.yml up -d
```

The service will be available at `http://localhost:8000`

### Option B: Direct Python Execution

```bash
pip install -r requirements-webhook.txt
python github-webhook-handler.py
```

### Option C: Heroku Deployment

```bash
# Create Procfile
echo "web: python github-webhook-handler.py" > Procfile

# Deploy
heroku create your-app-name
heroku config:set GITHUB_WEBHOOK_SECRET=your-secret
heroku config:set GITHUB_TOKEN=your-token
# ... set other env vars
git push heroku main
```

## Step 3: Expose Your Webhook Endpoint

If running locally or on a private network, use a tunneling service:

```bash
# Using ngrok
ngrok http 8000

# Using Cloudflare Tunnel
cloudflared tunnel --url http://localhost:8000
```

Note your public URL (e.g., `https://abc123.ngrok.io`)

## Step 4: Configure GitHub Webhook

1. Go to your repository: **Settings → Webhooks → Add webhook**

2. Fill in the webhook configuration:
   - **Payload URL**: `https://your-domain.com/webhook/github`
   - **Content type**: `application/json`
   - **Secret**: Paste your `GITHUB_WEBHOOK_SECRET`
   - **Which events would you like to trigger this webhook?**
     - Select: **Let me select individual events**
     - Check:
       - ✅ Watches (stars)
       - ✅ Forks
       - ✅ Pull requests
       - ✅ Issues
       - ✅ Issue comments
       - ✅ Pushes (optional)

3. Click **Add webhook**

## Step 5: Set Up Discord Notifications (Optional)

1. Go to your Discord server → Settings → Integrations → Webhooks
2. Click **New Webhook**
3. Name it "Airtop AI GitHub"
4. Copy the webhook URL
5. Paste it in `.env.webhook` as `DISCORD_WEBHOOK_URL`

## Step 6: Set Up Slack Notifications (Optional)

1. Go to [Slack API](https://api.slack.com/apps)
2. Create a new app → **From scratch**
3. Go to **Incoming Webhooks** → Activate
4. Click **Add New Webhook to Workspace**
5. Select your channel and authorize
6. Copy the webhook URL
7. Paste it in `.env.webhook` as `SLACK_WEBHOOK_URL`

## Step 7: Configure Airtop Agent (Optional)

If you want to trigger Airtop Agents on GitHub events:

1. Create an Airtop Agent in [Airtop Portal](https://portal.airtop.ai)
2. Generate a webhook for your agent
3. Get your API key from [API Keys](https://portal.airtop.ai/api-keys)
4. Fill in `.env.webhook`:
   - `AIRTOP_API_KEY`
   - `AIRTOP_AGENT_ID`
   - `AIRTOP_WEBHOOK_ID`

## Testing

### Test the webhook endpoint

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "healthy", "timestamp": "2024-01-15T10:30:00"}
```

### Test GitHub webhook delivery

1. Go to your webhook in GitHub: **Settings → Webhooks → Your webhook**
2. Scroll to **Recent Deliveries**
3. Click on a delivery to see the request/response
4. Or manually trigger by starring/forking the repo

### Test Discord notification

Star your repository and check your Discord channel for the notification.

## Troubleshooting

### Webhook not receiving events

- Verify the webhook URL is publicly accessible
- Check GitHub webhook delivery logs: **Settings → Webhooks → Recent Deliveries**
- Ensure firewall allows inbound traffic on your port

### Invalid signature error

- Verify `GITHUB_WEBHOOK_SECRET` matches in both GitHub and your `.env.webhook`
- Check server logs for signature mismatch errors

### Discord/Slack notifications not sending

- Verify webhook URLs are correct and still active
- Check if the webhook has been deleted or revoked
- Review server logs for HTTP errors

### Airtop Agent not triggering

- Verify API key is valid
- Check Agent ID and Webhook ID are correct
- Review Airtop portal for agent execution logs

## Monitoring

### View server logs

```bash
# Docker
docker-compose -f docker-compose.webhook.yml logs -f webhook-handler

# Direct Python
# Logs will be printed to console
```

### Monitor webhook deliveries

GitHub provides detailed delivery logs:
1. Go to **Settings → Webhooks → Your webhook**
2. Scroll to **Recent Deliveries**
3. Click each delivery to see request/response details

## Advanced Configuration

### Custom Labels

Edit `github-webhook-handler.py` in the `handle_issue_event()` function to customize auto-labeling logic:

```python
if any(word in title_lower for word in ["custom", "keyword"]):
    labels.append("custom-label")
```

### Custom Welcome Message

Edit the `welcome_message` in `post_welcome_comment()` function to customize the welcome text.

### Add More Integrations

The webhook handler is extensible. You can add:
- Email notifications
- Database logging
- Custom analytics
- Integration with other services (Jira, Linear, etc.)

## Production Deployment

For production use:

1. **Use a managed service**: Heroku, Railway, Render, or Fly.io
2. **Enable HTTPS**: Use Let's Encrypt or your hosting provider's SSL
3. **Monitor uptime**: Set up monitoring with Uptime Robot or similar
4. **Backup logs**: Store webhook logs for audit trails
5. **Rate limiting**: Implement rate limiting for API endpoints
6. **Error tracking**: Use Sentry or similar for error monitoring

## Security Best Practices

1. **Never commit `.env.webhook`** to version control
2. **Rotate secrets regularly**: Regenerate webhook secret and tokens periodically
3. **Use strong secrets**: Generate cryptographically secure random secrets
4. **Limit token scope**: Use minimal required permissions for GitHub token
5. **Monitor webhook deliveries**: Regularly check GitHub webhook logs
6. **Use HTTPS**: Always use HTTPS for webhook endpoints in production

## Support

For issues or questions:
- Check [Airtop Documentation](https://docs.airtop.ai)
- Review [GitHub Webhooks Guide](https://docs.github.com/en/developers/webhooks-and-events/webhooks)
- Check server logs for detailed error messages

## Next Steps

1. **Enhance README**: Make it more discoverable (see ENHANCEMENT_GUIDE.md)
2. **Create examples**: Add Python/Node.js SDK examples
3. **Write blog post**: Share your project on Dev.to, Hashnode, etc.
4. **Community engagement**: Respond quickly to issues and PRs
5. **Track metrics**: Monitor stars, forks, and contributor growth
