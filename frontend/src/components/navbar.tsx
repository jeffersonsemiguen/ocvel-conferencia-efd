"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { LogOutIcon, LayoutDashboard, Building2, Settings } from "lucide-react";
import { cn } from "@/lib/utils";
import { clearAuth, getUser } from "@/lib/auth";

const links = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/empresas",  label: "Empresas",  icon: Building2 },
  { href: "/admin",     label: "Admin",     icon: Settings, adminOnly: true },
];

export function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
  const [user, setUser] = useState<ReturnType<typeof getUser>>(null);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setUser(getUser());
    setMounted(true);
  }, []);

  function handleLogout() {
    clearAuth();
    router.push("/login");
  }

  const visibleLinks = links.filter(
    (l) => !l.adminOnly || user?.role === "admin"
  );

  return (
    <nav className="border-b bg-card">
      <div className="max-w-6xl mx-auto px-6 h-14 flex items-center gap-1">
        {/* Logo / brand */}
        <Link href="/" className="flex items-center gap-2 mr-4">
          <span className="inline-flex items-center justify-center w-7 h-7 rounded-md bg-primary text-primary-foreground font-bold text-xs">
            FC
          </span>
          <span className="font-semibold text-sm hidden sm:inline">FiscalCheck</span>
        </Link>

        {/* Nav links */}
        {visibleLinks.map(({ href, label, icon: Icon }) => {
          const active = pathname === href || pathname.startsWith(href + "/");
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm transition-colors",
                active
                  ? "bg-primary text-primary-foreground font-medium"
                  : "text-muted-foreground hover:text-foreground hover:bg-accent"
              )}
            >
              <Icon className="w-3.5 h-3.5" />
              {label}
            </Link>
          );
        })}

        {/* User + logout */}
        {mounted && (
          <div className="ml-auto flex items-center gap-3">
            {user && (
              <span className="text-xs text-muted-foreground hidden md:block">
                {user.name}
                {user.role === "admin" && (
                  <span className="ml-1.5 px-1.5 py-0.5 rounded text-[10px] bg-primary/20 text-primary-foreground font-medium">
                    admin
                  </span>
                )}
              </span>
            )}
            <button
              onClick={handleLogout}
              className="flex items-center gap-1 px-2.5 py-1.5 rounded-md text-xs text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
            >
              <LogOutIcon className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Sair</span>
            </button>
          </div>
        )}
      </div>
    </nav>
  );
}
