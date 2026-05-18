# Tailwind v4 Configuration

> **Purpose**: Tailwind v4 setup using @import, @theme inline, @layer base — no tailwind.config.js
> **MCP Validated**: 2026-05-05

## When to Use

- Setting up a new OCVEL frontend project
- Adding new design tokens to the system
- Understanding why there is no `tailwind.config.js`
- Extending the theme with new colors or radius values

## How Tailwind v4 Differs from v3

| Aspect | v3 | v4 (OCVEL) |
|--------|-----|------------|
| Config file | `tailwind.config.js` required | No config file |
| CSS import | `@tailwind base/components/utilities` | `@import "tailwindcss"` |
| Theme extension | JS object in config | `@theme inline {}` in CSS |
| Custom variants | `addVariant()` plugin | `@custom-variant` directive |
| Content detection | Explicit `content: []` array | Automatic file scanning |

## Complete index.css Structure

```css
/* 1. Import Tailwind v4 — replaces @tailwind base/components/utilities */
@import "tailwindcss";

/* 2. Define custom dark mode variant */
@custom-variant dark (&:is(.dark *));

/* 3. Design system — CSS custom properties (light mode) */
:root {
  --background: oklch(0.9791 0 0);
  --foreground: oklch(0.2178 0 0);
  --primary: oklch(0.8893 0.1777 95.2779);
  --primary-foreground: oklch(0.2178 0 0);
  --secondary: oklch(0.9612 0 0);
  --muted: oklch(0.9401 0 0);
  --muted-foreground: oklch(0.4640 0 0);
  --accent: oklch(0.9617 0.0592 95.8853);
  --destructive: oklch(0.5433 0.1740 29.6967);
  --destructive-foreground: oklch(1.0000 0 0);
  --border: oklch(0.9006 0 0);
  --input: oklch(0.9006 0 0);
  --ring: oklch(0.8893 0.1777 95.2779);
  --card: oklch(1.0000 0 0);
  --card-foreground: oklch(0.2393 0 0);
  --popover: oklch(1.0000 0 0);
  --popover-foreground: oklch(0.2393 0 0);
  --radius: 1.4rem;
  --font-sans: Inter, sans-serif;
  --font-mono: Inter, ui-sans-serif, sans-serif;
  --spacing: 0.25rem;
}

/* 4. Dark mode overrides */
.dark {
  --background: oklch(0.1398 0 0);
  --foreground: oklch(0.9850 0.0041 91.4457);
  --card: oklch(0.1822 0 0);
  --secondary: oklch(0.2221 0 0);
  --muted: oklch(0.2221 0 0);
  --muted-foreground: oklch(0.6830 0 0);
  --border: oklch(0.2520 0 0);
  --input: oklch(0.2520 0 0);
}

/* 5. Bridge CSS vars to Tailwind utility classes */
@theme inline {
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-primary: var(--primary);
  --color-primary-foreground: var(--primary-foreground);
  --color-secondary: var(--secondary);
  --color-secondary-foreground: var(--secondary-foreground);
  --color-muted: var(--muted);
  --color-muted-foreground: var(--muted-foreground);
  --color-accent: var(--accent);
  --color-accent-foreground: var(--accent-foreground);
  --color-destructive: var(--destructive);
  --color-destructive-foreground: var(--destructive-foreground);
  --color-border: var(--border);
  --color-input: var(--input);
  --color-ring: var(--ring);
  --color-card: var(--card);
  --color-card-foreground: var(--card-foreground);
  --font-sans: var(--font-sans);
  --font-mono: var(--font-mono);
  --radius-sm: calc(var(--radius) - 4px);
  --radius-md: calc(var(--radius) - 2px);
  --radius-lg: var(--radius);
  --radius-xl: calc(var(--radius) + 4px);
}

/* 6. Apply defaults globally */
@layer base {
  * {
    @apply border-border outline-ring/50;
  }
  body {
    @apply bg-background text-foreground;
  }
}
```

## Adding a New Token

```css
/* Step 1: Add CSS var in :root */
:root {
  --brand-green: oklch(0.72 0.17 145);
}

/* Step 2: Add dark override if needed */
.dark {
  --brand-green: oklch(0.65 0.15 145);
}

/* Step 3: Bridge in @theme inline */
@theme inline {
  --color-brand-green: var(--brand-green);
}

/* Step 4: Use in components */
/* className="bg-brand-green text-white" */
```

## Configuration

| Setting | Value | Notes |
|---------|-------|-------|
| CSS entry point | `src/index.css` | Imported in main.tsx |
| Tailwind import | `@import "tailwindcss"` | First line of index.css |
| Content scanning | Automatic | v4 scans all project files |
| Config file | None needed | All config in CSS |
| PostCSS | Required | `@tailwindcss/vite` plugin |

## Vite Integration

```ts
// vite.config.ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),  // Handles @import "tailwindcss" processing
  ],
});
```

## Common Mistakes

### Wrong — v3 syntax in v4 project
```css
/* Do NOT use these in a v4 project */
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### Correct — v4 import
```css
@import "tailwindcss";
```

### Wrong — extending theme in JS config
```js
// tailwind.config.js does not exist in this project
module.exports = { theme: { extend: { colors: { primary: "#..." } } } };
```

### Correct — extending in CSS
```css
@theme inline {
  --color-primary: var(--primary);
}
```

## See Also

- [shadcn-setup](../concepts/shadcn-setup.md)
- [dark-mode](./dark-mode.md)
- [design-tokens](../concepts/design-tokens.md)
