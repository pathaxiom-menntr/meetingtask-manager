"use client";

import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { Users, Mail } from "lucide-react";
import { usersService } from "@/services/users.service";
import { EmptyState } from "@/components/common/EmptyState";
import { Skeleton } from "@/components/common/LoadingSkeleton";

function TeamMemberSkeleton() {
  return (
    <div className="flex items-center gap-4 p-4 rounded-2xl border bg-card">
      <Skeleton className="w-10 h-10 rounded-full shrink-0" />
      <div className="flex-1 space-y-2 min-w-0">
        <Skeleton className="h-4 w-40" />
        <Skeleton className="h-3 w-56" />
      </div>
    </div>
  );
}

function getInitials(name: string) {
  return name
    .split(" ")
    .map((n) => n[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();
}

const AVATAR_COLORS = [
  "bg-indigo-500",
  "bg-emerald-500",
  "bg-amber-500",
  "bg-rose-500",
  "bg-violet-500",
  "bg-cyan-500",
];

export default function TeamPage() {
  const { data: users = [], isLoading } = useQuery({
    queryKey: ["users"],
    queryFn: () => usersService.getUsers({ limit: 100 }),
  });

  return (
    <div className="w-full space-y-6">
      <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-2xl font-bold tracking-tight">Team</h1>
        <p className="text-muted-foreground text-sm mt-0.5">
          {isLoading ? "Loading…" : `${users.length} member${users.length !== 1 ? "s" : ""}`}
        </p>
      </motion.div>

      {isLoading ? (
        <div className="space-y-2">
          {Array(6).fill(0).map((_, i) => <TeamMemberSkeleton key={i} />)}
        </div>
      ) : users.length === 0 ? (
        <EmptyState
          icon={Users}
          title="No team members"
          description="No users have been added yet."
        />
      ) : (
        <div className="space-y-2">
          {users.map((user, i) => (
            <motion.div
              key={user.id}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.04 }}
              className="flex items-center gap-4 p-4 rounded-2xl border bg-card hover:bg-accent/40 transition-colors"
            >
              <div
                className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 text-white text-sm font-semibold ${
                  AVATAR_COLORS[i % AVATAR_COLORS.length]
                }`}
              >
                {getInitials(user.full_name)}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{user.full_name}</p>
                <p className="text-xs text-muted-foreground flex items-center gap-1 truncate mt-0.5">
                  <Mail className="w-3 h-3 shrink-0" />
                  {user.email}
                </p>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}
