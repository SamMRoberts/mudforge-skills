---
name: mudforge-events-protocols
description: Implement or diagnose MudForge GMCP, MSDP, custom events, and session-scoped integrations with partial-data and reconnect handling.
---

# Events and protocols

Capture the actual package/variable name, payload shape, session ID, and update
order before choosing fields. Standard-looking names such as `Char.Vitals` do
not guarantee a server's schema. Read [protocol contracts](references/protocols.md).

Use session-scoped callbacks by default. Subscribe once per runtime, merge only
known partial fields, validate numeric input, and clear transient state on
disconnect. Preserve unknown/missing states rather than inventing default data.
Do not use the foreground-session flag as a connection test.

Adapt [session-vitals.lua](assets/session-vitals.lua) for independent session
state and GMCP/MSDP updates. Its terminal command provides synthetic data for
offline checks; a successful demo does not prove negotiation or transport.
Use namespaced `on`/`emit` for intra-session integration. Cross-session sends
or broadcasts need an actual requested cross-session use case.

Verify nil/partial/string-valued data, disconnect/reconnect, duplicate init,
and two sessions with different values. For mapper consumers, load the mapper
skill rather than equating every protocol room identifier with a local map ID.
