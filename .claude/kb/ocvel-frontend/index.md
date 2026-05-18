# OCVEL Frontend Knowledge Base

> **Purpose**: Frontend architecture, design system, and component patterns for the OCVEL project
> **MCP Validated**: 2026-05-05

## Quick Navigation

### Concepts (< 150 lines each)

| File | Purpose |
|------|---------|
| [concepts/tech-stack.md](concepts/tech-stack.md) | Vite + React + React Router + TypeScript setup |
| [concepts/design-tokens.md](concepts/design-tokens.md) | All CSS custom properties, light and dark values |
| [concepts/color-palette.md](concepts/color-palette.md) | Semantic color system with hex/oklch values |
| [concepts/shadcn-setup.md](concepts/shadcn-setup.md) | shadcn/ui integration with Tailwind v4 |

### Patterns (< 200 lines each)

| File | Purpose |
|------|---------|
| [patterns/component-pattern.md](patterns/component-pattern.md) | React component with shadcn + TypeScript + cn() |
| [patterns/dark-mode.md](patterns/dark-mode.md) | Dark mode via .dark class and @custom-variant |
| [patterns/tailwind-v4-config.md](patterns/tailwind-v4-config.md) | Tailwind v4 setup with @theme inline, no config file |

### Specs (Machine-Readable)

| File | Purpose |
|------|---------|
| [specs/design-system.yaml](specs/design-system.yaml) | All design tokens as machine-readable YAML |

---

## Quick Reference

- [quick-reference.md](quick-reference.md) — Fast lookup for tokens, commands, and common patterns

---

## Key Concepts

| Concept | Description |
|---------|-------------|
| **Brand color** | Warm yellow/amber `oklch(0.8893 0.1777 95.2779)` — identical in light and dark |
| **Tailwind v4** | CSS-first config via `@theme inline {}`, no `tailwind.config.js` |
| **shadcn/ui** | Component library using CSS vars mapped through `@theme inline` |
| **Dark mode** | `.dark` class on root element, via `@custom-variant dark (&:is(.dark *))` |
| **Radius** | 1.4rem base — very rounded, pill-like aesthetic |
| **Font** | Inter for all font stacks (sans, serif, mono) |
| **Shadows** | Extremely subtle (opacity 0.01–0.03) — near-flat design |

---

## Tech Stack Summary

| Layer | Technology | Version |
|-------|-----------|---------|
| Build | Vite | Latest |
| UI Library | React | 18+ |
| Routing | React Router | v6+ |
| Styling | Tailwind CSS | v4 |
| Language | TypeScript | 5+ |
| Components | shadcn/ui | Latest |

---

## Learning Path

| Level | Files |
|-------|-------|
| **Setup** | concepts/tech-stack.md → patterns/tailwind-v4-config.md |
| **Design System** | concepts/design-tokens.md → concepts/color-palette.md |
| **Components** | concepts/shadcn-setup.md → patterns/component-pattern.md |
| **Theming** | patterns/dark-mode.md |

---

## Agent Usage

| Agent | Primary Files | Use Case |
|-------|---------------|----------|
| Frontend dev | concepts/tech-stack.md, patterns/component-pattern.md | Building new components |
| Design system | concepts/design-tokens.md, specs/design-system.yaml | Token lookup and theming |
| Theming agent | patterns/dark-mode.md, concepts/color-palette.md | Light/dark mode changes |
