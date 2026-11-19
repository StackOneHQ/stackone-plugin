---
name: stackone-actions
description: Use StackOne to discover connected apps, look up records, or make a user-approved change in a connected account.
---

# Work with connected apps through StackOne

For “what do I have connected?”, call `stackone_list_accounts` and show the app and account names. If the list is empty, explain that the user needs to link an account in StackOne. If the tool requires sign-in, direct the user to the host’s StackOne sign-in control.

For a task in a connected app:

1. Describe the task to `stackone_search_actions`. Narrow by provider when the user names an app. Use the returned `available_accounts` to identify the destination. If several accounts fit and the request leaves the choice open, ask which one to use.
2. Build the request from the selected action’s `example_request` and `input_schema`. Keep the returned `action_id` and `session_id`, fill the required fields with real values, and pass the selected `stackone_account_id` when needed. Resolve a record by searching or listing it if the user supplied a name. Ask when multiple records match.
3. For a lookup, call `stackone_execute_action` and summarize the requested results. Honor filters, ordering, and limits supported by the action. If you cannot establish which records are most recent, say so. For a change, show the account, target and proposed values. Execute only after the user approves that specific change. A request for a draft ends at the preview.
4. Report what the tool confirmed, with the record link or ID when available. If a write times out, check the target before retrying to avoid applying the change twice.
