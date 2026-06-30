"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  Video,
  CheckSquare,
  Upload,
  Users,
  User,
  Settings,
  Zap,
} from "lucide-react";
import { useSidebarStore } from "@/store/sidebar.store";

const navItems = [
  { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { label: "Meetings", href: "/meetings", icon: Video },
  { label: "Tasks", href: "/tasks", icon: CheckSquare },
  { label: "AI Upload", href: "/upload", icon: Upload },
  { label: "Team", href: "/team", icon: Users },
];

const bottomItems = [
  { label: "Profile", href: "/profile", icon: User },
  { label: "Settings", href: "/settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  const open = useSidebarStore((s) => s.open);

  return (
    <AnimatePresence initial={false}>
      {open && (
        <motion.aside
          key="sidebar"
          initial={{ width: 0, opacity: 0 }}
          animate={{ width: 240, opacity: 1 }}
          exit={{ width: 0, opacity: 0 }}
          transition={{ duration: 0.22, ease: "easeInOut" }}
          className="hidden md:flex flex-col h-full bg-background border-r shrink-0 overflow-hidden"
        >
          {/* Logo */}
          <div className="flex items-center gap-3 px-5 h-16 border-b shrink-0">
            <div className="w-8 h-8 bg-indigo-600 rounded-xl flex items-center justify-center shrink-0">
              <Zap className="w-4 h-4 text-white" />
            </div>
            <div className="flex flex-col leading-tight">
              <span className="font-bold text-sm tracking-tight text-foreground">MeetingTask</span>
              <span className="text-[10px] text-muted-foreground font-medium tracking-wide uppercase">Manager</span>
            </div>
          </div>

          {/* Main nav */}
          <nav className="flex-1 px-3 py-5 space-y-0.5">
            {navItems.map(({ label, href, icon: Icon }) => {
              const active = pathname === href || pathname.startsWith(href + "/");
              return (
                <Link
                  key={href}
                  href={href}
                  className={cn(
                    "flex items-center gap-3 px-3 py-2 rounded-xl text-sm font-medium transition-all whitespace-nowrap",
                    active
                      ? "bg-indigo-600 text-white"
                      : "text-muted-foreground hover:bg-accent hover:text-foreground"
                  )}
                >
                  <Icon className="w-4 h-4 shrink-0" />
                  <span>{label}</span>
                </Link>
              );
            })}
          </nav>

          {/* Bottom nav */}
          <div className="px-3 py-4 border-t space-y-0.5">
            {bottomItems.map(({ label, href, icon: Icon }) => {
              const active = pathname === href;
              return (
                <Link
                  key={href}
                  href={href}
                  className={cn(
                    "flex items-center gap-3 px-3 py-2 rounded-xl text-sm font-medium transition-all whitespace-nowrap",
                    active
                      ? "bg-indigo-600 text-white"
                      : "text-muted-foreground hover:bg-accent hover:text-foreground"
                  )}
                >
                  <Icon className="w-4 h-4 shrink-0" />
                  <span>{label}</span>
                </Link>
              );
            })}
          </div>
        </motion.aside>
      )}
    </AnimatePresence>
  );
}
