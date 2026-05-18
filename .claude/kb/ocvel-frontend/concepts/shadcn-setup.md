# shadcn/ui Setup

> **Purpose**: How shadcn/ui integrates with Tailwind v4 via @theme inline and CSS var pattern
> **Confidence**: 0.97
> **MCP Validated**: 2026-05-05

## Overview

shadcn/ui generates React components that read design tokens from CSS custom properties. In Tailwind v4, these CSS vars are bridged to Tailwind utility classes through `@theme inline {}`. Components use Tailwind classes like `bg-primary` which resolve to `var(--color-primary)` which in turn resolves to `var(--primary)`.

## The CSS Var Bridge

Three layers connect the design system to components:

```
CSS Custom Property    →    @theme inline mapping    →    Tailwind class
--primary                   --color-primary              bg-primary
                            = var(--primary)
```

The `@theme inline {}` block in `index.css`:

```css
@theme inline {
  --color-primary: var(--primary);
  --color-primary-foreground: var(--primary-foreground);
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  /* ... all other tokens ... */
}
```

## Installation

```bash
# Initialize shadcn in a Vite + React + Tailwind v4 project
npx shadcn@latest init

# Add individual components
npx shadcn@latest add button
npx shadcn@latest add card
npx shadcn@latest add dialog
npx shadcn@latest add input
npx shadcn@latest add badge
```

Components are added to `src/components/ui/` and can be modified freely.

## components.json Configuration

```json
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "default",
  "rsx": false,
  "tsx": true,
  "tailwind": {
    "config": "",
    "css": "src/index.css",
    "baseColor": "neutral",
    "cssVariables": true,
    "prefix": ""
  },
  "aliases": {
    "components": "@/components",
    "utils": "@/lib/utils",
    "ui": "@/components/ui"
  }
}
```

## The cn() Utility

All shadcn components use `cn()` for conditional class merging. It combines `clsx` and `tailwind-merge`:

```ts
// src/lib/utils.ts
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

## Radius Mapping in @theme inline

shadcn expects `--radius-sm`, `--radius-md`, `--radius-lg`, `--radius-xl`. These are computed from the base `--radius: 1.4rem`:

```css
@theme inline {
  --radius-sm: calc(var(--radius) - 4px);  /* 1.15rem */
  --radius-md: calc(var(--radius) - 2px);  /* 1.3rem  */
  --radius-lg: var(--radius);               /* 1.4rem  */
  --radius-xl: calc(var(--radius) + 4px);  /* 1.65rem */
}
```

## Base Layer Defaults

```css
@layer base {
  * {
    @apply border-border outline-ring/50;
  }
  body {
    @apply bg-background text-foreground;
  }
}
```

This applies the design system globally: all borders default to `--border`, all outlines default to `--ring` at 50% opacity, and the body uses the semantic background and foreground tokens.

## Quick Reference

| Task | Command |
|------|---------|
| Add Button | `npx shadcn@latest add button` |
| Add Form | `npx shadcn@latest add form` |
| Add Table | `npx shadcn@latest add table` |
| Add Sidebar | `npx shadcn@latest add sidebar` |
| Update component | re-run add command, confirm overwrite |

## Related

- [tech-stack](./tech-stack.md)
- [design-tokens](./design-tokens.md)
- [tailwind-v4-config](../patterns/tailwind-v4-config.md)
- [component-pattern](../patterns/component-pattern.md)
