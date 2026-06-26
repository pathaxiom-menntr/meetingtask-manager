"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import { Video, Plus, Trash2 } from "lucide-react";
import { toast } from "sonner";
import { meetingsService } from "@/services/meetings.service";
import { MeetingCard } from "@/components/meetings/MeetingCard";
import { EmptyState } from "@/components/common/EmptyState";
import { MeetingCardSkeleton } from "@/components/common/LoadingSkeleton";
import { ConfirmDialog, useConfirmDialog } from "@/components/common/ConfirmDialog";
import { useState } from "react";
import Link from "next/link";

export default function MeetingsPage() {
  const queryClient = useQueryClient();
  const { state: confirmState, confirm, close: closeConfirm } = useConfirmDialog();
  const [deleteLoading, setDeleteLoading] = useState(false);

  const { data: meetings = [], isLoading } = useQuery({
    queryKey: ["meetings"],
    queryFn: () => meetingsService.getMeetings({ limit: 50 }),
  });

  const deleteMutation = useMutation({
    mutationFn: meetingsService.deleteMeeting,
    onSuccess: () => {
      toast.success("Meeting deleted");
      queryClient.invalidateQueries({ queryKey: ["meetings"] });
    },
    onError: () => toast.error("Failed to delete meeting"),
  });

  const handleDelete = (id: number) => {
    confirm(
      "Delete meeting?",
      "This will permanently delete the meeting and all its generated tasks.",
      async () => {
        setDeleteLoading(true);
        await deleteMutation.mutateAsync(id);
        setDeleteLoading(false);
        closeConfirm();
      }
    );
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -8 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Meetings</h1>
          <p className="text-muted-foreground text-sm mt-0.5">
            {meetings.length} meeting{meetings.length !== 1 ? "s" : ""} processed
          </p>
        </div>
        <Link
          href="/upload"
          className="flex items-center gap-2 px-4 py-2 bg-indigo-500 hover:bg-indigo-600 text-white rounded-xl text-sm font-medium transition"
        >
          <Plus className="w-4 h-4" /> Upload Transcript
        </Link>
      </motion.div>

      {/* List */}
      {isLoading ? (
        <div className="space-y-4">
          {Array(4).fill(0).map((_, i) => <MeetingCardSkeleton key={i} />)}
        </div>
      ) : meetings.length === 0 ? (
        <EmptyState
          icon={Video}
          title="No meetings yet"
          description="Upload your first meeting transcript and let AI extract tasks automatically."
          action={
            <Link
              href="/upload"
              className="flex items-center gap-2 px-4 py-2 bg-indigo-500 text-white rounded-xl text-sm font-medium hover:bg-indigo-600 transition"
            >
              <Plus className="w-4 h-4" /> Upload Transcript
            </Link>
          }
        />
      ) : (
        <AnimatePresence>
          <div className="grid gap-4 sm:grid-cols-2">
            {meetings.map((meeting, i) => (
              <MeetingCard
                key={meeting.id}
                meeting={meeting}
                index={i}
                onDelete={handleDelete}
              />
            ))}
          </div>
        </AnimatePresence>
      )}

      <ConfirmDialog
        {...confirmState}
        onCancel={closeConfirm}
        loading={deleteLoading}
      />
    </div>
  );
}
