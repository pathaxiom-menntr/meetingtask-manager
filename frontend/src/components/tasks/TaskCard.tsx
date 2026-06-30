"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  CheckCircle2,
  Circle,
  Trash2,
  ExternalLink,
  AlertTriangle,
  Flame,
  ArrowUp,
  ArrowDown,
  Calendar,
  CalendarCheck,
  Clock,
  ChevronDown,
  ChevronUp,
  Link2,
  UserCheck,
  UserCog,
  LockIcon,
} from "lucide-react";
import { cn, formatDate, formatDateRelative, getInitials } from "@/lib/utils";
import type { Task, User as UserType, TaskPriority } from "@/types";
import Link from "next/link";
import { useAuthStore } from "@/store/auth.store";

interface TaskCardProps {
  task: Task;
  users?: UserType[];
  onComplete?: (id: number) => void;
  onDelete?: (id: number) => void;
  index?: number;
}

/* ─── Priority config ────────────────────────────────────── */
const PRIORITY_CONFIG: Record<
  TaskPriority,
  {
    label: string;
    icon: React.ElementType;
    badge: string;
    bar: string;
    glow: string;
  }
> = {
  critical: {
    label: "Critical",
    icon: Flame,
    badge: "bg-red-500/10 text-red-500 border border-red-500/25 dark:bg-red-500/15",
    bar: "bg-red-500",
    glow: "hover:shadow-red-500/10",
  },
  high: {
    label: "High",
    icon: AlertTriangle,
    badge: "bg-orange-500/10 text-orange-500 border border-orange-500/25 dark:bg-orange-500/15",
    bar: "bg-orange-500",
    glow: "hover:shadow-orange-500/10",
  },
  medium: {
    label: "Medium",
    icon: ArrowUp,
    badge: "bg-yellow-500/10 text-yellow-600 dark:text-yellow-400 border border-yellow-500/25 dark:bg-yellow-500/15",
    bar: "bg-yellow-400",
    glow: "hover:shadow-yellow-500/5",
  },
  low: {
    label: "Low",
    icon: ArrowDown,
    badge: "bg-sky-500/10 text-sky-500 border border-sky-500/25 dark:bg-sky-500/15",
    bar: "bg-sky-400",
    glow: "hover:shadow-sky-500/5",
  },
};

/* ─── Avatar colors ──────────────────────────────────────── */
const AVATAR_COLORS = [
  "bg-violet-500",
  "bg-indigo-500",
  "bg-rose-500",
  "bg-emerald-500",
  "bg-amber-500",
  "bg-cyan-500",
  "bg-pink-500",
  "bg-teal-500",
];

function getAvatarColor(id: number) {
  return AVATAR_COLORS[id % AVATAR_COLORS.length];
}

/* ─── Sub-components ─────────────────────────────────────── */
function UserAvatar({
  name,
  id,
  size = "sm",
}: {
  name: string;
  id: number;
  size?: "sm" | "md";
}) {
  const sz = size === "md" ? "w-7 h-7 text-[11px]" : "w-5 h-5 text-[9px]";
  return (
    <div
      className={cn(
        "rounded-full flex items-center justify-center text-white font-bold shrink-0",
        sz,
        getAvatarColor(id)
      )}
      title={name}
    >
      {getInitials(name)}
    </div>
  );
}

function PriorityBadge({ priority }: { priority: TaskPriority }) {
  const cfg = PRIORITY_CONFIG[priority] ?? PRIORITY_CONFIG.medium;
  const Icon = cfg.icon;
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[11px] font-semibold tracking-wide shrink-0",
        cfg.badge
      )}
    >
      <Icon className="w-3 h-3" />
      {cfg.label}
    </span>
  );
}

function StatusBadge({ completed }: { completed: boolean }) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[11px] font-semibold shrink-0",
        completed
          ? "bg-emerald-500/10 text-emerald-500 border border-emerald-500/25"
          : "bg-amber-500/10 text-amber-500 border border-amber-500/25"
      )}
    >
      {completed ? (
        <CheckCircle2 className="w-3 h-3" />
      ) : (
        <Clock className="w-3 h-3" />
      )}
      {completed ? "Completed" : "In Progress"}
    </span>
  );
}

