"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const links = [
  { href: "/", label: "Início" },
  { href: "/empresas", label: "Empresas" },
];

export function Navbar() {
  const pathname = usePathname();

  return (
    <nav className="border-b bg-background">
      <div className="max-w-6xl mx-auto px-6 h-14 flex items-center gap-6">
        <span className="font-semibold text-sm mr-2">FiscalCheck EFD</span>
        {links.map((link) => (
          <Link
            key={link.href}
            href={link.href}
            className={cn(
              "text-sm transition-colors hover:text-foreground",
              pathname === link.href
                ? "text-foreground font-medium"
                : "text-muted-foreground"
            )}
          >
            {link.label}
          </Link>
        ))}
      </div>
    </nav>
  );
}
