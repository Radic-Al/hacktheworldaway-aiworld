# Benchline Woodworking Planner

A local hackathon MVP for one configurable indoor dining table. It follows the updated `spec.md` from `Radic-Al/hacktheworldaway-aiworld`. The form collects and confirms constraints before generating a plan. One deterministic project model supplies the dimensions, diagram, cut list, stock assignment, shopping list, tool list, and build steps.

## Run locally

Requires Python 3.10 or newer. No package installation or frontend build is needed.

```bash
cd woodworking-planner
python3 server.py
```

Open `http://127.0.0.1:8000`. Choose **Load demo**, review the inputs, confirm them, and generate a **Sample preview**. Change the length or width and repeat; the drawing, cuts, stock assignment, and steps are regenerated together. Change instruction detail to see the same design explained differently. Use **Print plan** for a browser print or PDF view.

The default server binds only to `127.0.0.1`. Set `PORT` to use another port. This is a local demo server, not a hardened public deployment.

## Enable a real OCI-backed request

The app selects **Sample preview** until `OCI_GENAI_API_KEY` is set on the server. Sample mode is clearly labeled and makes no OCI call. With a key present, **Live OCI** becomes available and is the default. A failed live request returns an error; the browser keeps all inputs for retry.

Configure a [Generative AI API key](https://docs.oracle.com/en-us/iaas/Content/generative-ai/api-keys.htm) for a supported model and region, then set these server-side environment variables:

| Variable | Purpose | Default |
| --- | --- | --- |
| `OCI_GENAI_API_KEY` | Secret Generative AI API key | unset |
| `OCI_GENAI_REGION` | OCI region identifier | `us-chicago-1` |
| `OCI_GENAI_MODEL` | Supported chat model name | `openai.gpt-oss-120b` |

The server sends a Chat Completions request to Oracle's [OCI Generative AI endpoint](https://docs.oracle.com/en-us/iaas/Content/generative-ai/openai-compatible-api.htm). It asks for a short interpretation and explanation of the fixed step sequence. AI text is displayed separately and cannot change dimensions, quantities, prices, or part IDs. The key is never sent to the browser or saved in this project. Confirm model availability and access in your tenancy before the live hackathon demo.

## Supported design

This prototype uses one fixed-height table template:

- Indoor rectangular dining table, 30 in high, 48–72 in long, 28–40 in wide.
- One 3/4 in plywood tabletop from a 48 × 96 in sheet.
- Four 4×4 legs, **actual** 3.5 × 3.5 in, cut to 29.25 in.
- Two long and two short aprons from 1×4 stock, **actual** 0.75 × 3.5 in. Aprons fit between legs; the tabletop overhang is 2 in on all sides.
- Pocket-hole screws join aprons to legs. Eight small angle brackets join the apron frame to the plywood top. The plan distinguishes 1/2 in top screws from 3/4 in apron screws.
- Lumber stock assignment uses a deterministic first-fit method and charges 1/8 in kerf per crosscut. It is feasible within the listed 8 ft stock units but is not a global cutting optimizer.
- Owned lumber reduces purchases **only** when its actual dimensions exactly match a complete catalog stock unit and the user confirms it. No offcuts or partial-board substitutions are counted. Hardware quantities are counted as individual pieces; remaining needs are rounded up to catalog pack sizes.
- Prices are illustrative USD sample data dated 2026-10-25, not retailer quotes. Tax, delivery, and tool purchases are excluded.

The template and limits are product assumptions for the demo. They have **not** been reviewed by a woodworking or structural expert. The generated plan is a prototype and makes no verified load-capacity or certification claim. Check the construction method, fasteners, stock condition, and finish instructions before any physical build.

## What the app does

- Captures an idea, dimensions, budget, tools, skill level, optional owned-material notes, confirmed item rows, and optional reference photos.
- Keeps photos in the browser session only. It does not upload, identify, or measure them.
- Requires a review and confirmation before generating.
- Blocks unsupported sizes and missing required tools with a concrete explanation.
- Produces one versioned plan object with stable part IDs shared by every view.
- Shows budget overruns and inventory items that were not counted.
- Regenerates the entire displayed plan after any constraint change.
- Produces a print-friendly manual with labeled diagrams, dimensions, cut list, shopping list, tool checklist, steps, checks, and safety notes.

## Verify

```bash
python3 -m unittest discover -s tests -v
```

The tests check part references, stock fit with kerf, inventory matching and cost arithmetic, dimension and skill changes, blocked inputs, and the OCI request boundary. HTTP smoke tests run where local socket binding is permitted; they skip in restricted execution environments.

## Files

- `planner.py` — deterministic table template, validation, stock allocation, costs, steps.
- `server.py` — local HTTP server, static files, server-side OCI request.
- `web/index.html`, `web/styles.css`, `web/app.js` — responsive UI, SVG drawing, print view.
- `tests/test_planner.py` — focused acceptance checks.

## Deferred

Arbitrary furniture, multiple designs or units, automatic photo identification, offcut matching, live retailer prices, accounts, collaboration, and structural certification. Public deployment also requires proper hosting, HTTPS, access control, and abuse protection.