function DueDateChip({
  due_date,
  completed,
}: {
  due_date: string | null;
  completed: boolean;
}) {
  if (!due_date) return null;
  const dueDate = new Date(due_date);
  const now = new Date();
  now.setHours(0, 0, 0, 0);
  const isOverdue = !completed && dueDate < now;
  const isToday =
    dueDate.toDateString() === now.toDateString();

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[11px] font-medium shrink-0",
        isOverdue
          ? "bg-red-500/10 text-red-500 border border-red-500/25"
          : isToday
            ? "bg-orange-500/10 text-orange-500 border border-orange-500/25"
            : "bg-muted text-muted-foreground border border-border"
      )}
    >
      <Calendar className="w-3 h-3" />
      {isOverdue ? "Overdue · " : isToday ? "Due today · " : ""}
      {formatDate(due_date)}
    </span>
  );
}

function UserChip({
  label,
  user,
  userId,
  icon: Icon,
}: {
  label: string;
  user: UserType | undefined;
  userId: number;
  icon: React.ElementType;
}) {
  return (
    <div className="flex items-center gap-1.5 min-w-0">
      <Icon className="w-3 h-3 text-muted-foreground/50 shrink-0" />
      {user ? (
        <>
          <UserAvatar name={user.full_name} id={user.id} />
          <span className="text-xs text-muted-foreground truncate max-w-[100px]">
            {user.full_name}
          </span>
        </>
      ) : (
        <span className="text-xs text-muted-foreground">#{userId}</span>
      )}
    </div>
  );
}

