# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

User-proposed React/TypeScript frontend and Python/FastAPI/MongoDB backend. Greenfield choices are documented in [decisions](docs/decisions/README.md); backend dependencies are now locally locked/installed, while frontend remains planned. The user confirmed establishing the foundation in this workspace.

## Users

Confirmed audience: a hiring-assessment evaluator who must run, inspect and discuss the solution. Working product assumption: an analyst or technically curious user exploring historical heatwave indicators. No interviews or additional personas have been fabricated.

## Product Purpose

Select a geographic location and historical period, analyze heatwaves, and understand frequency and duration patterns with their supporting data and limitations. [PRD](PRD.md) owns detailed requirements.

## Operating Context

A focused, single-page assessment application used on mobile through wide desktop screens. Results come from public historical weather data, backend scientific calculations, and NoSQL persistence. This is historical exploration, not forecasting or emergency advice.

## Capabilities and Constraints

Heatwave is the only initial hazard. Point/city selection is the first complete slice; bounded-area sampling is a later slice. No accounts, billing, notifications, AI inference or extra dashboards. Honest missing-data states and reproducible methods are part of the core product.

## Brand Commitments

Full project name: Climate Hazard Trend Analyzer. Dashboard identity: Climate Hazard Analyzer. The user's updated monochrome aesthetic is specified in [frontend/docs/design.md](frontend/docs/design.md); root DESIGN remains a navigation entry point. Copy should be direct, precise and neutral about trend direction.

## Evidence on Hand

The private assessment PDF and initial prompts were read in the requested order. Later requests supplied an external Atlas credential file, no-key provider instructions, the 85-concept checklist and the monochrome design/UI implementation brief. Public endpoint probes supplied basic data-access evidence at one point, not climate findings. No approved reference image, pre-existing application, customer evidence or deployment was supplied. Current partial implementation and limits belong in PROJECT_STATE.

## Product Principles

- A correct end-to-end heatwave workflow precedes bonus features.
- Every finding must have a backend result and visible methodological context.
- Missing evidence is an explicit state, never a plausible-looking placeholder.
- Small, explainable changes make the solution maintainable and defensible.

## Accessibility & Inclusion

Keyboard access, visible focus, accessible chart alternatives, readable text, reduced motion and usable narrow layouts are required. [Responsive verification](frontend/docs/responsiveness.md) defines the planned checks.
