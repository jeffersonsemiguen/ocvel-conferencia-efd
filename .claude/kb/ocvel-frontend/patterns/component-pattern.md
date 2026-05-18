# Component Pattern

> **Purpose**: Standard pattern for creating React components with shadcn, TypeScript, cn(), and OCVEL design system
> **MCP Validated**: 2026-05-05

## When to Use

- Creating any new UI component in the OCVEL frontend
- Wrapping shadcn/ui primitives with project-specific styling
- Building feature components that accept variant props
- Composing multiple shadcn primitives into a domain component

## Implementation

```tsx
// src/components/ui/status-badge.tsx
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

// 1. Define variants with cva
const statusBadgeVariants = cva(
  // Base classes applied always
  "inline-flex items-center rounded-full px-3 py-1 text-sm font-medium",
  {
    variants: {
      status: {
        success: "bg-primary text-primary-foreground",
        error:   "bg-destructive text-destructive-foreground",
        muted:   "bg-muted text-muted-foreground",
        accent:  "bg-accent text-accent-foreground",
      },
      size: {
        sm: "px-2 py-0.5 text-xs",
        md: "px-3 py-1 text-sm",
        lg: "px-4 py-1.5 text-base",
      },
    },
    defaultVariants: {
      status: "muted",
      size: "md",
    },
  }
);

// 2. TypeScript interface extends HTML element + variants
interface StatusBadgeProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof statusBadgeVariants> {
  label: string;
}

// 3. Component uses cn() to merge variants + consumer classes
export function StatusBadge({
  label,
  status,
  size,
  className,
  ...props
}: StatusBadgeProps) {
  return (
    <span
      className={cn(statusBadgeVariants({ status, size }), className)}
      {...props}
    >
      {label}
    </span>
  );
}
```

## Feature Component (Composing shadcn Primitives)

```tsx
// src/components/report/report-card.tsx
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

interface ReportCardProps {
  title: string;
  status: "pending" | "complete" | "error";
  children: React.ReactNode;
  className?: string;
}

const statusConfig = {
  pending: { label: "Pendente",  variant: "secondary" as const },
  complete: { label: "Concluido", variant: "default" as const },
  error:    { label: "Erro",      variant: "destructive" as const },
};

export function ReportCard({
  title,
  status,
  children,
  className,
}: ReportCardProps) {
  const { label, variant } = statusConfig[status];

  return (
    <Card className={cn("w-full", className)}>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="text-base">{title}</CardTitle>
        <Badge variant={variant}>{label}</Badge>
      </CardHeader>
      <CardContent>{children}</CardContent>
    </Card>
  );
}
```

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| Base classes | always applied | Layout, typography, base spacing |
| Variant classes | per variant | Colors, sizes from design system |
| `className` prop | undefined | Allows consumer overrides |
| `...props` spread | all HTML attrs | Passes a11y, event handlers through |

## Example Usage

```tsx
// In a page or parent component
import { StatusBadge } from "@/components/ui/status-badge";
import { ReportCard } from "@/components/report/report-card";

export function Dashboard() {
  return (
    <div className="grid gap-4 p-6">
      <ReportCard title="ECD 2024" status="complete">
        <StatusBadge label="Transmitido" status="success" size="sm" />
        <p className="mt-2 text-muted-foreground text-sm">
          Arquivo enviado com sucesso.
        </p>
      </ReportCard>

      <ReportCard title="ECD 2023" status="error" className="border-destructive">
        <StatusBadge label="Rejeicao" status="error" />
      </ReportCard>
    </div>
  );
}
```

## Rules

- Always accept and forward `className` prop via `cn()`
- Always spread `...props` for accessibility and event handler passthrough
- Use `cva` for multi-variant components, plain `cn()` for single-state components
- Keep components in `src/components/ui/` for primitives, `src/components/{feature}/` for domain components
- Never hardcode color hex values — always use Tailwind design system classes

## See Also

- [shadcn-setup](../concepts/shadcn-setup.md)
- [dark-mode](./dark-mode.md)
- [tailwind-v4-config](./tailwind-v4-config.md)
