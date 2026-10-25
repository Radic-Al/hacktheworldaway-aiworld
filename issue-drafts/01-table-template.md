# Lock the table template and calculation examples

## Why

The MVP promises one rectangular table design, but `spec.md` does not yet define the construction, part geometry, or supported dimensions. The diagram, cut list, shopping list, and instructions cannot be checked for consistency until those choices are fixed.

## Decide and document

- Fixed finished height; allowed length and width range and increments.
- Construction and joinery method, top layout, leg and apron placement, and overhangs.
- Actual (not just nominal) material dimensions, part labels, hardware quantities, and required tools.
- Formulas for every adjustable part, plus relevant safety notes and the limits of a prototype plan.

## Acceptance criteria

- A template definition gives deterministic part dimensions and quantities for any supported length and width.
- Two worked table sizes list the expected parts, quantities, hardware, and dimensioned drawing labels.
- The examples agree across diagram, cut list, shopping list, and assembly steps.
- Out-of-range sizes have a stated validation message.

Source: [spec.md, product goal and plan output](https://github.com/Radic-Al/hacktheworldaway-aiworld/blob/main/spec.md#L3-L30).
