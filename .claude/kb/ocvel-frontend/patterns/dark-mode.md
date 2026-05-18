# Dark Mode

> **Purpose**: How dark mode works with @custom-variant and .dark class on the root element
> **MCP Validated**: 2026-05-05

## When to Use

- Implementing light/dark mode toggle in OCVEL
- Adding dark-mode-specific styles to components
- Understanding why `.dark` class must be on the root/html element
- Debugging theme switching issues

## How It Works

OCVEL dark mode is class-based. The `@custom-variant` declaration in `index.css` defines the selector:

```css
/* index.css */
@custom-variant dark (&:is(.dark *));
```

This means: the `dark:` Tailwind variant matches any element that is a descendant of an element with the `.dark` class. The `.dark` class is placed on `<html>` (or `<body>`).

## CSS Variable Switching

The design system defines all tokens in both `:root` and `.dark`:

```css
:root {
  --background: oklch(0.9791 0 0);   /* near white */
  --foreground: oklch(0.2178 0 0);   /* near black */
  --primary:    oklch(0.8893 0.1777 95.2779);
}

.dark {
  --background: oklch(0.1398 0 0);   /* very dark */
  --foreground: oklch(0.9850 0.0041 91.4457); /* near white */
  --primary:    oklch(0.8893 0.1777 95.2779); /* unchanged */
}
```

When `.dark` is on `<html>`, all `var(--background)` references automatically pick up dark values — no component changes needed.

## Implementation — Theme Toggle

```tsx
// src/hooks/useTheme.ts
import { useEffect, useState } from "react";

type Theme = "light" | "dark" | "system";

export function useTheme() {
  const [theme, setTheme] = useState<Theme>(
    () => (localStorage.getItem("theme") as Theme) ?? "system"
  );

  useEffect(() => {
    const root = document.documentElement;
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    const isDark = theme === "dark" || (theme === "system" && prefersDark);

    root.classList.toggle("dark", isDark);
    localStorage.setItem("theme", theme);
  }, [theme]);

  return { theme, setTheme };
}
```

## Implementation — Toggle Button

```tsx
// src/components/ui/theme-toggle.tsx
import { Moon, Sun } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useTheme } from "@/hooks/useTheme";

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
      aria-label="Toggle theme"
    >
      {theme === "dark" ? (
        <Sun className="h-4 w-4" />
      ) : (
        <Moon className="h-4 w-4" />
      )}
    </Button>
  );
}
```

## Using dark: Variant in Components

```tsx
// Components rarely need dark: variants — CSS vars handle it automatically.
// Only use dark: for cases that can't be expressed through design tokens:

<div className="bg-background">  {/* Automatically dark in dark mode */}
  <p className="text-foreground"> {/* Automatically inverts */}
    Content
  </p>
</div>

// When you DO need dark: explicit override:
<div className="bg-white dark:bg-zinc-900 border dark:border-zinc-700">
  Custom element not using design tokens
</div>
```

## Configuration

| Setting | Value | Notes |
|---------|-------|-------|
| Variant declaration | `@custom-variant dark (&:is(.dark *))` | In index.css |
| Class target | `document.documentElement` | `<html>` element |
| Storage key | `"theme"` | localStorage |
| Default | `"system"` | Follows OS preference |
| Persistence | localStorage | Survives page refresh |

## Flicker Prevention

```html
<!-- index.html — inline script to avoid flash of wrong theme -->
<script>
  (function () {
    const stored = localStorage.getItem("theme");
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    if (stored === "dark" || (!stored && prefersDark)) {
      document.documentElement.classList.add("dark");
    }
  })();
</script>
```

Place this script in `<head>` before any stylesheets. It runs synchronously, setting the `.dark` class before the browser paints.

## Common Mistakes

### Wrong — toggling dark on body
```tsx
document.body.classList.toggle("dark"); // does NOT work with &:is(.dark *)
```

### Correct — toggling dark on html
```tsx
document.documentElement.classList.toggle("dark"); // correct target
```

## See Also

- [design-tokens](../concepts/design-tokens.md)
- [color-palette](../concepts/color-palette.md)
- [tailwind-v4-config](./tailwind-v4-config.md)
