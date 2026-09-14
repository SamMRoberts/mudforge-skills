---
name: mudforge-widgets
description: Build and debug MudForge HTML, canvas, and enhanced-text widgets with reactive values, events, responsive layout, and accessible controls.
---

# Widgets

Read [widget contracts](references/widgets.md). Choose HTML for controls and
structured text, canvas for drawing, or enhanced-text for ANSI output. Use
distinct widget names and positions, and the user's existing layout conventions.

Create stable markup once. Feed changing server text through text bindings;
use bounded numeric values for style bindings. Keep focus and scroll stable
during updates. Provide keyboard-operable buttons, readable contrast, labels,
and a clear waiting/error state. Do not put development diagnostics into a
player-facing flow unless they help the user decide what to do.

Adapt [reactive-vitals.lua](assets/reactive-vitals.lua) for a reactive HTML HUD
and [canvas-status.lua](assets/canvas-status.lua) for active-widget drawing.
The HUD's synthetic command is an explicit demo entry point, not a transport
test. Remove demo commands when adapting it to a production feature.

For protocol payload validation, use the events skill. Test actual clicks,
keyboard focus, resize, partial updates, reload, and cleanup in native MudForge.
If binding/event APIs are absent in the installed build, report the discrepancy
instead of assuming a browser-only example proves support.
