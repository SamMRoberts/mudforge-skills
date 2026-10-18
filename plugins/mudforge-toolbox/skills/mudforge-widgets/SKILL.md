---
name: mudforge-widgets
description: Build and debug MudForge HTML and canvas widgets, reactive values, gauges, widget messages, responsive layout, and accessible controls.
---

# Widgets

Read [widget contracts](references/widgets.md) for creation, layout, visibility,
and events. Choose HTML for controls and structured text, canvas for drawing,
or the mapper skill for embedded map widgets. Use distinct widget names and
initial positions, then respect the user's saved arrangement.

- For bindings, gauges, HTML scripts, menus, and safe message exchange, read
  [HTML widgets](references/html-widgets.md).
- For drawing, fonts, images, and canvas state, read
  [canvas drawing](references/canvas.md).

Create stable markup once and push changing server text through text bindings.
Keep focus and scroll stable. Provide keyboard-operable controls, labels,
readable contrast, and waiting/error states. Treat received messages and action
data as input to validate before sending commands.

Adapt [reactive-vitals.lua](assets/reactive-vitals.lua) for a reactive HTML
binding example and [canvas-status.lua](assets/canvas-status.lua) for drawing.
The HUD's synthetic command is a demo entry point, not a transport test; remove
it when adapting to production. For ordinary health/mana bars prefer the gauge
library described in the HTML reference.

Use the events skill for protocol validation. Test clicks, keyboard focus,
resize/docking, partial updates, font changes, reload, and multi-world isolation
in native MudForge. If the installed build differs from the guide, report the
specific discrepancy; browser-only fixtures do not establish native support.
