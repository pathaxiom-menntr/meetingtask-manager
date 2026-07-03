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
  onUncomplete?: (id: number) => void;
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
  onUncomplete,
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
        "group relative rounded-xl border bg-card overflow-hidden",
        "transition-all duration-200",
        "hover:shadow-md hover:-translate-y-0.5",
        cfg.glow,
        isCompleted && "opacity-60 grayscale-[0.2]"
      )}
    >
      {/* Top accent bar */}
      <div className={cn("absolute top-0 inset-x-0 h-1", cfg.bar)} />

      <div className="p-4 pt-5">
        {/* ── Row 1: Header (ID, Priority, Actions) ── */}
        <div className="flex items-start justify-between gap-2 mb-3">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-mono text-[11px] text-muted-foreground font-semibold tracking-wider">
              MTM-{task.id}
            </span>
            <PriorityBadge priority={priority} />
          </div>

          <div className="flex items-center gap-0.5 text-muted-foreground shrink-0 bg-secondary/30 rounded-md p-0.5">
            {isAssignee ? (
              <button
                onClick={() => isCompleted ? onUncomplete?.(task.id) : onComplete?.(task.id)}
                title={isCompleted ? "Mark as pending" : "Mark as complete"}
                className={cn(
                  "p-1.5 rounded-md transition-all",
                  isCompleted
                    ? "text-emerald-500 bg-emerald-500/10 hover:bg-emerald-500/20"
                    : "text-muted-foreground hover:text-emerald-500 hover:bg-emerald-500/10"
                )}
              >
                {isCompleted ? <CheckCircle2 className="w-3.5 h-3.5" /> : <Circle className="w-3.5 h-3.5" />}
              </button>
            ) : (
              <span title="Only assignee can complete" className="p-1.5 text-muted-foreground/30 cursor-not-allowed">
                <LockIcon className="w-3.5 h-3.5" />
              </span>
            )}

            <Link
              href={`/tasks/${task.id}`}
              className="p-1.5 rounded-md transition hover:bg-accent text-muted-foreground hover:text-foreground"
              title="Open task"
            >
              <ExternalLink className="w-3.5 h-3.5" />
            </Link>

            <button
              onClick={() => onDelete?.(task.id)}
              className="p-1.5 rounded-md transition hover:bg-red-500/10"
              title="Delete task"
            >
              <Trash2 className="w-3.5 h-3.5 text-red-400" />
            </button>
          </div>
        </div>

        {/* ── Row 2: Title & Description ── */}
        <div className="mb-3.5">
          <h3
            className={cn(
              "text-[13px] font-semibold leading-snug mb-1.5",
              isCompleted && "line-through text-muted-foreground"
            )}
          >
            {task.title}
          </h3>

          {task.description && (
            <div>
              <AnimatePresence initial={false}>
                <motion.p
                  key={expanded ? "expanded" : "collapsed"}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className={cn(
                    "text-[11px] text-muted-foreground leading-relaxed",
                    !expanded && "line-clamp-2"
                  )}
                >
                  {task.description}
                </motion.p>
              </AnimatePresence>
              {hasLongDesc && (
                <button
                  onClick={() => setExpanded((v) => !v)}
                  className="mt-1 flex items-center gap-1 text-[10px] font-medium text-indigo-500 hover:text-indigo-400 transition"
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
        </div>

        {/* ── Row 3: Tags / Metadata ── */}
        <div className="flex flex-wrap gap-1.5 mb-3.5">
          <StatusBadge completed={isCompleted} />
          {task.meeting_id && (
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[11px] bg-indigo-500/10 text-indigo-500 border border-indigo-500/20 font-medium">
              <Link2 className="w-3 h-3" />
              Meeting #{task.meeting_id}
            </span>
          )}
        </div>

        {/* ── Divider ── */}
        <div className="border-t border-border/60 mb-3.5 -mx-4" />

        {/* ── Row 4: Footer (Users + Dates) ── */}
        <div className="flex items-center justify-between gap-4">
          {/* Left: Assignee */}
          <div className="flex items-center gap-2">
            <div className="flex -space-x-1.5">
              {assignee && <UserAvatar name={assignee.full_name} id={task.assignee_id} size="md" />}
              {assigner && assigner.id !== task.assignee_id && (
                <UserAvatar name={assigner.full_name} id={task.assigned_by} size="md" />
              )}
            </div>
            <span className="text-[10px] text-muted-foreground font-medium">
               {assignee ? assignee.full_name.split(' ')[0] : 'Unassigned'}
            </span>
          </div>

          {/* Right: Date */}
          <div className="flex items-center shrink-0">
            <DueDateChip due_date={task.due_date} completed={isCompleted} />
            {!task.due_date && !isCompleted && (
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-medium bg-muted/50 text-muted-foreground border border-border/50">
                <Clock className="w-3 h-3" />
                {formatDateRelative(task.created_at)}
              </span>
            )}
            {isCompleted && task.completed_at && !task.due_date && (
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-medium bg-emerald-500/10 text-emerald-500 border border-emerald-500/20">
                <CalendarCheck className="w-3 h-3" />
                Done
              </span>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  );
}
