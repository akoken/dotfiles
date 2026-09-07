---
name: microsoft-extensions-configuration
description: Use when binding strongly typed .NET options, adding startup or cross-property validation, choosing options lifetimes and reload behavior, configuring named options, or testing environment-dependent settings.
---

# Microsoft.Extensions Configuration Patterns

## Workflow

1. Inspect configuration sources, section names, settings consumers, options registrations, and reload requirements.
2. Bind a settings type per configuration concern; choose data annotations for simple constraints and IValidateOptions<T> for cross-property or conditional rules.
3. Register validation and ValidateOnStart for required settings; aggregate actionable validation failures rather than throwing from validators.
4. Choose IOptions, IOptionsSnapshot, or IOptionsMonitor to match the consumer lifetime and reload behavior; apply post-configuration before validation.
5. Route named instances, dependency-aware validators, and environment rules to advanced-patterns.md; account for every configured name.
6. Test valid, missing, invalid, and conditional settings, then verify host startup rejects invalid required configuration and reload behavior matches the chosen lifetime.

Completion requires every changed settings type bound and validated, invalid required settings rejected at startup, and tests covering its names, conditional rules, and lifetime behavior.

## Reference Routing

Read only the needed branch of [references/full-guide.md](references/full-guide.md):

- `Why Configuration Validation Matters`.
- `Pattern 1: Basic Options Binding`.
- `Pattern 2: Data Annotations Validation`.
- `Pattern 3: IValidateOptions<T> for Complex Validation`.
- `Pattern 4: Options Lifetime`.
- `Pattern 5: Post-Configuration`.
- `Anti-Patterns to Avoid`.
- `Summary`.
- [advanced-patterns.md](advanced-patterns.md): Validators with Dependencies; Named Options; Complete Example - Production Settings Class; Testing Configuration Validators.

Use `rg -n '^## ' references/full-guide.md` to locate the relevant section.

## Guardrails

- Do not scatter raw IConfiguration string lookups through services.
- Do not defer required configuration validation to constructors or first request.
- Do not throw for ordinary validation failures; return ValidateOptionsResult.Fail with all failures.
- Do not inject scoped IOptionsSnapshot into singleton consumers.
- Do not assume IOptions reloads values or cache monitor values when live reload is required.
- Do not apply name-specific validation indiscriminately to all named options.
