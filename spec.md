# AI Woodworking Planner: Hackathon MVP

## Product Goal

Help a beginner or intermediate DIY builder turn a woodworking project idea into a clear project plan that fits their space, tools, and budget.

## 1. Simple User Flow

1. Show at least three clearly labeled example table ideas using the one supported construction method. The user selects one before the description field appears.
2. The user describes the selected idea. The example supplies starting dimensions, which the user can edit.
3. A short form collects dimensions, budget, available tools, and skill level. Use one unit system and one currency throughout the demo.
4. The user confirms the inputs and generates a plan.
5. The app displays a diagram, cut list, shopping list, and assembly instructions.
6. The user can change dimensions or request simpler/more detailed instructions and regenerate.
7. The user can print the plan using a clean browser print view.

Do not generate a plan immediately from a vague prompt. Ask for the missing essentials first. Explain when a request falls outside the supported table design.

## 2. Plan Output

Each plan includes:

- **Table diagram:** A simple dimensioned drawing generated from the predefined design.
- **Cut list:** Part labels, actual dimensions, and quantities.
- **Shopping list:** Required lumber and hardware, with an approximate total based on clearly labeled sample prices.
- **Tool checklist:** Required tools compared with the tools the user has.
- **Assembly steps:** Ordered instructions referencing the same part labels as the diagram and cut list, with relevant tool and safety notes.

The essential requirement: the diagram, cut list, shopping list, and assembly instructions describe the same table.

## 3. Available Materials and Skill Level

### Owned materials

Allow optional text input for lumber and hardware the user already owns. Ask them to confirm dimensions and quantities. Subtract confirmed, matching stock from the shopping list using a simple matching rule; complex offcut allocation and cutting optimization can wait.

Photos may be attached as references. The MVP does not need to identify materials or infer measurements from images; the user's confirmed text supplies those details.

### Skill adjustment

Let the user request simpler or more detailed instructions after viewing a plan. Change explanations, terminology, and step detail while keeping the same construction method and geometry. Preserve the other inputs when regenerating.

## 4. Lightweight Implementation

- Use AI to interpret the request, help collect missing inputs, and explain assembly steps for the predefined design.
- Use straightforward code to calculate part dimensions, quantities, and sample costs from the template.
- Keep a single project data object containing the inputs, parts, hardware, required tools, estimated cost, and assembly steps. Generate the drawing and lists from that object.
- Keep dimensions and part labels fixed when AI writes or simplifies instructions.
- Replace the displayed plan together after regeneration so outputs remain consistent. Keep user inputs if generation fails and offer retry.
- Make one real OCI-backed AI request in the demo. Select the service and confirm access early. Keep credentials on the server and out of the repository.
- The three starting ideas are predefined examples, not AI-generated. Google AI Pro subscription sign-in cannot authorize this website to make Gemini API calls; a user-owned Gemini API project/key connection is deferred.

## 5. Basic Boundaries

- Define the supported length and width range and required tools for the chosen template.
- Explain unsupported dimensions or missing required tools instead of inventing a construction alternative.
- Show when the sample shopping estimate exceeds the user's budget. Prices are illustrative, not live quotes.
- Do not claim verified weight capacity or structural certification. Present the output as a prototype plan requiring review before a physical build.
- Include relevant safety notes in the assembly steps.

## 6. Done for the Hackathon

The MVP is ready to demonstrate when:

1. Three example table ideas appear first; selecting one reveals the description field and leads to a confirmed set of inputs.
2. One supported example produces a diagram, cut list, shopping list, and steps that agree on dimensions, quantities, and part labels.
3. Changing length or width updates the affected outputs consistently.
4. Confirmed matching owned materials reduce the purchase quantities and estimated cost.
5. Changing skill level alters instruction detail without changing the table's construction.
6. Unsupported dimensions and missing required tools produce a clear explanation.
7. A live OCI-backed request succeeds; a failed request preserves inputs and allows retry.
8. The printed plan retains readable diagrams, dimensions, lists, and steps.

Verify the template calculations with a few known examples and manually walk through the complete demo flow. A broad automated acceptance suite is outside this MVP.

## 7. Demo Story

“I want a dining table for this space, and I already have some lumber.”

Enter the constraints and confirmed owned materials, generate the plan, and show how the shopping list accounts for what the user has. Change the table dimensions, show the matching drawing and cuts, request simpler instructions, and open the print view.

## 8. Deferred

Arbitrary furniture, outdoor/folding/extendable tables, alternative joinery systems, photorealistic design variants, automatic photo identification, live retailer pricing, stock-cutting optimization, detailed build scheduling, multiple unit systems/currencies, user-owned AI provider connections, accounts, community, marketplace, and formal certification workflows.

## 9. Immediate Team Decisions

- Choose the table template, supported dimensions, materials, and required tools.
- Choose the demo's units, currency, and sample prices.
- Choose the OCI service and confirm credentials/access.
- Confirm the hackathon deadline and divide the form, calculations, AI integration, diagram, and print-view work.
