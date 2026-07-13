---
title: "Sidenotes showcase"
date: "2026-07-13"
toc: true
tags: [design, typography]
---

This post exists to stress the margin-note layout. On a wide screen, notes
prefer the right margin. When several notes want the same vertical space, the
next one moves to the left margin instead of pushing the whole right column
down.[^right-first] That makes dense annotation feel more like a printed page:
the prose keeps its rhythm, the margins absorb the extra context, and the
reader can still scan the main text without jumping to the bottom.[^left-fallback]

[^right-first]: The first nearby note should claim the right margin. This one is
    just tall enough to occupy the right-side lane.

[^left-fallback]: This note is referenced in the same paragraph as the previous
    one. On a wide viewport it should appear in the left margin because the
    right margin is already occupied.

The collision rule should be local, not permanent. Nearby notes may continue in
the left lane while the right lane is still occupied, but the layout should
return to the right as soon as that margin has room. The point is not to balance
both sides evenly; it is to keep the closest available margin free of
overlap.[^still-local]

[^still-local]: This note can still fall left if the first right-side note is
    nearby enough. The ordinary-spacing examples below show the return case.

## A Narrow Cluster

Here is a tighter cluster with three notes near one another.[^cluster-one] The
first note should start on the right. The second note should use the left margin
if the first note is still occupying the right-side lane.[^cluster-two] A third
note gives the algorithm another chance to pick the lane with the least
collision pressure.[^cluster-three]

[^cluster-one]: This note has enough text to create a meaningful occupied area
    in the right margin.

[^cluster-two]: This is the sibling note in the cluster. It should not overlap
    the first note or push it away from its anchor.

[^cluster-three]: The third note confirms that the layout can continue after a
    local conflict without collapsing all subsequent notes into one side.

## Ordinary Spacing

Most posts will not have notes packed this tightly. With ordinary paragraph
spacing, sidenotes should quietly sit on the right and stay aligned with the
paragraph that introduced them.[^ordinary]

[^ordinary]: This is the common case: one note, enough vertical room, right
    margin placement.

That ordinary behavior matters more than the stress case. The fallback should
only become visible when the page needs it; a follow-up note close to a previous
right-side note may still use the left lane.[^ordinary-two]

[^ordinary-two]: A nearby follow-up note can move left because note seven is
    already sitting in the right margin.

## Wide Graph

Some material wants the whole field, especially diagrams, plots, and tables.
This block uses the `wide` shortcode so the graph spans both sidenote columns
and the central text measure on large screens.

{{< wide class="tufte-graph" >}}
<svg viewBox="0 0 1120 360" role="img" aria-labelledby="wide-graph-title wide-graph-desc">
  <title id="wide-graph-title">Example full-width graph</title>
  <desc id="wide-graph-desc">A sparse line graph spanning the margin columns and the main article column.</desc>
  <style>
    .axis { stroke: currentColor; stroke-width: 1.5; }
    .grid { stroke: currentColor; stroke-width: 0.6; opacity: 0.18; }
    .series-a { fill: none; stroke: currentColor; stroke-width: 3; }
    .series-b { fill: none; stroke: currentColor; stroke-width: 1.5; stroke-dasharray: 7 7; opacity: 0.7; }
    .label { fill: currentColor; font-size: 18px; }
    .small { fill: currentColor; font-size: 15px; opacity: 0.72; }
    .dot { fill: currentColor; }
  </style>
  <line class="axis" x1="70" y1="286" x2="1048" y2="286" />
  <line class="axis" x1="70" y1="46" x2="70" y2="286" />
  <line class="grid" x1="70" y1="226" x2="1048" y2="226" />
  <line class="grid" x1="70" y1="166" x2="1048" y2="166" />
  <line class="grid" x1="70" y1="106" x2="1048" y2="106" />
  <polyline class="series-b" points="70,248 170,232 270,218 370,196 470,178 570,164 670,142 770,126 870,104 970,92 1048,74" />
  <polyline class="series-a" points="70,268 170,238 270,246 370,198 470,206 570,146 670,158 770,112 870,128 970,78 1048,92" />
  <circle class="dot" cx="770" cy="112" r="4" />
  <circle class="dot" cx="970" cy="78" r="4" />
  <text class="label" x="70" y="26">A graph can use the margins when the argument needs width</text>
  <text class="small" x="78" y="326">draft</text>
  <text class="small" x="348" y="326">edit</text>
  <text class="small" x="628" y="326">review</text>
  <text class="small" x="908" y="326">publish</text>
  <text class="small" x="790" y="102">local peak</text>
  <text class="small" x="988" y="68">late peak</text>
</svg>
<p class="wide-caption">A deliberately sparse chart: it keeps the central prose narrow, but gives visual evidence enough room to breathe.</p>
{{< /wide >}}

## Other Article Furniture

The article chrome should still behave normally around footnotes. A list should
not disturb the note lanes:

- prose remains the primary column;
- notes remain outside the measure;
- mobile keeps footnotes at the bottom.

Code blocks should keep their full width inside the article column:

```js
const lane = rightMargin.isFreeAt(anchor) ? "right" : "left";
placeSidenote(note, lane, anchor);
```

And a final note at the end should still choose the right margin when nothing
nearby is competing for that space.[^final-note]

[^final-note]: End-of-post note, right margin by default.
