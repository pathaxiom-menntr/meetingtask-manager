"use client";

import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { Users, Mail } from "lucide-react";
import { usersService } from "@/services/users.service";
import { EmptyState } from "@/components/common/EmptyState";
import { Skeleton } from "@/components/common/LoadingSkeleton";

function TeamMemberSkeleton() {
  return (
    <div className="flex flex-col gap-4 p-5 rounded-2xl border bg-card">
      <div className="flex items-start justify-between">
        <Skeleton className="w-12 h-12 rounded-xl shrink-0" />
        <Skeleton className="h-5 w-16 rounded-md" />
      </div>
      <div className="space-y-2 mt-2">
        <Skeleton className="h-5 w-3/4" />
        <Skeleton className="h-4 w-full" />
      </div>
      <div className="mt-2 pt-3 border-t flex items-center justify-end">
        <Skeleton className="h-3 w-12" />
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
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {Array(8).fill(0).map((_, i) => <TeamMemberSkeleton key={i} />)}
        </div>
      ) : users.length === 0 ? (
        <EmptyState
          icon={Users}
          title="No team members"
          description="No users have been added yet."
        />
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {users.map((user, i) => (
            <motion.div
              key={user.id}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.04 }}
              className="flex flex-col gap-4 p-5 rounded-2xl border bg-card hover:border-primary/50 hover:shadow-sm transition-all group relative overflow-hidden cursor-pointer"
            >
              <div className="flex items-start justify-between gap-2">
                <div
                  className={`w-12 h-12 rounded-xl flex items-center justify-center shrink-0 text-white text-base font-semibold shadow-sm ${
                    AVATAR_COLORS[i % AVATAR_COLORS.length]
                  }`}
                >
                  {getInitials(user.full_name)}
                </div>
                <div className="px-2.5 py-1 rounded-md bg-secondary/50 text-[10px] font-medium text-secondary-foreground uppercase tracking-wider">
                  Member
                </div>
              </div>
              
              <div className="flex-1 min-w-0 mt-2">
                <h3 className="text-base font-semibold truncate group-hover:text-primary transition-colors">
                  {user.full_name}
                </h3>
                <div className="flex items-center gap-1.5 mt-1.5 text-muted-foreground">
                  <Mail className="w-3.5 h-3.5 shrink-0" />
                  <p className="text-sm truncate">{user.email}</p>
                </div>
              </div>
              
              <div className="mt-2 pt-3 border-t flex items-center justify-end text-xs text-muted-foreground/70 font-medium">
                <span className="flex items-center gap-1"><Users className="w-3 h-3" /> Team</span>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}
