---
name: microsoft-extensions-dependency-injection
description: Use when organizing .NET service registrations, composing reusable Add* extensions, choosing service lifetimes, resolving scoped services in background work, or testing conditional, factory, and keyed registrations.
---

# Dependency Injection Patterns

## Workflow

1. Inventory registrations, feature boundaries, configuration inputs, consumer lifetimes, and test overrides.
2. Group related services into feature-local IServiceCollection extensions with explicit configuration inputs and chainable returns.
3. Compose feature and layer extensions at the application entry point; preserve registration order and intentional overrides.
4. Choose lifetimes from ownership and thread-safety requirements; create and dispose a scope per background unit of work.
5. Route conditional, factory, keyed, and test replacement cases to advanced-patterns.md; reuse production registration methods in tests.
6. Build the provider with scope validation in tests and resolve affected services within their intended scopes; exercise the relevant host and override paths.

Completion requires all moved registrations reachable through production composition, correct scoped ownership and disposal, and passing resolution or host tests using the production extensions.

## Reference Routing

Read only the needed branch of [references/full-guide.md](references/full-guide.md):

- `The Problem`.
- `The Solution: Extension Method Composition`.
- `Extension Method Pattern`.
- `File Organization`.
- `Naming Conventions`.
- `Testing Benefits`.
- `Layered Extensions`.
- `Anti-Patterns`.
- `Best Practices Summary`.
- `Lifetime Management`.
- `Common Mistakes`.
- `Resources`: external documentation.
- [advanced-patterns.md](advanced-patterns.md): Testing Benefits; Common Patterns.

Use `rg -n '^## ' references/full-guide.md` to locate the relevant section.

## Guardrails

- Do not collect unrelated registrations into a vague AddServices method.
- Do not hardcode connection strings or hide required configuration inside extensions.
- Do not capture scoped services in singletons.
- Do not resolve scoped dependencies from the root provider for background work.
- Do not leave created scopes undisposed; use async disposal when dependencies require it.
- Do not duplicate production registrations in tests; replace only the dependencies that differ.
