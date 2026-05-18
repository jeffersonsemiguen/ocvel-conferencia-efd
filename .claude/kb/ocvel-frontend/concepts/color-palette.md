# Color Palette

> **Purpose**: Semantic color system explanation with hex/oklch values and usage guidance
> **Confidence**: 1.0
> **MCP Validated**: 2026-05-05

## Overview

OCVEL uses a semantic color system built on oklch values. Colors are referenced by role (primary, muted, destructive) rather than by hue, making them automatically theme-aware. The brand identity is anchored by a warm yellow/amber primary that remains constant in both light and dark modes.

## Primary — Brand Yellow/Amber

The defining color of OCVEL. Used for CTAs, active states, focus rings, and brand highlights.

| Property | Value | Approximate Hex |
|----------|-------|----------------|
| Light oklch | `oklch(0.8893 0.1777 95.2779)` | `#f0c93a` (warm amber) |
| Dark oklch | `oklch(0.8893 0.1777 95.2779)` | Same — does not change |
| Foreground | `oklch(0.2178 0 0)` | Near black — readable on yellow |

Usage: `bg-primary`, `text-primary`, `border-primary`, `ring-primary`

Rule: Primary background always has dark text foreground for contrast.

## Background & Surface

| Role | Light | Dark | Hex Approx |
|------|-------|------|------------|
| Page background | `oklch(0.9791 0 0)` | `oklch(0.1398 0 0)` | #f9f9f8 / #1c1c1c |
| Card surface | `oklch(1.0000 0 0)` | `oklch(0.1822 0 0)` | #ffffff / #222222 |
| Secondary | `oklch(0.9612 0 0)` | `oklch(0.2221 0 0)` | #f5f5f5 / #2a2a2a |
| Muted | `oklch(0.9401 0 0)` | `oklch(0.2221 0 0)` | #f0f0f0 / #2a2a2a |

Note: In dark mode, secondary and muted converge to the same value — both are dark surface tones.

## Text Colors

| Role | Light | Dark | Usage |
|------|-------|------|-------|
| `--foreground` | Near black | Near white (warm) | Body text |
| `--muted-foreground` | Medium gray | Light gray | Captions, placeholders |
| `--card-foreground` | Near black | Near white | Text inside cards |

## Accent — Light Amber Tint

A softer version of primary used for hover states, selected rows, and tag backgrounds.

| Mode | Value | Hex Approx |
|------|-------|------------|
| Light | `oklch(0.9617 0.0592 95.8853)` | Very light yellow tint |
| Dark | `oklch(0.2221 0 0)` | Dark surface (loses hue in dark) |

Usage: `bg-accent`, `text-accent-foreground`

## Destructive — Error Red

Used for delete actions, error states, validation messages.

| Property | Value | Hex Approx |
|----------|-------|------------|
| Both modes | `oklch(0.5433 0.1740 29.6967)` | `#c0392b` (medium red) |
| Foreground | `oklch(1.0000 0 0)` | White — constant |

Usage: `bg-destructive`, `text-destructive`, `border-destructive`

## Border & Input

| Token | Light | Dark |
|-------|-------|------|
| `--border` | `oklch(0.9006 0 0)` | `oklch(0.2520 0 0)` |
| `--input` | same as border | same as border |
| `--ring` | brand yellow | brand yellow |

The focus ring (`--ring`) uses the brand yellow in both modes — consistent visual feedback.

## Sidebar Color Group

Sidebar uses its own token set, allowing independent theming of navigation panels.

| Token | Light | Dark |
|-------|-------|------|
| Sidebar background | same as `--background` | same as `--background` |
| Sidebar accent | lighter amber tint | dark surface |
| Sidebar accent foreground | dark | **brand yellow** (key difference in dark) |

In dark mode, sidebar active items show brand yellow text on dark surface — inverted from light.

## Chart Color Palette

Five chart colors providing visual variety for data visualization.

| Chart | Hue Family | Light L | Dark L |
|-------|-----------|---------|--------|
| chart-1 | Yellow/amber (brand) | 0.89 | 0.89 |
| chart-2 | Blue | 0.45 | 0.58 |
| chart-3 | Teal/cyan | 0.50 | 0.60 |
| chart-4 | Warm gray/gold | 0.85 | 0.85 |
| chart-5 | Blue (lighter) | 0.60 | 0.70 |

## Related

- [design-tokens](./design-tokens.md)
- [dark-mode](../patterns/dark-mode.md)
- [shadcn-setup](./shadcn-setup.md)
