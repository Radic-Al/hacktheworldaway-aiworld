# Resolve form fields, validation, tools, and instruction-detail controls

## Why

The form and boundary rules leave several user-visible decisions open: what “fits their space” means, whether missing tools block generation, whether budget blocks or warns, and how skill level relates to simpler or more detailed instructions.

## Decide and document

- One unit system and currency, fixed table height, required form fields, defaults, and confirmation step.
- Whether to collect actual available-space dimensions or narrow the product promise to user-specified table dimensions.
- Exact validation for unsupported sizes and missing required tools; state whether either blocks generation.
- Budget behavior (recommended: warn, since prices are illustrative).
- One instruction-detail control used both before and after generation, or clearly separate skill and detail settings.
- What happens to a vague free-text idea: optional form prefill or simply a prompt that leads to the form.

## Acceptance criteria

- Every invalid or unsupported input has a clear message and next action.
- A supported input set reaches a confirmed form before generation.
- Changing instruction detail preserves all plan geometry and other inputs.

Source: [spec.md, product goal and user flow](https://github.com/Radic-Al/hacktheworldaway-aiworld/blob/main/spec.md#L3-L18).
