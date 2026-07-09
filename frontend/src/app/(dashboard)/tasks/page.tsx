"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import { CheckSquare, Plus, Filter } from "lucide-react";
import { toast } from "sonner";
import { tasksService } from "@/services/tasks.service";
import { usersService } from "@/services/users.service";
import { TaskCard } from "@/components/tasks/TaskCard";
import { EmptyState } from "@/components/common/EmptyState";
import { TaskCardSkeleton } from "@/components/common/LoadingSkeleton";
import { ConfirmDialog, useConfirmDialog } from "@/components/common/ConfirmDialog";
import { CreateTaskModal } from "@/components/tasks/CreateTaskModal";
import { useState } from "react";
import type { Task } from "@/types";

type Filter = "all" | "pending" | "completed";

export default function TasksPage() {
  const queryClient = useQueryClient();
  const { state: confirmState, confirm, close: closeConfirm } = useConfirmDialog();
  const [deleteLoading, setDeleteLoading] = useState(false);
  const [filter, setFilter] = useState<Filter>("all");
  const [createOpen, setCreateOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<"my" | "team">("my");

  const { data: tasks = [], isLoading } = useQuery({
    queryKey: ["tasks"],
    queryFn: () => tasksService.getTasks({ limit: 100 }),
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
    onError: (_e, _id, ctx) => {
      queryClient.setQueryData(["tasks"], ctx?.prev);
      toast.error("Failed to complete task");
    },
    onSuccess: () => {
      toast.success("Task completed!");
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });

  const uncompleteMutation = useMutation({
    mutationFn: tasksService.uncompleteTask,
    onMutate: async (taskId) => {
      await queryClient.cancelQueries({ queryKey: ["tasks"] });
      const prev = queryClient.getQueryData<Task[]>(["tasks"]);
      queryClient.setQueryData<Task[]>(["tasks"], (old) =>
        old?.map((t) => t.id === taskId ? { ...t, status: "pending" as const, completed_at: null } : t)
      );
      return { prev };
    },
    onError: (_e, _id, ctx) => {
      queryClient.setQueryData(["tasks"], ctx?.prev);
      toast.error("Failed to undo task completion");
    },
    onSuccess: () => {
      toast.success("Task marked as pending");
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: tasksService.deleteTask,
    onSuccess: () => {
      toast.success("Task deleted");
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
    },
  });

  const handleDelete = (id: number) => {
    confirm("Delete task?", "This cannot be undone.", async () => {
      setDeleteLoading(true);
      await deleteMutation.mutateAsync(id);
      setDeleteLoading(false);
      closeConfirm();
    });
  };

  const filtered = tasks.filter((t) => {
    if (filter === "pending") return t.status === "pending";
    if (filter === "completed") return t.status === "completed";
    return true;
  });

  const filters: { label: string; value: Filter }[] = [
    { label: "All", value: "all" },
    { label: "Pending", value: "pending" },
    { label: "Completed", value: "completed" },
  ];

  const { data: teamPendingTasks = [], isLoading: teamLoading } = useQuery({
    queryKey: ["team-pending-tasks"],
    queryFn: () => tasksService.getTeamPendingTasks({ limit: 100 }),
  });

  return (
    <div className="w-full space-y-6">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }}>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">Tasks</h1>
            <p className="text-muted-foreground text-sm mt-0.5">
              {tasks.filter((t) => t.status === "pending").length} pending · {tasks.filter((t) => t.status === "completed").length} completed
            </p>
          </div>
          <button
            onClick={() => setCreateOpen(true)}
            className="flex items-center gap-2 px-4 py-2 bg-indigo-500 hover:bg-indigo-600 text-white rounded-xl text-sm font-medium transition"
          >
            <Plus className="w-4 h-4" /> New Task
          </button>
        </div>
      </motion.div>

      {/* Tab Switcher */}
      <div className="flex items-center gap-6 border-b">
        <button
          onClick={() => setActiveTab("my")}
          className={`pb-3 text-sm font-medium border-b-2 transition-colors relative -mb-[1px] ${
            activeTab === "my"
              ? "border-indigo-500 text-indigo-600 dark:text-indigo-400"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          My Tasks
        </button>
        <button
          onClick={() => setActiveTab("team")}
          className={`pb-3 text-sm font-medium border-b-2 transition-colors relative -mb-[1px] ${
            activeTab === "team"
              ? "border-indigo-500 text-indigo-600 dark:text-indigo-400"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          Team Pending Tasks
        </button>
      </div>

      <div className="w-full">
        {activeTab === "my" ? (
          <div className="space-y-4 mt-4">
            <div className="flex items-center">
              <h2 className="text-lg font-semibold tracking-tight sr-only">My Tasks</h2>
              {/* Filter tabs */}
              <div className="flex items-center gap-1 bg-muted p-1 rounded-xl w-fit">
                {filters.map((f) => (
                  <button
                    key={f.value}
                    onClick={() => setFilter(f.value)}
                    className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
                      filter === f.value
                        ? "bg-background shadow-sm text-foreground"
                        : "text-muted-foreground hover:text-foreground"
                    }`}
                  >
                    {f.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Task list */}
            {isLoading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {Array(6).fill(0).map((_, i) => <TaskCardSkeleton key={i} />)}
              </div>
            ) : filtered.length === 0 ? (
              <EmptyState
                icon={CheckSquare}
                title="No tasks found"
                description={
                  filter === "all"
                    ? "Create your first task or upload a meeting transcript."
                    : `No ${filter} tasks.`
                }
                action={
                  filter === "all" ? (
                    <button
                      onClick={() => setCreateOpen(true)}
                      className="flex items-center gap-2 px-4 py-2 bg-indigo-500 text-white rounded-xl text-sm font-medium hover:bg-indigo-600 transition"
                    >
                      <Plus className="w-4 h-4" /> Create Task
                    </button>
                  ) : undefined
                }
              />
            ) : (
              <AnimatePresence>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                  {filtered.map((task, i) => (
                    <TaskCard
                      key={task.id}
                      task={task}
                      users={users}
                      index={i}
                      onComplete={(id) => completeMutation.mutate(id)}
                      onUncomplete={(id) => uncompleteMutation.mutate(id)}
                      onDelete={handleDelete}
                    />
                  ))}
                </div>
              </AnimatePresence>
            )}
          </div>
        ) : (
          <div className="space-y-4 mt-2">
            <h2 className="text-lg font-semibold tracking-tight sr-only">Team Pending Tasks</h2>
            {teamLoading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {Array(6).fill(0).map((_, i) => <TaskCardSkeleton key={i} />)}
              </div>
            ) : teamPendingTasks.length === 0 ? (
              <EmptyState
                icon={CheckSquare}
                title="No pending team tasks"
                description="Your team is all caught up!"
              />
            ) : (
              <AnimatePresence>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                  {teamPendingTasks.map((task, i) => (
                    <TaskCard
                      key={task.id}
                      task={task}
                      users={users}
                      index={i}
                      onComplete={(id) => completeMutation.mutate(id)}
                      onUncomplete={(id) => uncompleteMutation.mutate(id)}
                      onDelete={handleDelete}
                    />
                  ))}
                </div>
              </AnimatePresence>
            )}
          </div>
        )}
      </div>

      <CreateTaskModal
        open={createOpen}
        onClose={() => setCreateOpen(false)}
        users={users}
      />

      <ConfirmDialog {...confirmState} onCancel={closeConfirm} loading={deleteLoading} />
    </div>
  );
}
