# Tech Stack

> **Purpose**: Vite + React + React Router + TypeScript setup patterns for OCVEL frontend
> **Confidence**: 0.97
> **MCP Validated**: 2026-05-05

## Overview

OCVEL frontend is a Vite-based React SPA using TypeScript, React Router v6 for client-side routing, Tailwind CSS v4 for styling, and shadcn/ui for pre-built accessible components. There is no `tailwind.config.js` — all configuration lives inside the main CSS file via `@theme inline {}`.

## Project Structure Pattern

```text
src/
├── main.tsx          # React root + BrowserRouter
├── App.tsx           # Route definitions
├── index.css         # Tailwind v4 + design system CSS vars
├── components/
│   ├── ui/           # shadcn/ui generated components
│   └── {feature}/    # Domain-specific components
├── pages/            # Route-level page components
├── hooks/            # Custom React hooks
└── lib/
    └── utils.ts      # cn() utility + helpers
```

## Entry Point Pattern

```tsx
// main.tsx
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import "./index.css";
import App from "./App.tsx";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </StrictMode>
);
```

## Routing Pattern

```tsx
// App.tsx
import { Routes, Route } from "react-router-dom";
import { DashboardPage } from "@/pages/DashboardPage";
import { NotFoundPage } from "@/pages/NotFoundPage";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<DashboardPage />} />
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
```

## TypeScript Configuration

```json
// tsconfig.json (key settings)
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "moduleResolution": "bundler",
    "jsx": "react-jsx",
    "strict": true,
    "paths": { "@/*": ["./src/*"] }
  }
}
```

## Path Alias (Vite)

```ts
// vite.config.ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: { "@": path.resolve(__dirname, "./src") },
  },
});
```

## Quick Reference

| Concern | Solution | Import From |
|---------|----------|-------------|
| Routing | React Router v6 | `react-router-dom` |
| State | useState / useReducer | `react` |
| Path alias | `@/` prefix | configured in vite.config.ts |
| Class merging | `cn()` utility | `@/lib/utils` |
| Components | shadcn/ui | `@/components/ui/` |

## Common Mistakes

### Wrong — importing without alias
```tsx
import { Button } from "../../components/ui/button";
```

### Correct — using path alias
```tsx
import { Button } from "@/components/ui/button";
```

## Related

- [shadcn-setup](./shadcn-setup.md)
- [tailwind-v4-config](../patterns/tailwind-v4-config.md)
- [component-pattern](../patterns/component-pattern.md)
