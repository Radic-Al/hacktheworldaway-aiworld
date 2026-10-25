# Specify atomic regeneration, failure, retry, and print behavior

## Why

After the user edits dimensions, an OCI failure could leave the old plan next to new form values, implying they describe the same table. The spec says to preserve inputs and replace outputs together, but the exact state behavior is undecided.

## Recommended behavior

- Keep editable draft inputs separate from the last successfully generated plan.
- On success, publish the new diagram, lists, cost, and steps together.
- On failure, retain draft inputs and the previous plan, clearly labeled with its own dimensions and generation status; offer retry.
- Print only a successfully generated plan, with its matching dimensions, diagram, lists, and steps.

## Acceptance criteria

- A failed regeneration never displays a mixture of old and new plan outputs.
- Retry uses the user's latest confirmed draft inputs.
- The print view cannot silently print an out-of-date plan as if it matched edited inputs.

Source: [spec.md, regeneration and failure](https://github.com/Radic-Al/hacktheworldaway-aiworld/blob/main/spec.md#L40-L51).
