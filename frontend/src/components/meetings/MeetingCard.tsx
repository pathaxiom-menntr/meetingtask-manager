"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { FileText, Calendar, Hash, Trash2, Eye, X } from "lucide-react";
import { formatDateRelative } from "@/lib/utils";
import type { Meeting } from "@/types";

interface MeetingCardProps {
  meeting: Meeting;
  taskCount?: number;
  onDelete?: (id: number) => void;
  index?: number;
}

export function MeetingCard({ meeting, taskCount = 0, onDelete, index = 0 }: MeetingCardProps) {
  const [transcriptOpen, setTranscriptOpen] = useState(false);

  return (
    <>
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: index * 0.06 }}
        className="group bg-card border rounded-2xl p-5 hover:shadow-md hover:-translate-y-0.5 transition-all"
      >
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-start gap-3 min-w-0">
            <div className="w-10 h-10 bg-indigo-600 rounded-xl flex items-center justify-center shrink-0">
              <FileText className="w-5 h-5 text-white" />
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
            <button
              onClick={() => setTranscriptOpen(true)}
              className="p-1.5 hover:bg-accent rounded-lg transition"
              title="View transcript"
            >
              <Eye className="w-3.5 h-3.5 text-muted-foreground" />
            </button>
            <button
              onClick={() => onDelete?.(meeting.id)}
              className="p-1.5 hover:bg-red-100 dark:hover:bg-red-900 rounded-lg transition"
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

      {/* Transcript Modal */}
      <AnimatePresence>
        {transcriptOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center">
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 bg-black/50"
              onClick={() => setTranscriptOpen(false)}
            />

            {/* Modal */}
            <motion.div
              initial={{ opacity: 0, scale: 0.96, y: 12 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.96, y: 12 }}
              transition={{ duration: 0.2 }}
              className="relative bg-background border rounded-2xl shadow-xl w-full max-w-2xl mx-4 flex flex-col"
              style={{ maxHeight: "80vh" }}
            >
              {/* Header */}
              <div className="flex items-center justify-between px-6 py-4 border-b shrink-0">
                <div className="flex items-center gap-3 min-w-0">
                  <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center shrink-0">
                    <FileText className="w-4 h-4 text-white" />
                  </div>
                  <div className="min-w-0">
                    <h2 className="font-semibold text-sm truncate">{meeting.title}</h2>
                    <p className="text-xs text-muted-foreground">{formatDateRelative(meeting.created_at)}</p>
                  </div>
                </div>
                <button
                  onClick={() => setTranscriptOpen(false)}
                  className="p-1.5 hover:bg-accent rounded-lg transition shrink-0"
                >
                  <X className="w-4 h-4 text-muted-foreground" />
                </button>
              </div>

              {/* Transcript body */}
              <div className="overflow-y-auto px-6 py-5 flex-1">
                <pre className="text-sm text-foreground whitespace-pre-wrap font-sans leading-relaxed">
                  {meeting.transcript}
                </pre>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </>
  );
}
