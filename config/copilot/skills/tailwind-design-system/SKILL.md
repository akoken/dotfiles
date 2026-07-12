---
name: tailwind-design-system
description: Build or standardize Tailwind CSS v4 design systems with CSS-first tokens, variants, reusable components, responsive layouts, forms, theming, and accessibility. Use when creating a component library, defining design tokens, migrating design-system primitives, or removing inconsistent utility patterns.
---

# Tailwind CSS v4 Design Systems

## Workflow

1. Confirm the installed Tailwind major version, framework, build integration, existing tokens, component primitives, and class-composition utilities.
2. Inventory repeated visual decisions before adding tokens or variants.
3. Define semantic tokens at the narrowest shared layer and map components to them.
4. Build components around stable states and variants rather than copied utility strings.
5. Validate responsive behavior, keyboard/focus behavior, contrast, dark mode, and reduced motion.
6. Check generated CSS and production build output before declaring the design system complete.

Completion requires one owner for each token, explicit component states, responsive/accessibility verification, and no parallel ad-hoc styling system.

## Reference Routing

Read only the relevant section of [references/full-guide.md](references/full-guide.md):

- Tailwind v4 CSS-first setup and tokens;
- token hierarchy and component architecture;
- CVA variants;
- React compound components;
- form components;
- responsive grids;
- utility helpers.

Read [references/advanced-patterns.md](references/advanced-patterns.md) only when the requested branch specifically needs those advanced patterns.

Use `rg -n '^## |^### Pattern' references/full-guide.md` to locate the branch.

## Guardrails

- Do not apply v4 configuration patterns to a v3 project without an explicit migration.
- Prefer semantic tokens over raw palette values in shared components.
- Keep variant axes small and behaviorally meaningful.
- Preserve existing component APIs unless a migration is part of the request.
- Do not hide accessibility states behind visual-only variants.
- Avoid dynamic class strings that the build cannot detect.
