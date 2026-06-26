"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { X, Loader2 } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { tasksService } from "@/services/tasks.service";
import type { User } from "@/types";

const schema = z.object({
  title: z.string().min(1, "Title is required"),
  description: z.string().optional(),
  assignee_id: z.string().min(1, "Assignee is required"),
});

type FormData = z.infer<typeof schema>;

interface CreateTaskModalProps {
  open: boolean;
  onClose: () => void;
  users: User[];
}

export function CreateTaskModal({ open, onClose, users }: CreateTaskModalProps) {
  const queryClient = useQueryClient();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<FormData>({ resolver: zodResolver(schema) });

  const mutation = useMutation({
    mutationFn: (data: FormData) =>
      tasksService.createTask({
        title: data.title,
        description: data.description,
        assignee_id: Number(data.assignee_id),
      }),
    onSuccess: () => {
      toast.success("Task created!");
      queryClient.invalidateQueries({ queryKey: ["tasks", "dashboard"] });
      reset();
      onClose();
    },
    onError: () => toast.error("Failed to create task"),
  });

  const handleClose = () => {
    reset();
    onClose();
  };

  return (
    <AnimatePresence>
      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 bg-black/40 backdrop-blur-sm"
            onClick={handleClose}
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.96, y: 8 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.96, y: 8 }}
            transition={{ duration: 0.2 }}
            className="relative bg-background rounded-2xl border shadow-xl p-6 w-full max-w-md mx-4"
          >
            <div className="flex items-center justify-between mb-5">
              <h2 className="text-base font-semibold">Create Task</h2>
              <button
                onClick={handleClose}
                className="p-1.5 hover:bg-accent rounded-lg transition"
              >
                <X className="w-4 h-4 text-muted-foreground" />
              </button>
            </div>

            <form onSubmit={handleSubmit((d) => mutation.mutate(d))} className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-sm font-medium">Title</label>
                <input
                  {...register("title")}
                  placeholder="Write Q2 report..."
                  className="w-full px-4 py-2.5 rounded-xl border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 transition"
                />
                {errors.title && <p className="text-xs text-red-500">{errors.title.message}</p>}
              </div>

              <div className="space-y-1.5">
                <label className="text-sm font-medium">Description <span className="text-muted-foreground">(optional)</span></label>
                <textarea
                  {...register("description")}
                  rows={3}
                  placeholder="Add more context..."
                  className="w-full px-4 py-2.5 rounded-xl border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 transition resize-none"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-sm font-medium">Assign To</label>
                <select
                  {...register("assignee_id")}
                  className="w-full px-4 py-2.5 rounded-xl border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 transition"
                >
                  <option value="">Select a team member...</option>
                  {users.map((u) => (
                    <option key={u.id} value={u.id}>
                      {u.full_name}
                    </option>
                  ))}
                </select>
                {errors.assignee_id && <p className="text-xs text-red-500">{errors.assignee_id.message}</p>}
              </div>

              <div className="flex gap-2 pt-1">
                <button
                  type="button"
                  onClick={handleClose}
                  className="flex-1 py-2.5 border rounded-xl text-sm font-medium hover:bg-accent transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={mutation.isPending}
                  className="flex-1 py-2.5 bg-indigo-500 hover:bg-indigo-600 text-white rounded-xl text-sm font-medium transition flex items-center justify-center gap-2 disabled:opacity-60"
                >
                  {mutation.isPending && <Loader2 className="w-4 h-4 animate-spin" />}
                  {mutation.isPending ? "Creating..." : "Create Task"}
                </button>
              </div>
            </form>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
