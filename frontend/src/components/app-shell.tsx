"use client";

import { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import { Navbar } from "@/components/navbar";
import { isAuthenticated } from "@/lib/auth";

const PUBLIC_PATHS = ["/login"];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const isPublic = PUBLIC_PATHS.some(p => pathname.startsWith(p));

  useEffect(() => {
    if (!isPublic && !isAuthenticated()) {
      router.replace("/login");
    }
  }, [pathname, isPublic, router]);

  if (isPublic) {
    return <>{children}</>;
  }

  return (
    <>
      <Navbar />
      <div className="flex-1">{children}</div>
    </>
  );
}
