# Lab 1: Requirements Engineering & UML Use-Case Modelling

**Problem Statement #35 (Retail, E-Commerce & Finance) — Customizable Subscription Box Scheduler**

> A subscription box portal where subscribers customize monthly product selections (e.g., books, coffee, snacks) based on preference tags, with support for pausing or skipping billing cycles.
>
> **Target Stakeholders / Actors:** Subscriber, Fulfillment Lead (Payment Gateway is modelled as a supporting system actor — see `requirements-table.docx`).

## Contents

| File | Deliverable |
|---|---|
| [`requirements-table.docx`](./requirements-table.docx) | Complete requirements table — 5 FRs (FR-001–FR-005) + 2 NFRs (NFR-001, NFR-002), each with Req ID, Type, Description, Priority, Acceptance Criteria, and Rationale. Also lists all actors and use cases. |
| [`uml-diagram.pdf`](./uml-diagram.pdf) | UML use-case diagram — actors (1 primary, 2 secondary), 7 use cases, and the required `<<include>>` / `<<extend>>` relationships. |
| [`use-case-flow.docx`](./use-case-flow.docx) | One-page use-case flow specification for UC-02 "Swap or Pause Monthly Delivery" — preconditions, postconditions, main success scenario, and one alternate flow. |
| `usecase.puml` | PlantUML source for the diagram, kept for reference/edits. |

## Summary

- **FR-001** and **NFR-001** were given in the problem statement; FR-002–FR-005 and NFR-002 were elicited from the scenario.
- **`<<include>>`**: UC-04 "Process Monthly Payment" always includes UC-06 "Validate Payment Details."
- **`<<extend>>`**: UC-07 "Apply Promotional Discount" optionally extends UC-04 "Process Monthly Payment," applying only when a valid promo code is present.

## Author

Rhea — fill in Name / SRN / Section in `requirements-table.docx` before submitting.
