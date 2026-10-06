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

You need a StackOne account. Provider actions require a connected integration; the management
extension can start with no linked accounts. Create an account at [app.stackone.com](https://app.stackone.com).

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
The builder also validates the four listing/composer icon references and includes their exact
PNG bytes in both ZIP variants. Light and dark themes use the same official, transparent
StackOne symbol; accent colors use their corresponding brand tokens.

### Import the branded package

Upload the generated `dist/stackone-chatgpt.zip` through the plugin ZIP import flow. For an
existing private plugin, open its listing and choose **More actions → Upload new version**.
The full package includes `.codex-plugin/plugin.json` and every referenced asset. Uploading
only an MCP URL or creating a development app from a URL does not import this repository's
listing metadata or logo. Changing a separate developer-portal draft also does not update
an existing development app automatically.

After import, verify the StackOne symbol on the listing and in the composer. Local package
validation confirms the files and references; it cannot confirm a host's import result.
See [OpenAI's icon and import requirements](https://developers.openai.com/plugins/deploy/submission#icons-and-screenshots).

For a branding-only refresh, use the MCP-only ZIP. Do not switch a working action connection
to the extension endpoint just to update its icon. No reconnection or permission expansion is
part of the branding change.

The native app variant uses `python3 scripts/build-chatgpt-plugin.py --extension` and writes
`dist/stackone-chatgpt-extension.zip`. Its server URL is
`https://mcp.stackone.com/mcp?extension=on&management-only=on`. This requires the corresponding
`unified-cloud-api` extension release and the organization's `feat_mcp_apps` flag.
Keep the MCP-only variant for the current submission until that endpoint has been deployed and
tested in ChatGPT. Building a ZIP does not submit or publish it.

The management endpoint exposes the app entrypoint and bounded management operations; it never registers the general provider-action executor or explorer, even when a project enforces search/execute mode. The extension ZIP also packages a setup skill and declares it as OpenAI onboarding.

The native entrypoint (`stackone_open`) opens the StackOne management app from a global
sidebar or a thread:

- **Provider intent:** a known provider key such as `workday` opens the matching authorized accounts and profiles. Multiple profiles remain explicit choices. Unknown/unavailable providers do not silently open another provider. Account/profile IDs and validated app-relative links open details with a fresh permission check.
- **Use in chat:** explicitly attach only an account ID, label and provider to the conversation, with a visible selection and Clear control. This does not grant actions.
- **Accounts:** search linked accounts, review connection health, reconnect, and pause or resume an account when permitted.
- **Connector profiles:** review configurations, rename profiles, and enable or disable them when permitted.
- **Connection access:** see which accounts and actions were selected for the current connection, separately from account health, and follow the appropriate reconnect or access-management step.
- **Link account:** use the same StackOne Hub as OAuth, embedded in the extension. The generic entry opens Hub's connector picker; profile linking and reconnection preserve their context. New accounts use your authenticated identity. After verifying completion, the extension opens the account details. Provider sign-in may require a popup.
- **Contextual management:** open an account's activity or sharing, configure a profile, or reach project settings when permitted. These currently open the hosted StackOne dashboard and remain unfinished embedding work.

Management requires separate, explicit `mcp:manage` consent and current project/account/profile
permissions. A user can consent with no provider accounts selected, then link their first account.
Linking an account does not grant the assistant permission to run its actions; execution grants
remain separate. Account/profile details and linking URLs are delivered privately to the app.
Controls follow the user's current account and profile permissions. Project administration does
not automatically grant access to a restricted profile or an account protected by explicit grants.
Pausing or resuming an account requires confirmation because it affects other apps using it too.

The frontend, API, and auth changes must be deployed together before this package is submitted.
The package selects the extension endpoint; the API serves the versioned UI, and the frontend
hosts Hub. Updating or rebuilding this ZIP does not deploy those services.

Build the explicit Claude variant with `python3 scripts/build-chatgpt-plugin.py --extension --host claude`. It writes `dist/stackone-claude-extension.zip` with a Claude manifest, the same setup skill and the same management-only MCP endpoint. Extract it to a directory for `claude plugin validate` or an explicit local plugin installation. Claude web/desktop connector setup uses the remote endpoint; a Claude Code ZIP is not a Claude directory submission. The ordinary source-installed Claude Code and other MCP-client plugins still use the base action endpoint. Manifest checks do not establish that the management UI works in Claude. Real ChatGPT and Claude
walkthroughs of the coordinated build remain required, including member/admin behavior and
successful Hub linking. No full feature video of that build is available yet.

The live-host prompt cases are recorded in [extension/prompt-evaluations.json](extension/prompt-evaluations.json). Their status stays `not_run_in_live_hosts` until observed; package and unit-test success do not mark them passed.

See [OpenAI's extension documentation](https://developers.openai.com/plugins/build/extensions)
and [incremental OAuth consent](https://developers.openai.com/plugins/build/auth).

## Authentication and data

- **Auth:** OAuth 2.1 with PKCE and dynamic client registration against `https://idp-api.stackone.com/api/auth`. On first use your host opens the StackOne sign-in page. No API keys or secrets live in this repo.
- **Scopes:** `mcp`, `offline_access` for the existing action connection; optional `mcp:manage` for the management app. Opening management requests additional consent when needed.
- **Endpoints:** `mcp.stackone.com` (MCP) and `idp-api.stackone.com` (sign-in). The management app embeds Hub from `app.stackone.com`; configuration links open the hosted dashboard.
- **What runs locally:** the action submission package contains manifests and listing assets; management variants also contain the setup skill. The extension loads a sandboxed management app from the server. Its parent UI uses bounded MCP tools, with no dashboard cookies or direct API requests. Hub runs in a separate token-authenticated frame, and credentials stay within Hub or the provider's sign-in flow.
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
