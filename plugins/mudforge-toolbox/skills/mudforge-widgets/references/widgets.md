# Widget contracts

Source: [official authoring guide](https://mudforge.org/docs/ai-plugin-guide.md),
sections 4–5; reconciled with the user-supplied guide on 2026-10-18. Native
acceptance remains separate from documented support.

## Creation and layout

`createWidget(config)` returns the widget ID. Supported types are `canvas`,
`html`, and `map` (`renderMode` aliases `type`). Prefer nested
`position={x,y}` and `size={width,height}`. The detailed guide contract also
supports numeric top-level `x/y` when `position` is omitted, and `width/height`
when `size` is omitted; `height` alone is ignored. The supplied guide's opening
example and troubleshooting text conflict with that detailed contract about
`x/y`, so retain nested tables in examples rather than depend on the fallback.

IDs derive from plugin ID plus `name`, not `title` or a supplied `id`. Reusing a
name returns the existing widget; changing its type is reported. Distinct names
and initial positions prevent accidental reuse or overlap. `properties.content`
sets initial HTML; `template` is an HTML fallback. `appearance` overrides plugin
appearance defaults field by field. `zIndex` is clamped to 0–49; saved layering
wins on reload. `setWidgetZOrder(id, n)` can layer any widget in this world.

Saved placement and visibility belong to the player. Docked tiles own their
position and size: `moveWidget`/`resizeWidget` do not override docking. Reflow to
the actual available size. Phones adapt initial desktop geometry and remember
an arrangement independently from desktop. Widgets are moved/closed in phone
arrange mode; interactive widgets smaller than roughly 100×80 are hard to tap.
`hideWidget("terminal")` is refused on phones.

`showWidget(id)` respects a player's remembered closure. Use
`showWidget(id, true)` only for their explicit reopen action. Plain
`hideWidget(id)` is temporary; `hideWidget(id, true)` records the player's close
choice. `destroyWidget(id)` removes this world's copy, frees its handlers, and
keeps saved placement for recreation. Select a valid drawing target afterward.
`getWidgetProperty(id, "visible")` returns live visibility in this world.

## Events and geometry

Register with `registerWidgetEvent(id, type, callback)`; unregister one callback
or all of a type with `unregisterWidgetEvent(id, type, callback?)`. Events go
only to the plugin copy in the widget's world and carry `sessionId`, even when
several worlds use the same widget ID.

| Event | Useful fields |
|---|---|
| `click`, `doubleclick`, `mousedown`, `mouseup` | `x`, `y`, `button` (0 left, 1 middle, 2 right); HTML click also has target fields, `dataset`, `action`, `data` |
| `mousemove` | `x`, `y`, `buttons` |
| `keydown`, `keyup` | `key`, `code`, `mods`; keydown also `repeat` |
| `action` | `action`, `data`, `dataset`, `targetId`, `targetText`, `button` |
| `submit` | `formData` table |
| `resize` | `width`, `height`; HTML player resize has `source="html-player-resize"` |
| `move` | `x`, `y`, optional `source="player"` for finished player moves |
| `close` | Empty payload apart from common context; hides rather than destroys |
| `luamsg` | `event`, `data` from the HTML helper |
| `menuselect`, `menuclose` | `id`, optional `value` / empty payload |

Mouse/key events also carry `shiftKey`, `ctrlKey`, `altKey`, and `metaKey`.
Validate the action name and its data before dispatching; do not turn arbitrary
widget text into MUD commands. Prefer native HTML buttons for keyboard access.

Canvas resize fires when the surface changes, including docking and font
changes. HTML reflows automatically; to receive player resize events opt in
with `resizeEvents=true` in creation or `setWidgetProperty`. Those events do
not report initial size. All widgets can receive resize from `resizeWidget`.
Never answer a player resize with repeated `resizeWidget` calls. Use
`getWindowSize()` and the separate `windowResize` custom event for the viewport.
`widgetInfo` mostly reports creation-time metadata; prefer canvas size calls
for current drawing dimensions and the live visibility property above.

## Verification

Check explicit reopen after user closure, floating/docked resize, keyboard
activation, phone arrangement where available, and the same plugin in two
worlds. Verify that data, events, appearance changes, and closure affect the
intended world. Native resize/font and persistence behavior cannot be proved
by an isolated HTML fixture.
