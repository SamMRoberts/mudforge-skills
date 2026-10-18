# Canvas drawing

Source: [official authoring guide](https://mudforge.org/docs/ai-plugin-guide.md),
sections 4–5 and 19–20; user-supplied guide reviewed 2026-10-18.

## Target, dimensions, and fonts

Call `setActiveWidget(id)` before each drawing pass, especially from events and
timers or with multiple widgets. Creation automatically activates a new canvas,
but explicit selection makes later callbacks safe. Selecting an unknown ID
leaves the previous target active; do not keep drawing after a failed target
lookup. Draw only onto a canvas, not HTML.

Use preferred signatures without an ID prefix:
`drawRect(x,y,w,h,color,strokeColor?)`,
`drawText(text,x,y,color,font?)`, and `clear(color?)`. The guide says older
ID-prefixed forms remain in the shared base API while its hard rules call them
wrong/obsolete; emit the cleaner active-widget forms for new code without
claiming all compatibility calls were removed.

Read current dimensions with `getCanvasSize()` or width/height accessors after
selecting the target. Before measurement they return the supplied creation
size; without one they return placeholder 400×300 and warn. Draw initially,
then redraw on `resize` for player changes, docking, and font loading.

Omitting `drawText`'s font uses the widget's font. For measurement or variants,
use `getWidgetFont(id)` returning `{ family, size, weight, css }`, then pass the
same `css` to drawing and `measureText`. Hardcoded fonts override the player's
settings. `measureText` does not inherit the widget font itself; `setFont`
affects only `drawTextWrapped`, not `drawText` or `measureText`.
`getWidgetSettings(id?)` is a detached copy of saved customization, possibly
nil before world setup; it is not a replacement for the complete font returned
by `getWidgetFont`.

## Drawing and state

Colors are CSS strings; origin is top left, y increases downward, and angles
are radians. Use documented shape calls such as `drawLine`, `drawCircle`,
`drawPolygon`, `drawPath` (a Lua array of SVG command strings), or
`drawGradient(x,y,w,h,direction,color1,color2)`. Do not infer overloads from a
browser canvas API.

Draws are queued and flushed once per animation frame automatically. There is
no `startBatch`/`endBatch`. State changes apply in order: balance `save/restore`
around `translate`, `rotate`, `scale`, alpha, and blend changes.
`setClipRegion` saves and intersects the clip; `resetClipRegion` restores that
state, including transforms made after the clip. `clear()` is transparent;
`clear(color)` fills opaque. It drops queued draws and ignores transforms and
fill alpha, but respects the clip and preserves drawing state.

`loadImage` does not need an active widget; `drawImage` does. Draw only a loaded
image ID or a supported direct source. Use the optional `drawImage` alpha,
angle, source rectangle, and pivot parameters rather than inventing separate
alpha/rotation functions. Allow asynchronous loading and supply SVG dimensions
or explicit drawing size when required.

Do not generate runtime-absent `drawRadialGradient`, `drawTab`, `drawTabGroup`,
`drawTextAligned`, `drawTextWithShadow`, `drawImageAlpha`, `drawImagePart`,
`drawImageRotated`, `getPixel`, `setPixel`, or `clearWidget`.
`drawRectOn` is an inert warning stub; select a target and call `drawRect`.

Native checks: switch targets before callbacks, resize/dock, change font family
and size, and reload. Exercise asynchronous images and balanced clipping/state
only when the feature uses them; offline mocks cannot prove rendering.
