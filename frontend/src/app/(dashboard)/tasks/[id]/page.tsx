"use client";

import { useParams, useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { motion } from "framer-motion";
import {
  ArrowLeft,
  CheckCircle2,
  Circle,
  Trash2,
  Clock,
  Calendar,
  CalendarCheck,
  Flame,
  AlertTriangle,
  ArrowUp,
  ArrowDown,
  UserCheck,
  UserCog,
  Link2,
  Edit2,
  Loader2,
} from "lucide-react";
import { toast } from "sonner";
import { tasksService } from "@/services/tasks.service";
import { usersService } from "@/services/users.service";
import { cn, formatDate, formatDateRelative, getInitials } from "@/lib/utils";
import type { TaskPriority } from "@/types";
import Link from "next/link";
import { ConfirmDialog, useConfirmDialog } from "@/components/common/ConfirmDialog";
import { useState } from "react";
import { useAuthStore } from "@/store/auth.store";

/* ─── Priority config ─────────────────────────────────────── */
const PRIORITY_CONFIG: Record<
  TaskPriority,
  { label: string; icon: React.ElementType; badge: string; bar: string }
> = {
  critical: {
    label: "Critical",
    icon: Flame,
    badge: "bg-red-500/10 text-red-500 border border-red-500/25",
    bar: "bg-gradient-to-r from-red-500 to-red-400",
  },
  high: {
    label: "High",
    icon: AlertTriangle,
    badge: "bg-orange-500/10 text-orange-500 border border-orange-500/25",
    bar: "bg-gradient-to-r from-orange-500 to-orange-400",
  },
  medium: {
    label: "Medium",
    icon: ArrowUp,
    badge: "bg-yellow-500/10 text-yellow-600 dark:text-yellow-400 border border-yellow-500/25",
    bar: "bg-gradient-to-r from-yellow-500 to-yellow-400",
  },
  low: {
    label: "Low",
    icon: ArrowDown,
    badge: "bg-sky-500/10 text-sky-500 border border-sky-500/25",
    bar: "bg-gradient-to-r from-sky-500 to-sky-400",
  },
};

const AVATAR_COLORS = [
  "bg-violet-500", "bg-indigo-500", "bg-rose-500",
  "bg-emerald-500", "bg-amber-500", "bg-cyan-500",
  "bg-pink-500", "bg-teal-500",
];

function getAvatarColor(id: number) {
  return AVATAR_COLORS[id % AVATAR_COLORS.length];
}

function UserAvatar({ name, id }: { name: string; id: number }) {
  return (
    <div
      className={cn(
        "w-9 h-9 rounded-full flex items-center justify-center text-white text-sm font-bold shrink-0",
        getAvatarColor(id)
      )}
    >
      {getInitials(name)}
    </div>
  );
}

/* ─── Skeleton ────────────────────────────────────────────── */
function Skeleton({ className }: { className?: string }) {
  return (
    <div className={cn("animate-pulse rounded-lg bg-muted", className)} />
  );
}

/* ─── Page ────────────────────────────────────────────────── */
export default function TaskDetailPage() {
  const params = useParams();
  const router = useRouter();
  const queryClient = useQueryClient();
  const taskId = Number(params.id);
  const { state: confirmState, confirm, close: closeConfirm } = useConfirmDialog();
  const [deleteLoading, setDeleteLoading] = useState(false);
  const currentUser = useAuthStore((s) => s.user);

  const { data: task, isLoading, isError } = useQuery({
    queryKey: ["task", taskId],
    queryFn: () => tasksService.getTaskById(taskId),
    enabled: !isNaN(taskId),
  });

  const { data: users = [] } = useQuery({
    queryKey: ["users"],
    queryFn: () => usersService.getUsers({ limit: 100 }),
  });

  const completeMutation = useMutation({
    mutationFn: () => tasksService.completeTask(taskId),
    onSuccess: () => {
      toast.success("Task marked as complete!");
      queryClient.invalidateQueries({ queryKey: ["task", taskId] });
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
    onError: () => toast.error("Failed to complete task"),
  });

  const deleteMutation = useMutation({
    mutationFn: () => tasksService.deleteTask(taskId),
    onSuccess: () => {
      toast.success("Task deleted");
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
      router.push("/tasks");
    },
    onError: () => toast.error("Failed to delete task"),
  });

  const handleDelete = () => {
    confirm("Delete task?", "This action cannot be undone.", async () => {
      setDeleteLoading(true);
      await deleteMutation.mutateAsync();
      setDeleteLoading(false);
      closeConfirm();
    });
  };

  if (isError) {
    return (
      <div className="max-w-3xl mx-auto text-center py-24">
        <p className="text-lg font-semibold mb-2">Task not found</p>
        <p className="text-muted-foreground text-sm mb-6">
          This task may have been deleted or you don't have access.
        </p>
        <Link
          href="/tasks"
          className="inline-flex items-center gap-2 text-sm text-indigo-500 hover:underline"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Tasks
        </Link>
      </div>
    );
  }

  const isCompleted = task?.status === "completed";
  const isAssignee = currentUser?.id === task?.assignee_id;
  const priority = (task?.priority ?? "medium") as TaskPriority;
  const priorityCfg = PRIORITY_CONFIG[priority] ?? PRIORITY_CONFIG.medium;
  const PriorityIcon = priorityCfg.icon;

  const assignee = users.find((u) => u.id === task?.assignee_id);
  const assigner = users.find((u) => u.id === task?.assigned_by);

  const dueDate = task?.due_date ? new Date(task.due_date) : null;
  const now = new Date();
  now.setHours(0, 0, 0, 0);
  const isOverdue = dueDate ? dueDate < now && !isCompleted : false;
  const isDueToday = dueDate ? dueDate.toDateString() === now.toDateString() : false;

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Back nav */}
      <motion.div initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }}>
        <Link
          href="/tasks"
          className="inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Tasks
        </Link>
      </motion.div>

      {isLoading ? (
        <div className="space-y-4">
          <Skeleton className="h-3 w-24" />
          <Skeleton className="h-8 w-3/4" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-5/6" />
          <div className="grid grid-cols-2 gap-4 mt-6">
            <Skeleton className="h-24 rounded-2xl" />
            <Skeleton className="h-24 rounded-2xl" />
            <Skeleton className="h-24 rounded-2xl" />
            <Skeleton className="h-24 rounded-2xl" />
          </div>
        </div>
      ) : task ? (
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.25 }}
          className="space-y-5"
        >
          {/* ── Hero card ── */}
          <div className="rounded-2xl border bg-card overflow-hidden">
            {/* Priority gradient top bar */}
            <div className={cn("h-1.5 w-full", priorityCfg.bar)} />

            <div className="p-6">
              {/* Top row: ticket ID + badges + actions */}
              <div className="flex items-center gap-2 mb-4 flex-wrap">
                <span className="font-mono text-xs text-muted-foreground/50 tracking-widest">
                  MTM-{task.id}
                </span>

                {/* Priority badge */}
                <span className={cn("inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-semibold", priorityCfg.badge)}>
                  <PriorityIcon className="w-3.5 h-3.5" />
                  {priorityCfg.label}
                </span>

                {/* Status badge */}
                <span
                  className={cn(
                    "inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-semibold",
                    isCompleted
                      ? "bg-emerald-500/10 text-emerald-500 border border-emerald-500/25"
                      : "bg-amber-500/10 text-amber-500 border border-amber-500/25"
                  )}
                >
                  {isCompleted ? <CheckCircle2 className="w-3.5 h-3.5" /> : <Clock className="w-3.5 h-3.5" />}
                  {isCompleted ? "Completed" : "In Progress"}
                </span>

                {task.meeting_id && (
                  <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs bg-indigo-500/10 text-indigo-500 border border-indigo-500/20">
                    <Link2 className="w-3.5 h-3.5" />
                    Meeting #{task.meeting_id}
                  </span>
                )}

                {/* Action buttons */}
                <div className="ml-auto flex items-center gap-2">
                  {/* Only the assignee can mark complete */}
                  {isAssignee && !isCompleted && (
                    <button
                      onClick={() => completeMutation.mutate()}
                      disabled={completeMutation.isPending}
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-emerald-500 hover:bg-emerald-600 text-white rounded-xl text-xs font-medium transition disabled:opacity-60"
                    >
                      {completeMutation.isPending ? (
                        <Loader2 className="w-3.5 h-3.5 animate-spin" />
                      ) : (
                        <CheckCircle2 className="w-3.5 h-3.5" />
                      )}
                      Mark Complete
                    </button>
                  )}
                  <button
                    onClick={handleDelete}
                    className="p-2 hover:bg-red-500/10 rounded-xl transition"
                    title="Delete task"
                  >
                    <Trash2 className="w-4 h-4 text-red-400" />
                  </button>
                </div>
              </div>

              {/* Title */}
              <h1
                className={cn(
                  "text-2xl font-bold tracking-tight mb-3",
                  isCompleted && "line-through text-muted-foreground"
                )}
              >
                {task.title}
              </h1>

              {/* Description */}
              {task.description ? (
                <p className="text-sm text-muted-foreground leading-relaxed whitespace-pre-wrap">
                  {task.description}
                </p>
              ) : (
                <p className="text-sm text-muted-foreground/40 italic">No description provided.</p>
              )}
            </div>
          </div>

          {/* ── Detail grid ── */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* Assignee */}
            <div className="rounded-2xl border bg-card p-4 space-y-3">
              <div className="flex items-center gap-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                <UserCheck className="w-3.5 h-3.5" />
                Assigned To
              </div>
              {assignee ? (
                <div className="flex items-center gap-3">
                  <UserAvatar name={assignee.full_name} id={assignee.id} />
                  <div>
                    <p className="text-sm font-semibold">{assignee.full_name}</p>
                    <p className="text-xs text-muted-foreground">{assignee.email}</p>
                  </div>
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">User #{task.assignee_id}</p>
              )}
            </div>

            {/* Assigner */}
            <div className="rounded-2xl border bg-card p-4 space-y-3">
              <div className="flex items-center gap-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                <UserCog className="w-3.5 h-3.5" />
                Assigned By
              </div>
              {assigner ? (
                <div className="flex items-center gap-3">
                  <UserAvatar name={assigner.full_name} id={assigner.id} />
                  <div>
                    <p className="text-sm font-semibold">{assigner.full_name}</p>
                    <p className="text-xs text-muted-foreground">{assigner.email}</p>
                  </div>
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">User #{task.assigned_by}</p>
              )}
            </div>

            {/* Due date */}
            <div className="rounded-2xl border bg-card p-4 space-y-3">
              <div className="flex items-center gap-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                <Calendar className="w-3.5 h-3.5" />
                Due Date
              </div>
              {task.due_date ? (
                <div>
                  <p
                    className={cn(
                      "text-sm font-semibold",
                      isOverdue ? "text-red-500" : isDueToday ? "text-orange-500" : ""
                    )}
                  >
                    {formatDate(task.due_date)}
                  </p>
                  <p className="text-xs text-muted-foreground mt-0.5">
                    {isOverdue
                      ? "⚠️ Overdue"
                      : isDueToday
                      ? "📅 Due today"
                      : `${Math.ceil((dueDate!.getTime() - now.getTime()) / 86400000)} days remaining`}
                  </p>
                </div>
              ) : (
                <p className="text-sm text-muted-foreground/50 italic">No due date set</p>
              )}
            </div>

            {/* Timeline */}
            <div className="rounded-2xl border bg-card p-4 space-y-3">
              <div className="flex items-center gap-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                <Clock className="w-3.5 h-3.5" />
                Timeline
              </div>
              <div className="space-y-1.5">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-indigo-500 shrink-0" />
                  <span className="text-xs text-muted-foreground">Created</span>
                  <span className="text-xs font-medium ml-auto">
                    {formatDateRelative(task.created_at)}
                  </span>
                </div>
                {isCompleted && task.completed_at && (
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-emerald-500 shrink-0" />
                    <span className="text-xs text-muted-foreground">Completed</span>
                    <span className="text-xs font-medium ml-auto text-emerald-500">
                      {formatDateRelative(task.completed_at)}
                    </span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </motion.div>
      ) : null}

      <ConfirmDialog {...confirmState} onCancel={closeConfirm} loading={deleteLoading} />
    </div>
  );
}
