---
name: airtop-api-integration
description: Build or modify Airtop AI browser automation integrations with sessions, windows, page queries, and page interactions.
---

# Airtop API Integration

Use this skill when the task involves Airtop cloud browser automation, AI page queries, natural-language browser interactions, authenticated browser profiles, or human-in-the-loop login flows.

## Instructions

1. Identify the workflow goal: extraction, form automation, navigation testing, authenticated browsing, or browser-assisted agent work.
2. Inspect the target codebase for an existing Airtop client, SDK usage, session wrapper, or environment variable pattern before adding new abstractions.
3. Use `AIRTOP_API_KEY` from environment or the platform secret store. Do not hardcode credentials.
4. Prefer the official Airtop SDK for the project's language. Use REST only when the project already has a generic HTTP client layer or the SDK is unsuitable.
5. Model the browser workflow as explicit steps:
   - create or reuse a session,
   - open or select a window,
   - navigate,
   - interact or query,
   - validate the result,
   - close or persist the session.
6. Use page queries for extraction and state checks. Include a JSON schema when code needs reliable structured output.
7. Use page interaction methods sequentially. Wait after navigation, reloads, animations, and dynamic content changes.
8. Add tests around your wrapper logic and mock Airtop network calls unless the repository already has live integration testing conventions.
9. For manual validation, run a small end-to-end browser workflow only when credentials are available and the target site is safe to automate.

## TypeScript example

```ts
import { Airtop } from "airtop";

const client = new Airtop({ apiKey: process.env.AIRTOP_API_KEY });

const session = await client.sessions.create();
try {
  const window = await client.windows.create(session.data.id, {
    url: "https://example.com",
  });

  const result = await client.windows.pageQuery(session.data.id, window.data.windowId, {
    prompt: "Return the page title and one sentence describing the page.",
  });

  console.log(result.data);
} finally {
  await client.sessions.terminate(session.data.id);
}
```

## Python example

```python
import os
from airtop import Airtop

client = Airtop(api_key=os.environ["AIRTOP_API_KEY"])

session = client.sessions.create()
try:
    window = client.windows.create(session.data.id, url="https://example.com")
    result = client.windows.page_query(
        session.data.id,
        window.data.window_id,
        prompt="Return the page title and one sentence describing the page.",
    )
    print(result.data)
finally:
    client.sessions.terminate(session.data.id)
```

## Prompting patterns

- Give the AI page context before the task.
- State exact fields to extract.
- Include stop conditions for pagination or infinite scroll.
- Ask for JSON and provide a JSON schema when possible.
- Add examples for ambiguous or domain-specific values.

## Reliability checklist

- [ ] Missing `AIRTOP_API_KEY` fails with a clear setup message.
- [ ] Session cleanup runs in `finally` or equivalent cleanup hooks.
- [ ] Airtop IDs are logged only when they are not sensitive.
- [ ] Page query output is validated before persistence.
- [ ] Interactions are sequential and wait for expected page changes.
- [ ] Authenticated flows use approved persistent profiles or human-in-the-loop login.

## Troubleshooting

- `401` or authentication failure: check `AIRTOP_API_KEY` and secret injection for the current environment.
- Page query returns vague data: add page context, required fields, examples, and a JSON schema.
- Interaction targets the wrong element: narrow the element description, reduce viewport size, scroll the element into view, and retry sequentially.
- Workflow hangs after a click: wait for navigation or add an explicit delay for dynamic content.
- Authenticated page loses login state: verify the profile ID and whether the session was created with the intended persistent profile.
