# Design Tokens

> **Purpose**: Complete reference for all CSS custom properties in the OCVEL design system
> **Confidence**: 1.0
> **MCP Validated**: 2026-05-05

## Overview

All design tokens are CSS custom properties defined in `:root` (light) and `.dark` (dark mode). They are mapped to Tailwind utility classes via `@theme inline {}`. The token system covers colors, radius, shadows, fonts, and spacing.

## Color Tokens — Light Mode (`:root`)

| Token | Value | Description |
|-------|-------|-------------|
| `--background` | `oklch(0.9791 0 0)` | Page background ≈ #f9f9f8 |
| `--foreground` | `oklch(0.2178 0 0)` | Primary text (near black) |
| `--card` | `oklch(1.0000 0 0)` | Card surface (pure white) |
| `--card-foreground` | `oklch(0.2393 0 0)` | Card text |
| `--popover` | `oklch(1.0000 0 0)` | Popover surface |
| `--popover-foreground` | `oklch(0.2393 0 0)` | Popover text |
| `--primary` | `oklch(0.8893 0.1777 95.2779)` | Brand yellow/amber |
| `--primary-foreground` | `oklch(0.2178 0 0)` | Text on primary |
| `--secondary` | `oklch(0.9612 0 0)` | Secondary surface |
| `--secondary-foreground` | `oklch(0.2178 0 0)` | Text on secondary |
| `--muted` | `oklch(0.9401 0 0)` | Muted surface |
| `--muted-foreground` | `oklch(0.4640 0 0)` | Subdued text |
| `--accent` | `oklch(0.9617 0.0592 95.8853)` | Accent (light amber tint) |
| `--accent-foreground` | `oklch(0.2178 0 0)` | Text on accent |
| `--destructive` | `oklch(0.5433 0.1740 29.6967)` | Error/danger (red) |
| `--destructive-foreground` | `oklch(1.0000 0 0)` | Text on destructive |
| `--border` | `oklch(0.9006 0 0)` | Default border |
| `--input` | `oklch(0.9006 0 0)` | Input border |
| `--ring` | `oklch(0.8893 0.1777 95.2779)` | Focus ring (brand yellow) |

## Color Tokens — Dark Mode (`.dark`)

| Token | Dark Value | Change from Light |
|-------|-----------|-------------------|
| `--background` | `oklch(0.1398 0 0)` | Very dark ≈ #1c1c1c |
| `--foreground` | `oklch(0.9850 0.0041 91.4457)` | Near white, warm tint |
| `--card` | `oklch(0.1822 0 0)` | Dark elevated surface |
| `--primary` | `oklch(0.8893 0.1777 95.2779)` | Unchanged — brand stays |
| `--secondary` | `oklch(0.2221 0 0)` | Dark surface |
| `--muted` | `oklch(0.2221 0 0)` | Dark muted surface |
| `--muted-foreground` | `oklch(0.6830 0 0)` | Medium gray |
| `--accent` | `oklch(0.2221 0 0)` | Dark accent (no hue) |
| `--border` | `oklch(0.2520 0 0)` | Dark border |
| `--input` | `oklch(0.2520 0 0)` | Dark input border |

## Sidebar Tokens

| Token | Light | Dark |
|-------|-------|------|
| `--sidebar` | `oklch(0.9791 0 0)` | `oklch(0.1398 0 0)` |
| `--sidebar-foreground` | `oklch(0.2178 0 0)` | `oklch(0.8514 0 0)` |
| `--sidebar-primary` | `oklch(0.8893 0.1777 95.2779)` | same |
| `--sidebar-accent` | `oklch(0.9766 0.0410 96.5830)` | `oklch(0.2002 0 0)` |
| `--sidebar-accent-foreground` | `oklch(0.2178 0 0)` | `oklch(0.8893 0.1777 95.2779)` |
| `--sidebar-border` | `oklch(0.9006 0 0)` | `oklch(0.2520 0 0)` |
| `--sidebar-ring` | `oklch(0.8893 0.1777 95.2779)` | same |

## Chart Tokens

| Token | Light | Dark |
|-------|-------|------|
| `--chart-1` | `oklch(0.8893 0.1777 95.2779)` | same (brand) |
| `--chart-2` | `oklch(0.4490 0.0405 250.0452)` | `oklch(0.5799 0.0496 249.6959)` |
| `--chart-3` | `oklch(0.4999 0.0802 180.1312)` | `oklch(0.6001 0.0802 180.0405)` |
| `--chart-4` | `oklch(0.8494 0.0104 58.1918)` | same |
| `--chart-5` | `oklch(0.6001 0.0492 249.6616)` | `oklch(0.6990 0.0505 250.4634)` |

## Non-Color Tokens

| Token | Value | Notes |
|-------|-------|-------|
| `--font-sans` | `Inter, sans-serif` | Primary font |
| `--font-serif` | `Inter, serif` | Same as sans |
| `--font-mono` | `Inter, ui-sans-serif, sans-serif` | Code font |
| `--radius` | `1.4rem` | Base radius |
| `--spacing` | `0.25rem` | 1 unit = 4px |
| `--tracking-normal` | `0em` | Letter spacing |
| `--shadow-color` | `#000000` | Shadow base color |
| `--shadow-opacity` | `0.01` | Near-flat shadows |

## Related

- [color-palette](./color-palette.md)
- [shadcn-setup](./shadcn-setup.md)
- [tailwind-v4-config](../patterns/tailwind-v4-config.md)
- [specs/design-system.yaml](../specs/design-system.yaml)
