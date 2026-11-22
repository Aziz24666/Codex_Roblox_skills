# V27 Gradual Strict-Typing Migration Playbook

The goal is better contracts and earlier feedback without destabilizing every script at once.

## Stage 1 — Measure

Run `v27.py audit` and `v27.py typecheck` in project mode. Review the current `strict`, `nonstrict`, `nocheck`, and default-mode counts. Save the diagnostics as a baseline in your development branch.

## Stage 2 — Define shared contracts

Identify stable data records, configuration shapes, service interfaces and remote payloads. Put shared types close to the system boundary they describe. Avoid turning every internal implementation detail into a public type.

## Stage 3 — Migrate leaf modules

Start with pure utilities, stable data definitions and modules with few dependencies. Add parameter types, return types and optional-field handling. Prefer precise unions and records to broad `any` casts.

## Stage 4 — Migrate callers and service boundaries

Move one bounded subsystem at a time. Update callers alongside the public interface. Run static analysis and the relevant unit/integration tests after each boundary change.

## Stage 5 — Expand coverage

Continue through services, controllers, UI modules and systems with more dependencies. Keep a short record of intentionally non-strict or nocheck areas and the reason they remain that way.

## Completion criteria

- The analyzer passes in project mode.
- Critical shared modules have explicit public interfaces.
- Callers and server-side boundaries use the same payload contracts.
- The tests cover optional values, invalid inputs, failure returns and relevant state changes.
- Any remaining non-strict/nocheck areas are understood and documented.

Do not use mass search-and-replace to add `--!strict`. V27's recommendations are advisory; humans decide when each module is ready.
