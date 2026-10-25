# AI Woodworking Planner: Hackathon MVP Specification

## Product Promise and Target User

Turn an idea into a woodworking project the user can build with their tools, space, and budget.

The first user is a beginner or intermediate DIY builder who wants a simple indoor dining table and needs help translating an idea into consistent dimensions, materials, cuts, and assembly instructions. Success means producing one coherent plan whose drawings, cut list, and instructions describe the same object.

## MVP Scope

Support one configurable family of rectangular, fixed-height indoor dining tables using a single predefined construction system. Dimensions and material choices must stay within the template's documented bounds and supported catalog.

Before implementation, select and document the construction template, its dimension bounds, actual material sizes, compatible fasteners, required tools, and evidence supporting those limits. An AI-generated template is not automatically validated.

Include the constraint interview, one configurable design, geometry-derived diagrams, materials and cuts, tool checks, cost/time estimates, available-materials input (text or photos), skill-level adjustments, and a print-friendly manual.

Defer arbitrary furniture generation, outdoor/folding/extendable designs, multiple construction systems, photorealistic variants, live retailer pricing, globally optimized stock cutting, accounts, community, and marketplace features. The MVP does not establish certified structural or weight-capacity claims.

## 1. User Onboarding & Idea Capture
When a user enters a simple idea (e.g., "I want to build a dinner table"), the app must NOT immediately generate a plan. Instead, it must interactively prompt the user for the following key constraints:
* **Budget:** Amount and currency. A rough tier is acceptable initially, but clarify the amount before comparing estimates with a budget.
* **Purpose & Environment:** Confirm indoor dining use. Explain that outdoor, folding, and other unsupported designs are outside the MVP.
* **Dimensions & Space:** Desired length, width, height, seating needs, available space, and preferred units. Weight-capacity requests may be recorded as intent but must not become verified load-rating claims.
* **User Skill Level:** (Beginner, Intermediate, Advanced)
* **Available Tools:** (e.g., hand tools only, basic power tools like a circular saw and drill, or a full workshop with table saw and router)

**Available Lumber and Parts:** Let the user describe owned materials in text or upload photographs. Require confirmation of actual dimensions, quantities, material type, and usable condition before including stock in a plan. Photos assist capture; do not infer exact measurements or structural suitability from an image alone. Unsupported or unconfirmed stock is listed separately and is not counted as usable inventory.

Ask only for missing or ambiguous information and preserve answers when constraints change. Capture currency and supported material preferences. Confirm indoor dining use and explain unsupported requests.

Show a constraint summary for confirmation before generation. Clarify conflicting requirements instead of inventing an answer. If a request cannot fit the supported template, explain the conflict and propose a concrete revision; never silently exceed the budget or supported dimension bounds.

## 2. Core Feature Specifications
Once constraints are gathered, the app must generate a cohesive project proposal featuring:
* **Visual Design:** A dimensioned overview and assembly diagrams derived from the supported project's geometry. Future AI concept images must be labeled illustrative and must not serve as construction drawings.
* **Material Calculation:** A cut list specifying supported materials, actual dimensions, quantities, hardware, and estimated costs. Calculate finished parts separately from a feasible stock allocation, accounting for saw kerf, trim allowance, and stated waste assumptions. Separate usable stock the user already owns from materials and hardware that must be purchased. Do not claim globally optimal cutting.
* **Tool Check:** A required and optional tools checklist based on what the user owns versus what the project demands.
* **Labor & Time Estimates:** Estimated active build time, curing/drying time (for finishes), and total project timeline.

### Calculation and Estimate Rules

- Distinguish nominal lumber labels from actual dimensions used in calculations.
- Normalize calculations to one internal unit system; define conversion tolerance and display precision.
- Reject cuts that do not fit their allocated stock, including kerf and allowances.
- Use a local sample price catalog with currency, catalog date, and source or sample-data label. Calculate totals from quantities and unit prices; state exclusions such as tax, delivery, and tool purchases.
- Allocate each confirmed owned stock item at most once, accounting for prior cuts, kerf, and remaining usable dimensions. Purchase quantities cover only the shortfall; show owned items separately from the purchase subtotal.
- Mark missing prices as incomplete rather than zero. Disclose budget overruns.
- Separate active work from waiting time. Use the selected glue/finish product's documented waiting times or explicitly mark them unresolved.
- If a required tool is unavailable, offer only a supported alternative or block readiness until the constraint changes.

## 3. Step-by-Step "IKEA-Style" Manual
The core deliverable is an ultra-clear, sequential instruction manual. Each step must include:
* **Action & Cut Details:** Exact instructions (e.g., "Cut 4 pieces of 2x4 lumber at 36 inches").
* **Tool Assignment:** Which specific tool to use for that step.
* **Safety Precautions:** Highlighted safety warnings (e.g., "⚠️ Always wear safety glasses and ear protection when operating the miter saw").
* **Visual Diagrams:** Geometry-derived drawings for that assembly phase, labeled with the same part IDs as the cut list.
* **Prerequisites & Completion Check:** What must be done first and how the builder can check the step before continuing.

