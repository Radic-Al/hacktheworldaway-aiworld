# Define purchasable materials, owned-stock matching, and sample prices

## Why

The cut list describes finished parts, while the shopping list must describe purchasable lumber and hardware. The current spec does not say how to convert between them or what makes an owned item a match. Without a rule, costs and purchase quantities can change unpredictably.

## Decide and document

- A small catalog of supported lumber and hardware with dimensions, units, and illustrative unit prices.
- A simple, deterministic rule that maps cut parts to catalog items; explicitly exclude offcut reuse and cutting optimization.
- Structured confirmation fields for owned item type, dimensions or catalog item, and quantity after any free-text entry.
- The matching and subtraction rule, including partial ownership and nonmatching stock.
- What the estimate excludes, such as tax, delivery, finishes, and tool purchases.

## Acceptance criteria

- A worked example shows the cut list, purchase quantities, and total before and after confirmed owned stock.
- A nonmatching owned item leaves the shopping list and total unchanged.
- The UI labels prices as examples and warns when the estimate exceeds the budget.

Source: [spec.md, owned materials and budget](https://github.com/Radic-Al/hacktheworldaway-aiworld/blob/main/spec.md#L24-L38).
