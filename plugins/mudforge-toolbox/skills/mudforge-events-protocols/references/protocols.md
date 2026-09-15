# Protocol and event contracts

Source: [authoring guide](https://mudforge.org/docs/ai-plugin-guide.md), sections
11–14; [GMCP settings](https://mudforge.org/#/docs/gmcp). Reviewed 2026-09-14.

| API | Meaning |
|---|---|
| `getGMCPData(packageName)` | Current session's cached package, possibly nil. No argument returns all packages. |
| `onGMCPUpdate(packageName, fn)` | Session-scoped `fn(data)`. |
| `sendGMCP(package, data)` | Sends through a connected transport; table data is JSON-encoded. |
| `onMSDPChange(name, fn)` | Session-scoped `fn(newValue, oldValue)`. |
| `onMSDPChangeGlobal(name, fn)` | All sessions; `fn(sessionId,newValue,oldValue)`. |
| `getSessionId()` | Current plugin session ID. |
| `getSessionGMCP(sessionName, package)` | Explicit cross-session cache lookup. |

Subscribe at init, optionally render the current cache, then handle updates.
Cached values can be stale after reconnect; show freshness separately if the
workflow depends on it. A scalar field omitted from a partial update retains
that session's prior value; an explicitly invalid field becomes unknown.
Do not carry values across connection lifetimes without an explicit reason.

Custom `on`/`emit` delivers synchronously within the session and includes the
sender. Cross-session `onGlobal`/`broadcast` also includes the sender. Guard
against event loops and use distinct names for source and derived events.
Do not invent a GMCP unsubscribe API; verify runtime unload behavior natively.

Transport acceptance requires a real connection, even when its peer is a local
fixture. Directly calling a callback verifies payload logic only. Keep raw logs
out of source control and redact authentication, private messages, and history.
