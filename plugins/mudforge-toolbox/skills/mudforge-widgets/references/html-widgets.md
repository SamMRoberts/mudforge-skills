# HTML widgets, bindings, and messages

Source: [official authoring guide](https://mudforge.org/docs/ai-plugin-guide.md),
sections 3–4 and 6; user-supplied guide reviewed 2026-10-18.

## Stable content and safe data

HTML lives in an iframe. Set `content` once with
`setWidgetProperty(id, "content", html)` and prefer reactive changes:

- `data-mud-bind="key"` with `setBoundValue(id,key,value)` or
  `setBoundValues(id, values)` inserts text; nil displays empty.
- `data-mud-bind-style="width:pct"` binds a style and
  `data-mud-bind-attr="title:tip"` an attribute. Event attributes, `style`, and
  `srcdoc` cannot be attribute-bound; bound URLs are checked.
- `bindWidgetVariable(id,key,name,scope?)` pushes now and on writes; default
  variables and `"global"` variables are separate, so match the writer's scope.
  `bindWidgetGMCP(id,key,package,path?)` pushes the current value and updates.
  `unbindWidget(id)` stops both kinds; unload ends all bindings.

Validate and derive values in Lua. Clamp percentages and reject zero/missing
maxima. Show unknown data explicitly and clear data on session changes. Keep
server text in text bindings; for generated markup use `escapeHTML(text)`, and
inside a script use `json.encodeForScript(value)` rather than `json.encode`.
In widget JavaScript, use `mudforge.escapeHTML` before assigning external text
through `innerHTML`. Links, styles, and commands remain distinct boundaries.

Replacing `content` replaces the entire document and cancels its timers and
animation callbacks. Bound values survive and are reapplied, but DOM state,
focus, listeners, and other script state are rebuilt. Prefer value updates.
Overflow gets the client's themed scrollbar automatically; mentioning
`scrollbar` in the widget's markup opts into managing its scrollbar styling.

## Gauge library

Prefer `gaugeHTML(options)` for ordinary health/mana/other bars. Concatenate its
markup into HTML content; each gauge needs a distinct `id`. Only `id` is
required. `label` supplies a screen-reader name; `showLabel=false` hides only
the visible label. `look="party"` or `"status"` follows that user-selected look;
other options can override it. Query `getGaugeCatalog()` for current style,
gradient, and palette choices; entries are records with `id` and `name`, not
bare strings. Avoid baking a catalogue into a plugin.

`setGauge(widget,id,value,max?)` updates in place; omitted max keeps its previous
value. `setGauges(widget,{ hp={value=50,max=100} })` updates several; pair tables
or bare values are also supported. Keep separate waiting/invalid-data text
rather than silently treating missing data as a valid percentage. Gauge values
survive content rebuilds, but rebuilding still discards other document state.
The binding asset is intentionally a custom binding demonstration, not the
recommended replacement for the gauge library.

## Widget JavaScript bridge

Use the iframe's `window.mudforge`, available from its first script line,
instead of `window.parent` or `window.frameElement`:

| Widget JavaScript | Lua side / behavior |
|---|---|
| `mudforge.send(event,data)` | `luamsg` callback receives `{event,data}`; plain JSON-style values only |
| `mudforge.onMessage(fn)` | Receives `sendWidgetMessage(id,data)`; one receiver |
| `mudforge.onProperty(name,fn)` | Receives a custom `setWidgetProperty(id,name,value)` as `fn(value,name)`; one receiver per name |
| `mudforge.showMenu(items,event)` | App-level menu; `menuselect` receives `id` and color `value`, `menuclose` reports dismissal |
| `mudforge.setAppearance(settings)`, `mudforge.setBorder(settings)` | Restyles this world's widget copy |

`"content"` replaces the document and cannot have a property receiver. Menus
accept label, separator, item, and color records. Messages and property changes
sent before receivers exist are not buffered. Register Lua `luamsg` handling,
install the widget's receivers, have the widget send `"ready"`, then push its
initial data from that handler. Repeat the handshake after content replacement.

The helper routes messages and appearance changes only to its world. Older
parent-window CustomEvents remain compatible but some lack world context and
can reach copies in other worlds; do not generate that pattern for new code.
These HTML-only calls warn and have no receiver on canvas widgets.

Native checks: verify the ready handshake, hostile text, malformed/unknown
actions, menu dismissal/selection, focus/scroll retention, reload, and identical
widget IDs in two worlds. Test transport separately from synthetic input.
