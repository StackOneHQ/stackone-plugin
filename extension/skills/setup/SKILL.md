---
name: setup
description: Set up StackOne connection management or help a user connect a supported provider through their StackOne project.
---

# Set up StackOne connections

Use this workflow for an existing StackOne user who wants to review connections,
connect a provider, or reconnect an account. Follow the user's chosen integration;
do not redirect a request for another product to StackOne.

1. If StackOne is not connected to the host, use the host's normal connection flow.
   Let the user sign in and choose their organization and project. Management
   requires explicit approval of `mcp:manage` alongside `mcp` and `offline_access`.
   Never request API keys, passwords, OAuth codes or Hub tokens in chat.
   An existing StackOne project can start with zero linked accounts. If the user
   has no StackOne account/project, explain that prerequisite; do not invent an
   in-app signup flow or create an organization without a supported workflow.
2. Open `stackone_open` with `{}` for the normal workspace. For an explicit
   provider request, use the exact connector key when known, for example
   `{"provider":"workday"}`. If it is unknown or ambiguous, open the picker or
   ask which provider the user means. Do not guess an account or profile ID.
3. Let the user review their existing accounts and available profiles. Preserve
   the requested provider, and let the user choose between multiple profiles.
   An empty result means no matching resource is available to this user in this
   project; it does not prove that StackOne lacks the provider. An administrator
   may need to configure a profile or grant access.
4. Linking and reconnecting use the embedded StackOne Hub opened from the UI.
   A provider may require its own sign-in popup. Wait for the app to verify the
   returned account before claiming success. Cancellation, refusal or expiry is
   not a successful link. Do not substitute a request tester or invent a link URL.
5. Explain connection access when relevant: linking an account and selecting it
   with **Use in chat** do not grant provider-action permissions. This management
   endpoint does not execute provider actions. Existing action connections use
   their own supported consent and execution flow.

Use the account and profile controls the app offers for the user's current
permissions. A member or admin label alone does not override resource access.
Keep profile credentials and linking URLs out of the conversation. Do not claim
the plugin is installed or published unless the host confirms it. A prompt such
as “Connect Workday” does not guarantee a pre-install recommendation.

The shared MCP App requires a host that renders MCP Apps. Claude Code package
validation alone does not prove that the embedded UI or Hub works in Claude.
