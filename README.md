# StackOne plugin

Give AI agents 30,000+ safe, token-optimized actions across Workday, SAP, Oracle + hundreds more.

This plugin connects your agent to StackOne's hosted MCP server. Install it once, sign in with your StackOne account, and the agent can search for and run actions across every connector linked to that account. One repo, one plugin, loads in Grok Build, Cursor, Claude Code, Codex and ChatGPT.

StackOne is the AI Agent Integration Platform. Tool calling is safe and token-optimized: Defender, StackOne's safety model, screens every call in real time; Advanced Tool Search (ranked #1 for tool search accuracy on public benchmarks) and StackOne Query keep token usage and latency low. StackOne handles authentication, rate limiting, and multi-tenancy across every connector.

## Install

| Host | How |
|---|---|
| **Grok Build** | `/marketplace` → find **stackone** → `i`. Or `grok plugin install stackone --trust`. Then `/mcp` → **stackone** → `i` to sign in. |
| **Cursor** | Marketplace → **StackOne** → Install, or `/add-plugin stackone`. Sign in when Cursor prompts. |
| **Grok Bot** | Settings → Plugins → Marketplace → **StackOne** → Add (available once the Cursor Marketplace listing is approved; Grok Bot uses the Cursor plugin catalog). |
| **Claude Code** | `/plugin marketplace add StackOneHQ/stackone-plugin` then `/plugin install stackone@stackone`. |
| **Codex / ChatGPT desktop** | `codex plugin marketplace add StackOneHQ/stackone-plugin` then `codex plugin add stackone`. The Plugins Directory listing follows once OpenAI review completes. |
| **Any MCP client** | Add `https://mcp.stackone.com/mcp` as a remote (Streamable HTTP) server. |

You need a StackOne account with at least one connected integration. Create one at [app.stackone.com](https://app.stackone.com).

## What it does

The server exposes four tools:

| Tool | What it does |
|---|---|
| `stackone_search_actions` | Describe a goal in plain language and get the matching actions across every connected integration (30,000+ actions, ranked by Advanced Tool Search). |
| `stackone_execute_action` | Run one of those actions with the arguments it returns. Write and destructive actions follow the host's approval flow. |
| `stackone_list_accounts` | List the accounts (Workday, Salesforce, Notion, Jira, …) linked to your session and their ids. |
| `stackone_submit_feedback` | Report a tool result that was wrong or unhelpful. |

Example prompts once connected:

- "List the accounts I have connected through StackOne."
- "Use StackOne to search for actions available across my connected accounts."
- "Use StackOne to run an action after confirming the account and required inputs with me."

## ChatGPT extension and submission ZIPs

Build the MCP-only submission with `python3 scripts/build-chatgpt-plugin.py`. It writes
`dist/stackone-chatgpt.zip` with the OpenAI manifest, MCP configuration and listing assets.
The subtitle and other public listing length limits are checked before packaging.

The native app variant uses `python3 scripts/build-chatgpt-plugin.py --extension` and writes
`dist/stackone-chatgpt-extension.zip`. Its server URL is
`https://mcp.stackone.com/mcp?extension=on&tool-mode=search_execute`. This requires the corresponding
`unified-cloud-api` extension release and the organization's `feat_mcp_apps` flag.
Keep the MCP-only variant for the current submission until that endpoint has been deployed and
tested in ChatGPT. Building a ZIP does not submit or publish it.

The native entrypoint (`stackone_open`) is declared by the MCP server. It opens the existing
grant-scoped account and action explorer from a global sidebar or a thread. Users can search
action descriptions, save useful actions locally, and copy task prompts that exclude account
IDs, inputs and results. Simple read actions can run in the app; writes and complex inputs use
guided chat with confirmation. Project tool-mode policy still applies, with guided chat when
individual tools are required. The same OAuth grant and action execution path apply.
Account linking, account administration and connector
configuration are future dashboard work requiring explicit management consent and live
per-resource authorization; the current extension does not expose those operations.

## Authentication and data

- **Auth:** OAuth 2.1 with PKCE and dynamic client registration against `https://idp-api.stackone.com/api/auth`. On first use your host opens the StackOne sign-in page. No API keys or secrets live in this repo.
- **Scopes:** `mcp`, `offline_access` (refresh tokens so you sign in once).
- **Network endpoints this plugin calls:** `mcp.stackone.com` (the MCP server) and `idp-api.stackone.com` (sign-in). Nothing else.
- **What runs locally:** the submission package contains manifests and listing assets. The optional extension loads a sandboxed MCP App from the server; saved connector/action IDs stay in browser storage. No account IDs, inputs or results are saved by that preference.
- **Data:** actions run against the SaaS accounts you have linked in StackOne, under the permissions of that link. Privacy policy: <https://www.stackone.com/terms/privacy-policy/>. Terms: <https://www.stackone.com/terms/saas-terms/>.

## Repository layout

Each host reads its own manifest file, so the same facts appear a few times. `scripts/check-manifests.py` (run in CI) keeps them identical.

```
stackone-plugin/
├── .claude-plugin/plugin.json      # Claude Code (Grok Build accepts this too)
├── .claude-plugin/marketplace.json # lets the repo be added as a one-plugin marketplace
├── .grok-plugin/plugin.json        # Grok Build
├── .cursor-plugin/plugin.json      # Cursor (displayName, logo, category)
├── .codex-plugin/plugin.json       # Codex / ChatGPT
├── .agents/plugins/marketplace.json# Codex / ChatGPT desktop repo marketplace
├── mcp.json                        # server config read by Cursor
├── .mcp.json                       # server config read by Claude Code, Grok Build, Codex
├── assets/logo.png, logo.svg
└── scripts/check-manifests.py
```

## Releases

Versions are cut by release-please from conventional commits on `main`. A release bumps `version` in every manifest at once; the Grok Build marketplace re-pins to the new commit automatically, Cursor and the Claude community catalog pick it up on their own schedule.

## Links

- Docs: <https://docs.stackone.com>
- Connector catalog: <https://www.stackone.com/connectors>
- MCP Registry entry: `com.stackone/mcp`
- Support: <mailto:support@stackone.com>

MIT licensed.
