# OCVEL Frontend Quick Reference

> Fast lookup tables. For full details, see linked concept/pattern files.
> **MCP Validated**: 2026-05-05

## Stack Versions & Commands

| Tool | Version | Key Command |
|------|---------|-------------|
| Vite | latest | `npm run dev` / `npm run build` |
| React | 18+ | — |
| React Router | v6+ | `<BrowserRouter>`, `useNavigate()` |
| Tailwind CSS | v4 | `@import "tailwindcss"` in CSS |
| TypeScript | 5+ | `tsc --noEmit` |
| shadcn/ui | latest | `npx shadcn@latest add <component>` |

## Brand Color Tokens (Most Used)

| Token | Tailwind Class | Light Value | Dark Value |
|-------|---------------|-------------|------------|
| `--primary` | `bg-primary` / `text-primary` | `oklch(0.8893 0.1777 95.2779)` | same |
| `--background` | `bg-background` | `oklch(0.9791 0 0)` ≈ #f9f9f8 | `oklch(0.1398 0 0)` ≈ #1c1c1c |
| `--foreground` | `text-foreground` | `oklch(0.2178 0 0)` | `oklch(0.9850 0.0041 91.4457)` |
| `--muted` | `bg-muted` | `oklch(0.9401 0 0)` | `oklch(0.2221 0 0)` |
| `--muted-foreground` | `text-muted-foreground` | `oklch(0.4640 0 0)` | `oklch(0.6830 0 0)` |
| `--border` | `border-border` | `oklch(0.9006 0 0)` | `oklch(0.2520 0 0)` |
| `--destructive` | `bg-destructive` | `oklch(0.5433 0.1740 29.6967)` | same |
| `--accent` | `bg-accent` | `oklch(0.9617 0.0592 95.8853)` | `oklch(0.2221 0 0)` |
| `--card` | `bg-card` | `oklch(1.0000 0 0)` | `oklch(0.1822 0 0)` |

## Radius Values

| Token | Value | Tailwind Class |
|-------|-------|---------------|
| `--radius` (base) | `1.4rem` | — |
| `--radius-sm` | `calc(1.4rem - 4px)` = `1.15rem` | `rounded-sm` |
| `--radius-md` | `calc(1.4rem - 2px)` = `1.3rem` | `rounded-md` |
| `--radius-lg` | `1.4rem` | `rounded-lg` |
| `--radius-xl` | `calc(1.4rem + 4px)` = `1.65rem` | `rounded-xl` |

## Font Stack

| Token | Value | Usage |
|-------|-------|-------|
| `--font-sans` | `Inter, sans-serif` | Body text, UI |
| `--font-serif` | `Inter, serif` | Headings (same as sans) |
| `--font-mono` | `Inter, ui-sans-serif, sans-serif` | Code blocks |

## Shadow Scale

| Token | Opacity | Use |
|-------|---------|-----|
| `--shadow-2xs` / `--shadow-xs` / `--shadow-sm` | 0.01 | Subtle lift |
| `--shadow` / `--shadow-md` | 0.01 | Default card shadow |
| `--shadow-lg` / `--shadow-xl` | 0.01 | Elevated elements |
| `--shadow-2xl` | 0.03 | Modals/dialogs |

## Common Pitfalls

| Don't | Do |
|-------|-----|
| Use `tailwind.config.js` | Configure via `@theme inline {}` in CSS |
| Import color as hex directly | Use CSS var: `bg-primary`, `text-foreground` |
| Toggle dark with JS class names manually | Add/remove `.dark` on `<html>` element |
| Use `rounded-full` for cards | Use `rounded-lg` (maps to 1.4rem radius) |

## Related Documentation

| Topic | Path |
|-------|------|
| Design tokens (full) | `concepts/design-tokens.md` |
| Component pattern | `patterns/component-pattern.md` |
| Dark mode | `patterns/dark-mode.md` |
| Full Index | `index.md` |
