# Choose the HTML app architecture and prove OCI access

## Why

The demo needs a real OCI-backed AI request and server-side credentials. A standalone HTML file cannot safely hold those credentials. The team needs a deployment shape and a working endpoint before building around AI behavior.

## Decide and document

- HTML/CSS/JavaScript frontend and a small backend or serverless endpoint for OCI calls.
- OCI service, model, region, authentication method, and where server-side secrets are stored.
- The endpoint request and response shape, timeout, and visible error states.
- Demo hosting and who can access the OCI account during the hackathon.

## Acceptance criteria

- A minimal end-to-end request from the HTML frontend through the endpoint to OCI succeeds in the demo environment.
- No OCI secret is sent to the browser or committed to the repository.
- A failed or timed-out request returns a handled error and permits retry.
- If the app must be a single static HTML file, revise the live OCI requirement explicitly before implementation.

Source: [spec.md, lightweight implementation and done criteria](https://github.com/Radic-Al/hacktheworldaway-aiworld/blob/main/spec.md#L44-L51).