Distinguish cutting, dry fitting, assembly, and finishing. Generated warnings do not prove a design safe. Unsupported requests, invalid geometry, or missing required tools prevent publication as a ready-to-build plan.

### Adjust Skill Level and Regenerate

After viewing a plan, the user can increase or decrease the requested skill level and request a new iteration. Preserve the other confirmed constraints, adjust explanation detail and supported techniques, and revalidate the entire plan. Skill changes do not permit unsupported construction systems or bypass tool requirements. If no supported adaptation fits, explain the limitation. Show the new revision consistently across the manual, diagrams, parts, and estimates.

## 4. Generation Architecture and Shared Project Model

Use this pipeline:

`Confirmed constraints → AI maps intent to supported template parameters → deterministic calculations and validation → shared project model → diagrams, lists, and instructions`

The AI interprets requests and explains the plan. Deterministic code owns dimensions, quantities, stock allocation, cost arithmetic, and validation. Validate AI output against the schema and supported catalog before calculating or rendering a plan.

All outputs derive from one versioned model. Each part has a stable ID, material reference, quantity, and actual dimensions. Cuts, diagrams, and steps reference those same IDs. Tool and hardware references resolve to catalog entries. A constraint edit creates a new revision and invalidates dependent outputs; never mix revisions.

Define a machine-validated schema containing at least:

| Field | Purpose |
| --- | --- |
| `schemaVersion`, `planId`, `revision` | Identify the data contract and exact plan revision. |
| `constraints` | Confirmed budget, currency, units, space, dimensions, skill, tools, and purpose. |
| `templateId`, `templateVersion` | Identify the construction system and its supported bounds. |
| `materials`, `parts`, `hardware` | Catalog references, stable IDs, actual dimensions, and quantities. |
| `availableInventory` | Confirmed owned materials/hardware, quantities, actual dimensions, condition, and text/photo provenance. |
| `stockAllocation` | Owned and purchased stock, assigned cuts, remaining stock, kerf, and allowances. |
| `steps` | Ordered actions, part/tool/hardware references, prerequisites, and completion checks. |
| `diagrams` | Geometry-derived views, labeled part IDs, and plan revision. |
| `estimates` | Cost arithmetic, currency, pricing provenance, exclusions, and time ranges. |
| `validation` | Ready/blocked status, errors, warnings, and unresolved assumptions. |

Schema validity alone is insufficient: geometric and cross-reference checks must pass. Preserve entered constraints after generation errors and explain retry options without showing a partial plan as complete.

## 5. Acceptance Criteria and Verification

The MVP must pass these scenarios:

1. A vague dining-table request gathers and confirms missing constraints before generation.
2. A supported request produces diagrams, parts, cuts, hardware, and steps that agree on IDs, dimensions, quantities, and revision.
3. Equivalent metric and imperial inputs produce equivalent geometry within the documented tolerance.
4. Every cut fits its allocated stock with kerf and allowances included; insufficient stock is detected.
5. Every referenced part, tool, hardware item, and prerequisite exists; required parts are accounted for in assembly.
6. Costs match catalog arithmetic. Missing prices and budget overruns are visible.
7. Removing a required tool selects a supported alternative or blocks readiness with an actionable explanation.
8. Changing dimensions regenerates every affected diagram, cut, quantity, estimate, and instruction without stale outputs.
9. Unsupported designs, out-of-range dimensions, malformed AI responses, and impossible constraints produce actionable errors rather than fabricated plans.
10. The print-friendly manual retains diagram labels, dimensions, step order, and relevant warnings.
11. Capacity requests never produce an unverified load-rating claim.
12. Text and photo inputs require inventory confirmation; unconfirmed or unsupported materials are not used in allocations.
13. Owned inventory reduces purchases only by its usable contribution; no item is double-counted, and costs cover the remaining purchase quantities.
14. Increasing or decreasing skill level creates a consistently validated revision, preserves other constraints, and explains unsupported adaptations.

Use deterministic fixture tests for calculations and cross-output consistency, plus an end-to-end test of the constraint-change demo. These checks establish internal consistency, not structural certification. The construction template requires documented domain review before anyone relies on it for a physical build.

## 6. OCI Integration and Hackathon Demo

Before implementation, document the chosen OCI service, its capability, request/response boundary, required configuration, and failure behavior. Service selection remains open; this spec assumes no specific service.

The demo must show an actual successful OCI-backed request. Keep credentials out of the client and repository. On timeout or service failure, retain inputs and offer retry. Clearly label sample or fallback responses rather than presenting them as live results.

Demo sequence:

1. Enter "I want to build a dining table."
2. Complete and confirm the constraints.
3. Generate the supported plan using the OCI-backed capability.
4. Inspect matching diagram labels, parts, cuts, estimates, and assembly steps.
5. Change the available space and show consistent regeneration.
6. Remove a required tool and show a supported adaptation or explicit blocked state.
7. Open the print-friendly manual.

## 7. Decisions Required Before Implementation

- Select the construction template and document supported bounds and review evidence.
- Define material, hardware, tool, and sample-price catalogs.
- Specify internal units, display precision, kerf, trim, and waste policies.
- Select the OCI-backed capability and deployment approach.
- Confirm the hackathon deadline and team capacity, then sequence the included scope accordingly.
