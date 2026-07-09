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
  const mobileOpen = useSidebarStore((s) => s.mobileOpen);
  const closeMobile = useSidebarStore((s) => s.closeMobile);

  const renderContent = (isExpanded: boolean, onClickLink?: () => void) => (
    <>
      {/* Logo */}
      <div className={cn("flex items-center h-16 border-b shrink-0", isExpanded ? "px-5 gap-3" : "px-0 justify-center")}>
        <div className="relative shrink-0">
          <div
            className="absolute inset-0 rounded-xl blur-md opacity-50"
            style={{ background: "linear-gradient(135deg, #818cf8, #7c3aed)" }}
          />
          <div
            className="relative w-8 h-8 rounded-xl flex items-center justify-center"
            style={{
              background: "linear-gradient(135deg, #6366f1 0%, #7c3aed 100%)",
              boxShadow: "inset 0 1px 0 rgba(255,255,255,0.2), 0 2px 10px rgba(99,102,241,0.35)",
            }}
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path
                d="M2 13V3L8 9L14 3V13"
                stroke="white"
                strokeWidth="1.9"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </div>
        </div>
        {isExpanded && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="flex flex-col leading-none whitespace-nowrap">
            <span className="font-bold text-sm tracking-tight text-foreground">MeetingTask</span>
            <span className="text-[10px] text-indigo-400 font-medium tracking-widest uppercase mt-0.5">AI</span>
          </motion.div>
        )}
      </div>

      {/* Main nav */}
      <nav className={cn("flex-1 py-5 space-y-0.5", isExpanded ? "px-3" : "px-3")}>
        {navItems.map(({ label, href, icon: Icon }) => {
          const active = pathname === href || pathname.startsWith(href + "/");
          return (
            <Link
              key={href}
              href={href}
              onClick={onClickLink}
              title={!isExpanded ? label : undefined}
              className={cn(
                "flex items-center rounded-xl text-sm font-medium transition-all whitespace-nowrap",
                isExpanded ? "px-3 py-2 gap-3" : "px-0 py-3 justify-center",
                active
                  ? "bg-indigo-600 text-white"
                  : "text-muted-foreground hover:bg-accent hover:text-foreground"
              )}
            >
              <Icon className="w-5 h-5 shrink-0" />
              {isExpanded && <span>{label}</span>}
            </Link>
          );
        })}
      </nav>

      {/* Bottom nav */}
      <div className={cn("py-4 border-t space-y-0.5", isExpanded ? "px-3" : "px-3")}>
        {bottomItems.map(({ label, href, icon: Icon }) => {
          const active = pathname === href;
          return (
            <Link
              key={href}
              href={href}
              onClick={onClickLink}
              title={!isExpanded ? label : undefined}
              className={cn(
                "flex items-center rounded-xl text-sm font-medium transition-all whitespace-nowrap",
                isExpanded ? "px-3 py-2 gap-3" : "px-0 py-3 justify-center",
                active
                  ? "bg-indigo-600 text-white"
                  : "text-muted-foreground hover:bg-accent hover:text-foreground"
              )}
            >
              <Icon className="w-5 h-5 shrink-0" />
              {isExpanded && <span>{label}</span>}
            </Link>
          );
        })}
      </div>
    </>
  );

  return (
    <>
      {/* Mobile Sidebar Overlay */}
      <AnimatePresence>
        {mobileOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={closeMobile}
              className="fixed inset-0 bg-black/50 z-40 md:hidden"
            />
            <motion.aside
              initial={{ x: "-100%" }}
              animate={{ x: 0 }}
              exit={{ x: "-100%" }}
              transition={{ type: "spring", bounce: 0, duration: 0.3 }}
              className="fixed inset-y-0 left-0 w-64 bg-background border-r z-50 flex flex-col md:hidden"
            >
              {renderContent(true, closeMobile)}
            </motion.aside>
          </>
        )}
      </AnimatePresence>

      {/* Desktop Sidebar */}
      <motion.aside
        key="desktop-sidebar"
        initial={false}
        animate={{ width: open ? 240 : 72 }}
        transition={{ duration: 0.22, ease: "easeInOut" }}
        className="hidden md:flex flex-col h-full bg-background border-r shrink-0 overflow-hidden z-30 relative"
      >
        {renderContent(open)}
      </motion.aside>
    </>
  );
}
