# Widget contracts

Sources: [plugins and HTML bindings](https://mudforge.org/#/docs/plugins) and
[authoring guide](https://mudforge.org/docs/ai-plugin-guide.md), sections 4–5.
Reviewed 2026-09-14.

`createWidget` accepts a table with `type`, distinct `name`, `title`, nested
`position={x,y}`, and `size={width,height}`. Top-level x/y do not position it.
`destroyWidget(id)` releases widget event handlers. Preserve user arrangement
where supported; do not force a new position on every data update.

Canvas calls act on the active widget. Call `setActiveWidget(id)` before each
draw batch, then `clear`, `drawRect`, or `drawText` without a widget-ID prefix.
Recompute drawing dimensions on the widget's `resize` event. `getWindowSize`
returns viewport dimensions; `windowResize` is a separate custom event.

HTML lives in a sandboxed iframe. Set `content` once with
`setWidgetProperty(id,"content",html)`. Use `data-mud-bind="key"` plus
`setBoundValue`/`setBoundValues` for text. `data-mud-bind-style="width:pct"`
changes a style; `data-mud-bind-attr="title:tip"` changes an attribute.
`bindWidgetVariable` and `bindWidgetGMCP` are useful for direct bindings; validate
and compute derived values in Lua. These mechanisms are documented online;
native behavior remains a separate acceptance gate.

HTML buttons can declare `data-mud-action`. The online docs describe `action`,
click, keydown, and submit events, but do not fully specify every payload field.
Use one fixed action per fixture or inspect the real payload before dispatching
multiple actions. Never guess a field and wire it to `send`. Prefer normal HTML
buttons so keyboard interaction is available.

External strings belong in text bindings, never concatenated markup. Treat
links, CSS values, and commands as distinct trust boundaries. Clamp percentages
and reject missing/zero maxima; display unknown data rather than a misleading
full bar. A disconnected or partial-data HUD must not retain another session's
values. Avoid full HTML replacement on each protocol update.
