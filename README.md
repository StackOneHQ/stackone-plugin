# StackOne plugin

Give AI agents 30,000+ safe, token-optimized actions across Workday, SAP, Oracle + hundreds more.

This plugin connects your agent to StackOne's hosted MCP server. Install it once, sign in with your StackOne account, and the agent can search for and run actions across every connector linked to that account. The plugin works with Google Antigravity, Grok Build, Cursor, Claude Code, Codex and ChatGPT desktop.

StackOne is the AI Agent Integration Platform. Tool calling is safe and token-optimized: Defender, StackOne's safety model, screens every call in real time; Advanced Tool Search (ranked #1 for tool search accuracy on public benchmarks) and StackOne Query keep token usage and latency low. StackOne handles authentication, rate limiting, and multi-tenancy across every connector.

## Install

| Host | How |
|---|---|
| **Google Antigravity** | Run `agy plugin install https://github.com/StackOneHQ/stackone-plugin`. Open `/plugin` → **Installed** → **stackone** → **Sign in**, then ask “List my connected StackOne accounts.” |
| **Grok Build** | Clone this repository, then launch `grok --plugin-dir /path/to/stackone-plugin`. Open `/mcp`, select **stackone**, and sign in. |
| **Cursor** | Add the `stackone` server from [mcp.json](mcp.json) to the `mcpServers` object in `~/.cursor/mcp.json`, then sign in when prompted. |
| **Grok Bot** | If StackOne appears under Settings → Plugins → Marketplace, select **Add**. Availability depends on the shared Cursor catalog. |
| **Claude Code** | `/plugin marketplace add StackOneHQ/stackone-plugin` then `/plugin install stackone@stackone`. |
| **Codex / ChatGPT desktop** | `codex plugin marketplace add StackOneHQ/stackone-plugin` then `codex plugin add stackone@stackone`. |
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

### Try it with your connected apps

- “Which apps do I have connected through StackOne?”
- “Use StackOne to show me the five most recently updated records in a connected app.”
- “Help me update a record through StackOne. Show me the proposed change before saving it.”

In Antigravity, you can also type `/stackone-actions` and describe a task. The [workflow](skills/stackone-actions/SKILL.md) finds actions available to your account, uses their input schemas, and previews changes for approval.

## Authentication and data

- **Auth:** OAuth 2.1 with PKCE against `https://idp-api.stackone.com/api/auth`. The server takes either kind of client the host brings: a URL-based client ID backed by a client ID metadata document, or one from dynamic client registration. On first use your host opens the StackOne sign-in page. No API keys or secrets live in this repo.
- **Scopes:** `mcp`, `offline_access` (refresh tokens so you sign in once).
- **Network endpoints this plugin calls:** `mcp.stackone.com` (the MCP server) and `idp-api.stackone.com` (sign-in). Nothing else.
- **What runs locally:** nothing. No hooks, no scripts, no bundled binaries. The bundled skill is Markdown. StackOne runs the actions on its hosted MCP server.
- **Data:** actions run against the SaaS accounts you have linked in StackOne, under the permissions of that link. Privacy policy: <https://www.stackone.com/terms/privacy-policy/>. Terms: <https://www.stackone.com/terms/saas-terms/>.

## Repository layout

Each host reads its own manifest file, so the same facts appear a few times. `scripts/check-manifests.py` (run in CI) keeps them identical.

```
stackone-plugin/
├── .antigravity-plugin/plugin.json # Google Antigravity
├── .claude-plugin/plugin.json      # Claude Code (Grok Build accepts this too)
├── .claude-plugin/marketplace.json # lets the repo be added as a one-plugin marketplace
├── .grok-plugin/plugin.json        # Grok Build
├── .cursor-plugin/plugin.json      # Cursor (displayName, logo, category)
├── .codex-plugin/plugin.json       # Codex / ChatGPT
├── .agents/plugins/marketplace.json# Codex / ChatGPT desktop repo marketplace
├── mcp_config.json                 # server config read by Antigravity
├── mcp.json                        # server config read by Cursor
├── .mcp.json                       # server config read by Claude Code, Grok Build, Codex
├── skills/stackone-actions/SKILL.md # Connected-app workflow
├── assets/logo.png, logo.svg
└── scripts/check-manifests.py
```

## Releases

Release Please updates the version in each host manifest when it cuts a release from `main`. Marketplace listings follow each publisher’s review and update process.

For a listing in the Google Antigravity Marketplace, validate the plugin with `agy plugin validate .` and submit the released repository through [Google’s partner intake](https://antigravity.google/docs/build-plugins#publish-to-the-antigravity-marketplace).

## Links

- Docs: <https://docs.stackone.com>
- Connector catalog: <https://www.stackone.com/connectors>
- MCP Registry entry: `com.stackone/mcp`
- Support: <mailto:support@stackone.com>

MIT licensed.
