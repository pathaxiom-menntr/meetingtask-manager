"use client";

import { motion } from "framer-motion";
import { CheckCircle2, Circle, Trash2, ExternalLink } from "lucide-react";
import { cn, formatDateRelative, getInitials } from "@/lib/utils";
import type { Task } from "@/types";
import Link from "next/link";

interface TaskCardProps {
  task: Task;
  onComplete?: (id: number) => void;
  onDelete?: (id: number) => void;
  index?: number;
}

export function TaskCard({ task, onComplete, onDelete, index = 0 }: TaskCardProps) {
  const isCompleted = task.status === "completed";

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.97 }}
      transition={{ duration: 0.3, delay: index * 0.05 }}
      className={cn(
        "group flex items-start gap-4 p-4 rounded-2xl border bg-card hover:shadow-sm transition-all",
        isCompleted && "opacity-60"
      )}
    >
      {/* Complete button */}
      <button
        onClick={() => !isCompleted && onComplete?.(task.id)}
        disabled={isCompleted}
        className={cn(
          "mt-0.5 shrink-0 transition-colors",
          isCompleted ? "text-emerald-500 cursor-default" : "text-muted-foreground hover:text-emerald-500"
        )}
      >
        {isCompleted ? (
          <CheckCircle2 className="w-5 h-5" />
        ) : (
          <Circle className="w-5 h-5" />
        )}
      </button>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between gap-2">
          <p className={cn("text-sm font-medium truncate", isCompleted && "line-through text-muted-foreground")}>
            {task.title}
          </p>
          <span
            className={cn(
              "shrink-0 text-xs px-2 py-0.5 rounded-full font-medium",
              isCompleted
                ? "bg-emerald-50 text-emerald-600 dark:bg-emerald-950 dark:text-emerald-400"
                : "bg-amber-50 text-amber-600 dark:bg-amber-950 dark:text-amber-400"
            )}
          >
            {isCompleted ? "Done" : "Pending"}
          </span>
        </div>

        {task.description && (
          <p className="text-xs text-muted-foreground mt-1 line-clamp-1">{task.description}</p>
        )}

        <div className="flex items-center gap-3 mt-2">
          {/* Assignee avatar */}
          <div className="w-5 h-5 bg-indigo-500 rounded-full flex items-center justify-center text-white text-[9px] font-bold">
            {getInitials("User")}
          </div>
          <span className="text-xs text-muted-foreground">{formatDateRelative(task.created_at)}</span>
          {task.meeting_id && (
            <span className="text-xs bg-muted px-1.5 py-0.5 rounded-md">
              Meeting #{task.meeting_id}
            </span>
          )}
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity shrink-0">
        <Link
          href={`/tasks/${task.id}`}
          className="p-1.5 hover:bg-accent rounded-lg transition"
        >
          <ExternalLink className="w-3.5 h-3.5 text-muted-foreground" />
        </Link>
        <button
          onClick={() => onDelete?.(task.id)}
          className="p-1.5 hover:bg-red-50 dark:hover:bg-red-950/30 rounded-lg transition"
        >
          <Trash2 className="w-3.5 h-3.5 text-red-400" />
        </button>
      </div>
    </motion.div>
  );
}
