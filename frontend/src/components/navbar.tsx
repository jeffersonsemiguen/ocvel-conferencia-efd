"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { LogOutIcon } from "lucide-react";
import { cn } from "@/lib/utils";
import { clearAuth, getUser } from "@/lib/auth";
import { Button } from "@/components/ui/button";

const links = [
  { href: "/", label: "Início" },
  { href: "/empresas", label: "Empresas" },
];

export function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
  const user = getUser();

  function handleLogout() {
    clearAuth();
    router.push("/login");
  }

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

        <div className="ml-auto flex items-center gap-3">
          {user && (
            <span className="text-xs text-muted-foreground">
              {user.name}
              <span className="ml-1 opacity-60">({user.role})</span>
            </span>
          )}
          <Button
            size="sm"
            variant="ghost"
            className="h-7 px-2 text-muted-foreground"
            onClick={handleLogout}
          >
            <LogOutIcon className="w-3.5 h-3.5 mr-1" />
            Sair
          </Button>
        </div>
      </div>
    </nav>
  );
}
