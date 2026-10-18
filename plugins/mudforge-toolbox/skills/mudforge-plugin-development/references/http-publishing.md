# HTTP integrations and repository publishing

Source: user-supplied official `mud-client-ai-plugin-guide.md`, sections 13,
16.5, and 16.6; reviewed 2026-10-18. These contracts are documented, not live-tested.

## HTTP

Only `http.get(url, headers?, callback?)` and
`http.post(url, body, headers?, callback?)` exist. URLs must be HTTPS; JSON bodies
must be explicitly encoded strings using `json.encode(table)`. Keep the callback
last and provide nil headers when omitted: `http.get(url, nil, callback)`, not
`http.get(url, callback)`.
The latter loses the reply because a function in the header slot is ignored.

The callback runs once with `(status, body, error)`. Any HTTP response, including
404/500, has nil error, so check status separately. Transport, permission, URL,
size, timeout, or rate failures have nil body and an error; status can be 0 or
a diagnostic code. After checking success, protect decoding with
`local ok, value = pcall(json.decode, body)`, then validate the decoded schema.
Successful decoding alone does not establish valid application data. Response
headers are unavailable. Callback errors are reported as plugin errors rather
than calling the callback a second time.

Requests have a 30s timeout, 10 MB response maximum, and up to five HTTPS
redirects. The web proxy limits each domain to 100 requests/minute and blocks
loopback/private/link-local/metadata/reserved destinations. Desktop/mobile use
native requests and allow private/LAN hosts, still behind permission checks.
Do not describe web-proxy blocking as a universal desktop restriction.

Permission is per installed plugin and domain; first contact prompts the user,
with session or persistent choices. Library requests use the consumer's scope;
package installation grants no HTTP permission. Handle refusal without retry
loops, avoid logging credentials, and never hard-code real tokens. Local-only
automation should need no network permission.

## Publishing plugins and libraries

A MudForge plugin repository is HTTPS static hosting with `plugins.json` and
raw Lua files; it is separate from a Codex plugin manifest. Prefer a schemaVersion
1 object containing repository name/description and a plugins array. Each plugin
listing includes stable id, name/version/author/description, category/tags, and
relative or absolute downloadUrl. Raw Lua is the normal format; a JSON record
with script is an export format. Omit invented rating/download statistics.

Keep listing id stable and bump listing version on changes: the listing owns
installed identity and update metadata for raw Lua; source metadata fills gaps.
Publish lowercase SHA-256 of the exact served bytes and recompute on every
change. Missing hashes fail the default integrity setting; a mismatch is refused
regardless of that setting. Web access requires cross-origin readability for
both index and files. Ordinary GitHub/GitLab repository URLs are rewritten to
raw hosts by the client, and relative file URLs resolve from that raw root.

Optional `libraries` listings share the index. Names must match require rules,
be no longer than 64 characters, and match the filename. Include downloadUrl,
version/author/description and exact-byte sha256; library source is capped at
256 KB and requires its own parseable `library` metadata table. Installed
libraries remain available offline in every world. Never claim a repository was
published merely because its index built successfully.

The guide's index builder, manifest, pnpm task, and deployment paths belong to
its client source tree. Inspect the actual repository before using them; do not
invent those commands in an unrelated plugin repository. Validate listing/source
metadata and hashes locally, then verify the served index and file bytes when
publication is authorized. Use a disposable client for install/update/reload
acceptance. For `.mfp` server-package consent, maps/layout, and uninstall
behavior, read [package contracts](../../mudforge-worlds-migration/references/formats.md).