/* ─── Main card ──────────────────────────────────────────── */
export function TaskCard({
  task,
  users = [],
  onComplete,
  onDelete,
  index = 0,
}: TaskCardProps) {
  const [expanded, setExpanded] = useState(false);
  const currentUser = useAuthStore((s) => s.user);
  const isCompleted = task.status === "completed";
  const isAssignee = currentUser?.id === task.assignee_id;
  const priority = (task.priority ?? "medium") as TaskPriority;
  const cfg = PRIORITY_CONFIG[priority] ?? PRIORITY_CONFIG.medium;

  const assignee = users.find((u) => u.id === task.assignee_id);
  const assigner = users.find((u) => u.id === task.assigned_by);
  const hasLongDesc = (task.description?.length ?? 0) > 100;

  return (
    <motion.div
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -6, scale: 0.98 }}
      transition={{ duration: 0.22, delay: index * 0.035 }}
      layout
      className={cn(
        "group relative rounded-2xl border bg-card overflow-hidden",
        "transition-all duration-200",
        "hover:shadow-lg hover:-translate-y-0.5",
        cfg.glow,
        isCompleted && "opacity-55"
      )}
    >
      {/* Left priority bar */}
      <div
        className={cn(
          "absolute left-0 inset-y-0 w-[3px] rounded-r-full",
          cfg.bar
        )}
      />

      <div className="pl-4 pr-4 pt-3.5 pb-3">
        {/* ── Row 1: ID + badges + actions ── */}
        <div className="flex items-center gap-2 mb-2">
          <span className="font-mono text-[10px] text-muted-foreground/40 tracking-widest shrink-0">
            MTM-{task.id}
          </span>

          <PriorityBadge priority={priority} />
          <StatusBadge completed={isCompleted} />

          {task.meeting_id && (
            <span className="hidden sm:inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[11px] bg-indigo-500/10 text-indigo-500 border border-indigo-500/20">
              <Link2 className="w-3 h-3" />
              Meeting #{task.meeting_id}
            </span>
          )}

          {/* Push actions to the right */}
          <div className="ml-auto flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
            {/* Complete — only for assignee */}
            {isAssignee ? (
              <button
                onClick={() => !isCompleted && onComplete?.(task.id)}
                disabled={isCompleted}
                title={isCompleted ? "Already completed" : "Mark as complete"}
                className={cn(
                  "p-1.5 rounded-lg transition-all",
                  isCompleted
                    ? "text-emerald-500 cursor-default"
                    : "text-muted-foreground hover:text-emerald-500 hover:bg-emerald-500/10 hover:scale-110"
                )}
              >
                {isCompleted ? (
                  <CheckCircle2 className="w-4 h-4" />
                ) : (
                  <Circle className="w-4 h-4" />
                )}
              </button>
            ) : (
              <span
                title="Only the assignee can complete this task"
                className="p-1.5 text-muted-foreground/30 cursor-not-allowed"
              >
                <LockIcon className="w-3.5 h-3.5" />
              </span>
            )}

            <Link
              href={`/tasks/${task.id}`}
              className="p-1.5 rounded-lg transition hover:bg-accent text-muted-foreground hover:text-foreground"
              title="Open task"
            >
              <ExternalLink className="w-3.5 h-3.5" />
            </Link>

            <button
              onClick={() => onDelete?.(task.id)}
              className="p-1.5 rounded-lg transition hover:bg-red-500/10"
              title="Delete task"
            >
              <Trash2 className="w-3.5 h-3.5 text-red-400" />
            </button>
          </div>
        </div>

        {/* ── Row 2: Title ── */}
        <div className="flex items-start gap-2 mb-1">
          {/* Inline complete toggle — only for the assignee */}
          {isAssignee ? (
            <button
              onClick={() => !isCompleted && onComplete?.(task.id)}
              disabled={isCompleted}
              title={isCompleted ? "Completed" : "Mark as complete"}
              className={cn(
                "mt-0.5 shrink-0 transition-all",
                isCompleted
                  ? "text-emerald-500 cursor-default"
                  : "text-muted-foreground/30 hover:text-emerald-500 hover:scale-110"
              )}
            >
              {isCompleted ? (
                <CheckCircle2 className="w-4 h-4" />
              ) : (
                <Circle className="w-4 h-4" />
              )}
            </button>
          ) : (
            <span className="mt-0.5 shrink-0">
              {isCompleted ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-500" />
              ) : (
                <Circle className="w-4 h-4 text-muted-foreground/20" />
              )}
            </span>
          )}

          <h3
            className={cn(
              "text-sm font-semibold leading-snug flex-1",
              isCompleted && "line-through text-muted-foreground"
            )}
          >
            {task.title}
          </h3>
        </div>

        {/* ── Row 3: Description (expandable) ── */}
        {task.description && (
          <div className="ml-6 mb-2">
            <AnimatePresence initial={false}>
              <motion.p
                key={expanded ? "expanded" : "collapsed"}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className={cn(
                  "text-xs text-muted-foreground leading-relaxed",
                  !expanded && "line-clamp-2"
                )}
              >
                {task.description}
              </motion.p>
            </AnimatePresence>

            {hasLongDesc && (
              <button
                onClick={() => setExpanded((v) => !v)}
                className="mt-1 flex items-center gap-1 text-[11px] text-indigo-500 hover:text-indigo-400 transition"
              >
                {expanded ? (
                  <>
                    <ChevronUp className="w-3 h-3" /> Show less
                  </>
                ) : (
                  <>
                    <ChevronDown className="w-3 h-3" /> Show more
                  </>
                )}
              </button>
            )}
          </div>
        )}

        {/* ── Divider ── */}
        <div className="border-t border-border/50 my-2.5 ml-6" />

        {/* ── Row 4: Meta footer ── */}
        <div className="ml-6 flex items-center justify-between flex-wrap gap-x-4 gap-y-1.5">
          {/* Left: assignee + assigner */}
          <div className="flex items-center gap-3 flex-wrap">
            <UserChip
              label="Assignee"
              user={assignee}
              userId={task.assignee_id}
              icon={UserCheck}
            />
            <span className="text-muted-foreground/20 text-xs">|</span>
            <UserChip
              label="From"
              user={assigner}
              userId={task.assigned_by}
              icon={UserCog}
            />
          </div>

          {/* Right: date info */}
          <div className="flex items-center gap-2 flex-wrap">
            {/* Due date */}
            <DueDateChip due_date={task.due_date} completed={isCompleted} />

            {/* Completed date */}
            {isCompleted && task.completed_at && (
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[11px] bg-emerald-500/10 text-emerald-500 border border-emerald-500/25">
                <CalendarCheck className="w-3 h-3" />
                Done {formatDateRelative(task.completed_at)}
              </span>
            )}

            {/* Created at (when no due date & not completed) */}
            {!task.due_date && !isCompleted && (
              <span className="inline-flex items-center gap-1 text-[11px] text-muted-foreground/50">
                <Clock className="w-3 h-3" />
                {formatDateRelative(task.created_at)}
              </span>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  );
}
