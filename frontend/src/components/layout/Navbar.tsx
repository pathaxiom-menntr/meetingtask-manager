"use client";

import { useAuthStore } from "@/store/auth.store";
import { useRouter } from "next/navigation";
import { getInitials, formatDateRelative } from "@/lib/utils";
import {
  Bell,
  Search,
  LogOut,
  User,
  ChevronDown,
  CheckCheck,
  ClipboardList,
  X,
  Menu,
  CheckSquare,
  Video,
} from "lucide-react";
import { useState, useRef, useEffect } from "react";
import { toast } from "sonner";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { notificationsService } from "@/services/notifications.service";
import type { Notification } from "@/services/notifications.service";
import { tasksService } from "@/services/tasks.service";
import { meetingsService } from "@/services/meetings.service";
import Link from "next/link";
import { cn } from "@/lib/utils";
import { motion, AnimatePresence } from "framer-motion";
import { useSidebarStore } from "@/store/sidebar.store";

export function Navbar() {
  const { user, logout } = useAuthStore();
  const router = useRouter();
  const queryClient = useQueryClient();
  const toggleSidebar = useSidebarStore((s) => s.toggle);
  const toggleMobile = useSidebarStore((s) => s.toggleMobile);

  const [menuOpen, setMenuOpen] = useState(false);
  const [notifOpen, setNotifOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchOpen, setSearchOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const notifRef = useRef<HTMLDivElement>(null);
  const searchRef = useRef<HTMLDivElement>(null);

  // Close dropdowns on outside click
  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setMenuOpen(false);
      }
      if (notifRef.current && !notifRef.current.contains(e.target as Node)) {
        setNotifOpen(false);
      }
      if (searchRef.current && !searchRef.current.contains(e.target as Node)) {
        setSearchOpen(false);
      }
    }
    function handleKey(e: KeyboardEvent) {
      if (e.key === "Escape") {
        setSearchOpen(false);
        setSearchQuery("");
      }
    }
    document.addEventListener("mousedown", handleClick);
    document.addEventListener("keydown", handleKey);
    return () => {
      document.removeEventListener("mousedown", handleClick);
      document.removeEventListener("keydown", handleKey);
    };
  }, []);

  // Fetch notifications
  const { data: notifications = [] } = useQuery({
    queryKey: ["notifications"],
    queryFn: notificationsService.getAll,
    refetchInterval: 30000,
  });

  // Fetch all tasks + meetings for search
  const { data: allTasks = [] } = useQuery({
    queryKey: ["tasks"],
    queryFn: () => tasksService.getTasks({ limit: 200 }),
  });
  const { data: allMeetings = [] } = useQuery({
    queryKey: ["meetings"],
    queryFn: () => meetingsService.getMeetings({ limit: 200 }),
  });

  // Filter results
  const q = searchQuery.trim().toLowerCase();
  const matchedTasks = q
    ? allTasks.filter(
        (t) =>
          t.title.toLowerCase().includes(q) ||
          (t.description ?? "").toLowerCase().includes(q)
      ).slice(0, 5)
    : [];
  const matchedMeetings = q
    ? allMeetings.filter(
        (m) =>
          m.title.toLowerCase().includes(q) ||
          m.transcript.toLowerCase().includes(q)
      ).slice(0, 5)
    : [];
  const hasResults = matchedTasks.length > 0 || matchedMeetings.length > 0;

  const unreadCount = notifications.filter((n) => !n.is_read).length;

  const markReadMutation = useMutation({
    mutationFn: notificationsService.markRead,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["notifications"] }),
  });

  const markAllReadMutation = useMutation({
    mutationFn: notificationsService.markAllRead,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["notifications"] }),
  });

  const handleNotifClick = (n: Notification) => {
    if (!n.is_read) markReadMutation.mutate(n.id);
    if (n.task_id) {
      router.push(`/tasks/${n.task_id}`);
      setNotifOpen(false);
    }
  };

  const handleLogout = async () => {
    await logout();
    toast.success("Signed out");
    router.push("/login");
  };

  return (
    <header className="h-16 border-b flex items-center gap-3 px-4 bg-background shrink-0">
      {/* Hamburger toggle (mobile) */}
      <button
        onClick={toggleMobile}
        className="md:hidden w-9 h-9 rounded-xl hover:bg-accent flex items-center justify-center transition shrink-0"
        aria-label="Toggle mobile sidebar"
      >
        <Menu className="w-4 h-4 text-muted-foreground" />
      </button>

      {/* Hamburger toggle (desktop) */}
      <button
        onClick={toggleSidebar}
        className="hidden md:flex w-9 h-9 rounded-xl hover:bg-accent items-center justify-center transition shrink-0"
        aria-label="Toggle sidebar"
      >
        <Menu className="w-4 h-4 text-muted-foreground" />
      </button>

      {/* Search */}
      <div className="relative hidden sm:block" ref={searchRef}>
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground pointer-events-none" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => { setSearchQuery(e.target.value); setSearchOpen(true); }}
          onFocus={() => setSearchOpen(true)}
          placeholder="Search tasks, meetings..."
          className="pl-9 pr-8 py-2 text-sm rounded-xl bg-muted border-0 w-72 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition"
        />
        {searchQuery && (
          <button
            onClick={() => { setSearchQuery(""); setSearchOpen(false); }}
            className="absolute right-2.5 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        )}

        {/* Results dropdown */}
        <AnimatePresence>
          {searchOpen && q && (
            <motion.div
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 4 }}
              transition={{ duration: 0.15 }}
              className="absolute top-full mt-2 left-0 w-96 bg-popover border rounded-2xl shadow-xl z-50 overflow-hidden"
            >
              {!hasResults ? (
                <div className="px-4 py-6 text-center text-sm text-muted-foreground">
                  No results for &ldquo;{searchQuery}&rdquo;
                </div>
              ) : (
                <div className="py-2">
                  {/* Tasks */}
                  {matchedTasks.length > 0 && (
                    <div>
                      <p className="px-4 py-1.5 text-[10px] font-semibold text-muted-foreground uppercase tracking-wider">Tasks</p>
                      {matchedTasks.map((t) => (
                        <button
                          key={t.id}
                          onClick={() => { router.push(`/tasks/${t.id}`); setSearchOpen(false); setSearchQuery(""); }}
                          className="w-full flex items-center gap-3 px-4 py-2.5 hover:bg-accent transition text-left"
                        >
                          <CheckSquare className="w-4 h-4 text-indigo-500 shrink-0" />
                          <div className="min-w-0">
                            <p className="text-sm font-medium truncate">{t.title}</p>
                            {t.description && <p className="text-xs text-muted-foreground truncate">{t.description}</p>}
                          </div>
                          <span className={cn(
                            "ml-auto text-[10px] px-1.5 py-0.5 rounded-full font-medium shrink-0",
                            t.status === "completed" ? "bg-emerald-100 text-emerald-700" : "bg-amber-100 text-amber-700"
                          )}>
                            {t.status === "completed" ? "Done" : "Pending"}
                          </span>
                        </button>
                      ))}
                    </div>
                  )}

                  {/* Meetings */}
                  {matchedMeetings.length > 0 && (
                    <div className={matchedTasks.length > 0 ? "border-t mt-1 pt-1" : ""}>
                      <p className="px-4 py-1.5 text-[10px] font-semibold text-muted-foreground uppercase tracking-wider">Meetings</p>
                      {matchedMeetings.map((m) => (
                        <button
                          key={m.id}
                          onClick={() => { router.push(`/meetings`); setSearchOpen(false); setSearchQuery(""); }}
                          className="w-full flex items-center gap-3 px-4 py-2.5 hover:bg-accent transition text-left"
                        >
                          <Video className="w-4 h-4 text-violet-500 shrink-0" />
                          <div className="min-w-0">
                            <p className="text-sm font-medium truncate">{m.title}</p>
                            <p className="text-xs text-muted-foreground truncate">{m.transcript.slice(0, 60)}...</p>
                          </div>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      <div className="flex items-center gap-3 ml-auto">
        {/* ── Notification bell ── */}
        <div className="relative" ref={notifRef}>
          <button
            onClick={() => setNotifOpen((v) => !v)}
            className="relative w-9 h-9 rounded-xl hover:bg-accent flex items-center justify-center transition"
            aria-label="Notifications"
          >
            <Bell className="w-4 h-4 text-muted-foreground" />
            {unreadCount > 0 && (
              <motion.span
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                className="absolute -top-0.5 -right-0.5 min-w-[18px] h-[18px] px-1 bg-indigo-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center"
              >
                {unreadCount > 9 ? "9+" : unreadCount}
              </motion.span>
            )}
          </button>

          <AnimatePresence>
            {notifOpen && (
              <motion.div
                initial={{ opacity: 0, y: 6, scale: 0.97 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: 4, scale: 0.97 }}
                transition={{ duration: 0.15 }}
                className="absolute right-0 top-full mt-2 w-80 bg-popover border rounded-2xl shadow-xl z-50 overflow-hidden"
              >
                {/* Header */}
                <div className="flex items-center justify-between px-4 py-3 border-b">
                  <div className="flex items-center gap-2">
                    <Bell className="w-4 h-4 text-muted-foreground" />
                    <span className="text-sm font-semibold">Notifications</span>
                    {unreadCount > 0 && (
                      <span className="text-[11px] px-1.5 py-0.5 bg-indigo-500/10 text-indigo-500 rounded-full font-medium">
                        {unreadCount} new
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-1">
                    {unreadCount > 0 && (
                      <button
                        onClick={() => markAllReadMutation.mutate()}
                        title="Mark all as read"
                        className="p-1.5 hover:bg-accent rounded-lg transition text-muted-foreground hover:text-foreground"
                      >
                        <CheckCheck className="w-3.5 h-3.5" />
                      </button>
                    )}
                    <button
                      onClick={() => setNotifOpen(false)}
                      className="p-1.5 hover:bg-accent rounded-lg transition text-muted-foreground hover:text-foreground"
                    >
                      <X className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>

                {/* Notification list */}
                <div className="max-h-[360px] overflow-y-auto">
                  {notifications.length === 0 ? (
                    <div className="flex flex-col items-center justify-center py-10 text-center px-4">
                      <Bell className="w-8 h-8 text-muted-foreground/30 mb-2" />
                      <p className="text-sm font-medium text-muted-foreground">No notifications</p>
                      <p className="text-xs text-muted-foreground/60 mt-0.5">
                        You're all caught up!
                      </p>
                    </div>
                  ) : (
                    notifications.map((n) => (
                      <button
                        key={n.id}
                        onClick={() => handleNotifClick(n)}
                        className={cn(
                          "w-full text-left px-4 py-3 flex gap-3 hover:bg-accent transition border-b last:border-0",
                          !n.is_read && "bg-indigo-500/5"
                        )}
                      >
                        {/* Icon */}
                        <div
                          className={cn(
                            "w-8 h-8 rounded-full flex items-center justify-center shrink-0 mt-0.5",
                            !n.is_read
                              ? "bg-indigo-500/15 text-indigo-500"
                              : "bg-muted text-muted-foreground"
                          )}
                        >
                          <ClipboardList className="w-4 h-4" />
                        </div>

                        {/* Content */}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-start justify-between gap-2">
                            <p className={cn("text-xs font-semibold leading-snug", !n.is_read && "text-foreground")}>
                              {n.title}
                            </p>
                            {!n.is_read && (
                              <span className="w-2 h-2 rounded-full bg-indigo-500 shrink-0 mt-1" />
                            )}
                          </div>
                          <p className="text-xs text-muted-foreground mt-0.5 line-clamp-2 leading-relaxed">
                            {n.message}
                          </p>
                          <p className="text-[11px] text-muted-foreground/50 mt-1">
                            {formatDateRelative(n.created_at)}
                          </p>
                        </div>
                      </button>
                    ))
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* ── User menu ── */}
        <div className="relative" ref={menuRef}>
          <button
            onClick={() => setMenuOpen(!menuOpen)}
            className="flex items-center gap-2 px-3 py-1.5 rounded-xl hover:bg-accent transition"
          >
            <div className="w-7 h-7 bg-indigo-600 rounded-full flex items-center justify-center text-white text-xs font-semibold">
              {user ? getInitials(user.full_name) : "U"}
            </div>
            <span className="text-sm font-medium hidden sm:block">
              {user?.full_name?.split(" ")[0] ?? "User"}
            </span>
            <ChevronDown className="w-3.5 h-3.5 text-muted-foreground" />
          </button>

          {menuOpen && (
            <div className="absolute right-0 top-full mt-2 w-48 bg-popover border rounded-xl shadow-lg py-1 z-50">
              <div className="px-3 py-2 border-b">
                <p className="text-sm font-medium">{user?.full_name}</p>
                <p className="text-xs text-muted-foreground truncate">{user?.email}</p>
              </div>
              <button
                onClick={() => { router.push("/profile"); setMenuOpen(false); }}
                className="flex items-center gap-2 w-full px-3 py-2 text-sm hover:bg-accent transition"
              >
                <User className="w-4 h-4" /> Profile
              </button>
              <button
                onClick={handleLogout}
                className="flex items-center gap-2 w-full px-3 py-2 text-sm text-red-500 hover:bg-red-50 dark:hover:bg-red-950/20 transition"
              >
                <LogOut className="w-4 h-4" /> Sign out
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
