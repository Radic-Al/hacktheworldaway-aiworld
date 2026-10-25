You are an expert product manager and software architect specializing in AI-driven woodworking and DIY applications. I want you to help me design and specify an app that generates custom woodworking project plans, schematics, and step-by-step assembly guides from simple user prompts.

## 1. User Onboarding & Idea Capture
When a user enters a simple idea (e.g., "I want to build a dinner table"), the app must NOT immediately generate a plan. Instead, it must interactively prompt the user for the following key constraints:
* **Budget:** (e.g., $, $$, $$$ or exact dollar amounts)
* **Purpose & Environment:** (e.g., indoor dining, heavy-duty outdoor patio table, space-saving/folding)
* **Dimensions & Capacity:** (e.g., seating capacity, target weight capacity, available room space)
* **User Skill Level:** (Beginner, Intermediate, Advanced)
* **Available Tools:** (e.g., hand tools only, basic power tools like a circular saw and drill, or a full workshop with table saw and router)

## 2. Core Feature Specifications
Once constraints are gathered, the app must generate a cohesive project proposal featuring:
* **Visual Concepts:** Rendered design options tailored specifically to the user's budget and skill level.
* **Material Calculation:** An optimized cut list specifying lumber types (e.g., Douglas Fir, Oak, Plywood), dimensions, quantities, hardware (screws, brackets, glue), and estimated material costs.
* **Tool Check:** A required and optional tools checklist based on what the user owns versus what the project demands.
* **Labor & Time Estimates:** Estimated active build time, curing/drying time (for finishes), and total project timeline.

## 3. Step-by-Step "IKEA-Style" Manual
The core deliverable is an ultra-clear, sequential instruction manual. Each step must include:
* **Action & Cut Details:** Exact instructions (e.g., "Cut 4 pieces of 2x4 lumber at 36 inches").
* **Tool Assignment:** Which specific tool to use for that step.
* **Safety Precautions:** Highlighted safety warnings (e.g., "⚠️ Always wear safety glasses and ear protection when operating the miter saw").
* **Visual Diagrams:** Description of visual aids or exploded-view schematics for that specific assembly phase.

## Output Request
Please break down the response into:
1. **Product Requirements Document (PRD) Summary**
2. **User Flow & Interaction Model**
3. **Sample JSON Schema or Data Structure** for how the app generates a project plan
4. **Sample Output Preview** using the "dinner table" example.