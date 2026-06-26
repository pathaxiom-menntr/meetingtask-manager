"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import { CheckSquare, Clock, CheckCircle2, Video, Plus, TrendingUp } from "lucide-react";
import { toast } from "sonner";
import { dashboardService } from "@/services/dashboard.service";
import { tasksService } from "@/services/tasks.service";
import { usersService } from "@/services/users.service";
import { StatsCard } from "@/components/dashboard/StatsCard";
import { TaskCard } from "@/components/tasks/TaskCard";
import { EmptyState } from "@/components/common/EmptyState";
import { StatsSkeleton, TaskCardSkeleton } from "@/components/common/LoadingSkeleton";
import { ConfirmDialog, useConfirmDialog } from "@/components/common/ConfirmDialog";
import { useAuthStore } from "@/store/auth.store";
import { useState } from "react";
import Link from "next/link";
import type { Task } from "@/types";

export default function DashboardPage() {
  const { user } = useAuthStore();
  const queryClient = useQueryClient();
  const { state: confirmState, confirm, close: closeConfirm } = useConfirmDialog();
  const [deleteLoading, setDeleteLoading] = useState(false);

  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ["dashboard"],
    queryFn: dashboardService.getStats,
  });

  const { data: tasks = [], isLoading: tasksLoading } = useQuery({
    queryKey: ["tasks"],
    queryFn: () => tasksService.getTasks({ limit: 50 }),
  });

  const { data: users = [] } = useQuery({
    queryKey: ["users"],
    queryFn: () => usersService.getUsers({ limit: 100 }),
  });

  const completeMutation = useMutation({
    mutationFn: tasksService.completeTask,
    onMutate: async (taskId) => {
      await queryClient.cancelQueries({ queryKey: ["tasks"] });
      const prev = queryClient.getQueryData<Task[]>(["tasks"]);
      queryClient.setQueryData<Task[]>(["tasks"], (old) =>
        old?.map((t) => t.id === taskId ? { ...t, status: "completed" as const } : t)
      );
      return { prev };
    },
    onError: (_err, _id, ctx) => {
      queryClient.setQueryData(["tasks"], ctx?.prev);
      toast.error("Failed to complete task");
    },
    onSuccess: () => {
      toast.success("Task marked as complete!");
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: tasksService.deleteTask,
    onSuccess: () => {
      toast.success("Task deleted");
      queryClient.invalidateQueries({ queryKey: ["tasks", "dashboard"] });
    },
    onError: () => toast.error("Failed to delete task"),
  });

  const handleDelete = (id: number) => {
    confirm(
      "Delete task?",
      "This action cannot be undone.",
      async () => {
        setDeleteLoading(true);
        await deleteMutation.mutateAsync(id);
        setDeleteLoading(false);
        closeConfirm();
      }
    );
  };

  const pendingTasks = tasks.filter((t) => t.status === "pending");
  const completedTasks = tasks.filter((t) => t.status === "completed");

  const statsCards = [
    { label: "Total Tasks", value: stats?.total_tasks ?? 0, icon: CheckSquare, color: "indigo" as const },
    { label: "Pending", value: stats?.pending_tasks ?? 0, icon: Clock, color: "amber" as const },
    { label: "Completed", value: stats?.completed_tasks ?? 0, icon: CheckCircle2, color: "emerald" as const },
    { label: "Meetings", value: stats?.total_meetings ?? 0, icon: Video, color: "rose" as const },
  ];

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -8 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-2xl font-bold tracking-tight">
            Good morning, {user?.full_name?.split(" ")[0]} 👋
          </h1>
          <p className="text-muted-foreground text-sm mt-0.5">
            Here's what's happening with your tasks today.
          </p>
        </div>
        <Link
          href="/upload"
          className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-indigo-500 to-violet-500 hover:from-indigo-600 hover:to-violet-600 text-white rounded-xl text-sm font-medium transition shadow-sm shadow-indigo-200 dark:shadow-none"
        >
          <Plus className="w-4 h-4" /> New Upload
        </Link>
      </motion.div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {statsLoading
          ? Array(4).fill(0).map((_, i) => <StatsSkeleton key={i} />)
          : statsCards.map((card, i) => (
              <StatsCard key={card.label} {...card} index={i} />
            ))}
      </div>

      {/* Completion rate */}
      {stats && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="bg-card border rounded-2xl p-5"
        >
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-indigo-500" />
              <span className="text-sm font-medium">Completion Rate</span>
            </div>
            <span className="text-sm font-bold text-indigo-500">{stats.completion_rate}%</span>
          </div>
          <div className="h-2 bg-muted rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${stats.completion_rate}%` }}
              transition={{ duration: 0.8, delay: 0.4, ease: "easeOut" }}
              className="h-full bg-indigo-500 rounded-full"
            />
          </div>
        </motion.div>
      )}

      {/* Task sections */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Pending */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-semibold flex items-center gap-2">
              <Clock className="w-4 h-4 text-amber-500" /> Pending Tasks
              <span className="text-xs bg-amber-50 dark:bg-amber-950 text-amber-600 dark:text-amber-400 px-1.5 py-0.5 rounded-full">
                {pendingTasks.length}
              </span>
            </h2>
          </div>
          <div className="space-y-2">
            {tasksLoading ? (
              Array(3).fill(0).map((_, i) => <TaskCardSkeleton key={i} />)
            ) : pendingTasks.length === 0 ? (
              <EmptyState
                icon={CheckSquare}
                title="All caught up!"
                description="No pending tasks right now."
              />
            ) : (
              <AnimatePresence>
                {pendingTasks.slice(0, 6).map((task, i) => (
                  <TaskCard
                    key={task.id}
                    task={task}
                    users={users}
                    index={i}
                    onComplete={(id) => completeMutation.mutate(id)}
                    onDelete={handleDelete}
                  />
                ))}
              </AnimatePresence>
            )}
          </div>
        </div>

        {/* Completed */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-semibold flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-500" /> Completed Tasks
              <span className="text-xs bg-emerald-50 dark:bg-emerald-950 text-emerald-600 dark:text-emerald-400 px-1.5 py-0.5 rounded-full">
                {completedTasks.length}
              </span>
            </h2>
          </div>
          <div className="space-y-2">
            {tasksLoading ? (
              Array(3).fill(0).map((_, i) => <TaskCardSkeleton key={i} />)
            ) : completedTasks.length === 0 ? (
              <EmptyState
                icon={CheckCircle2}
                title="No completed tasks yet"
                description="Complete a task to see it here."
              />
            ) : (
              <AnimatePresence>
                {completedTasks.slice(0, 6).map((task, i) => (
                  <TaskCard key={task.id} task={task} users={users} index={i} onDelete={handleDelete} />
                ))}
              </AnimatePresence>
            )}
          </div>
        </div>
      </div>

      <ConfirmDialog
        {...confirmState}
        onCancel={closeConfirm}
        loading={deleteLoading}
      />
    </div>
  );
}
