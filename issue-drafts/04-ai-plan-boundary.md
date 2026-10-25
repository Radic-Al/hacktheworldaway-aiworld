# Keep plan calculations authoritative when AI writes instructions

## Why

AI interpretation and prose generation could introduce dimensions or part labels that disagree with the calculated plan. The current spec requires consistency but does not define the contract at the AI boundary.

## Recommended contract

- Validate confirmed inputs, calculate a canonical plan in code, then generate the drawing, cut list, shopping list, and step references from that plan.
- Give AI fixed step IDs and the relevant canonical facts. Ask it only for explanation text and terminology appropriate to the selected detail level.
- Render dimensions, quantities, and part labels from the canonical plan rather than trusting AI prose to supply them.
- Define how to handle invalid or missing AI output, including a deterministic fallback if appropriate.

## Acceptance criteria

- Changing instruction detail does not alter part geometry, quantities, hardware, cost, or construction method.
- Every displayed step references valid part IDs; no AI-supplied measurement overrides the plan.
- A mocked malformed AI response has a defined user-visible outcome.

Source: [spec.md, consistency and AI implementation](https://github.com/Radic-Al/hacktheworldaway-aiworld/blob/main/spec.md#L20-L50).
