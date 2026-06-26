"use client";

import { motion } from "framer-motion";
import { FileText, Calendar, Hash, Trash2, Eye } from "lucide-react";
import { formatDateRelative } from "@/lib/utils";
import type { Meeting } from "@/types";
import Link from "next/link";

interface MeetingCardProps {
  meeting: Meeting;
  taskCount?: number;
  onDelete?: (id: number) => void;
  index?: number;
}

export function MeetingCard({ meeting, taskCount = 0, onDelete, index = 0 }: MeetingCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.06 }}
      className="group bg-card border rounded-2xl p-5 hover:shadow-md transition-all"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3 min-w-0">
          <div className="w-10 h-10 bg-indigo-50 dark:bg-indigo-950 rounded-xl flex items-center justify-center shrink-0">
            <FileText className="w-5 h-5 text-indigo-500" />
          </div>
          <div className="min-w-0">
            <h3 className="font-semibold text-sm truncate">{meeting.title}</h3>
            <p className="text-xs text-muted-foreground mt-0.5 line-clamp-2">
              {meeting.transcript.slice(0, 100)}...
            </p>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity shrink-0">
          <Link
            href={`/meetings/${meeting.id}`}
            className="p-1.5 hover:bg-accent rounded-lg transition"
          >
            <Eye className="w-3.5 h-3.5 text-muted-foreground" />
          </Link>
          <button
            onClick={() => onDelete?.(meeting.id)}
            className="p-1.5 hover:bg-red-50 dark:hover:bg-red-950/30 rounded-lg transition"
          >
            <Trash2 className="w-3.5 h-3.5 text-red-400" />
          </button>
        </div>
      </div>

      <div className="flex items-center gap-4 mt-4 pt-4 border-t">
        <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
          <Calendar className="w-3.5 h-3.5" />
          <span>{formatDateRelative(meeting.created_at)}</span>
        </div>
        <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
          <Hash className="w-3.5 h-3.5" />
          <span>{taskCount} task{taskCount !== 1 ? "s" : ""}</span>
        </div>
        <div className="ml-auto">
          <span className="text-xs px-2 py-0.5 bg-emerald-50 text-emerald-600 dark:bg-emerald-950 dark:text-emerald-400 rounded-full font-medium">
            Processed
          </span>
        </div>
      </div>
    </motion.div>
  );
}
