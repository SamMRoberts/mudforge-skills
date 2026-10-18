# Libraries and dependency resolution

Source: user-supplied official `mud-client-ai-plugin-guide.md`, sections 3 and
16; reviewed 2026-10-18. This is documentation evidence, not native acceptance.

`require(name)` accepts flat alphanumeric, underscore, or hyphen names, without
paths, dots, or extensions. Top-level names have a 64-character maximum; nested
library requires keep the character restriction but omit that length cap.
Each consuming plugin has an independent execution/cache; repeated or transitive
requires within it return the cached instance. Circular dependencies and missing
modules raise diagnostic errors; inspect those errors rather than adding globals.

Resolution prefers bundled/on-disk libraries, then editor-created user libraries,
then repository-installed libraries, then package libraries. Editor libraries
cannot replace bundled or disk files. Installed libraries are device-wide,
available offline in every world; package libraries persist per world.
Byte-identical package libraries share an entry; conflicting code under one
package-library name is refused. Diagnose the actual winning source before
changing code that appears not to reload.

Libraries get the same math/string/table implementations as plugins, plus
language built-ins, JSON, HTTP, and nested require. They lack send/echo, widgets,
timers, variables, protocols, sessions, io/os, and MUSHclient host APIs. Inject
only needed host functions through an explicit `lib.init({ ... })`. Library HTTP
inherits the consuming plugin's permissions. `print` goes to debug logs, not
the player's terminal. Raw table helpers exist inside libraries but are not
plugin globals; do not assume unrestricted standard Lua facilities.

The guide's §10 still describes obsolete library pattern differences, while
§16 explicitly says parity was restored. Use the focused §16 contract and verify
older client builds when relevant. Do not maintain a second regex-only utility
implementation solely to accommodate that stale paragraph.

Plugin Manager → Libraries → New library/Edit uses library mode. Save changes
the next load; **Save & Reload users** restarts enabled dependent plugins.
Expect their init hooks to reload saved state. A library returns its export table,
not a plugin table. Published libraries additionally need `library = { name,
version, description, author, license }` metadata; name must match the filename.
Local-only utilities need no publication metadata. See
[repository publishing](http-publishing.md).

Bundled helpers include `string` for extended text operations, `table` for table
utilities, `discord` for webhooks/polling, `sqlite` for read-only file inspection,
and `test-utils` for loader smoke checks. Discord polling requires injected
addTimer/removeTimer/echo and a live connection; start from onConnect and handle
refusal. Choose only dependencies needed for the requested behavior. See
[file input and SQLite](storage.md) before reading a database.
