"use client";

import { useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useDropzone } from "react-dropzone";
import { Upload, FileText, CheckCircle2, AlertCircle, X, Loader2, Sparkles, ArrowRight, UserCheck } from "lucide-react";
import Link from "next/link";
import { toast } from "sonner";
import { meetingsService } from "@/services/meetings.service";
import { useQueryClient } from "@tanstack/react-query";
import { cn } from "@/lib/utils";
import type { MeetingUploadResponse, AutoAssignedTask } from "@/types";

type Stage = "idle" | "uploading" | "extracting" | "generating" | "done" | "error";

const stages: { key: Stage; label: string }[] = [
  { key: "uploading", label: "Uploading file..." },
  { key: "extracting", label: "Extracting transcript..." },
  { key: "generating", label: "Generating AI tasks..." },
  { key: "done", label: "Tasks generated successfully!" },
];

export default function UploadPage() {
  const queryClient = useQueryClient();
  const [stage, setStage] = useState<Stage>("idle");
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState("");
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState<MeetingUploadResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const ALLOWED_EXTENSIONS = [".txt", ".md", ".pdf", ".docx"];

  const onDrop = useCallback((accepted: File[]) => {
    if (accepted.length > 0) {
      const selectedFile = accepted[0];
      const fileName = selectedFile.name.toLowerCase();
      const hasValidExtension = ALLOWED_EXTENSIONS.some((ext) =>
        fileName.endsWith(ext)
      );
      if (!hasValidExtension) {
        setError(
          `Unsupported file type. Only ${ALLOWED_EXTENSIONS.join(", ")} files are supported.`
        );
        return;
      }
      setError(null);
      setFile(selectedFile);
      setTitle(selectedFile.name.replace(/\.[^.]+$/, ""));
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "text/plain": [".txt"],
      "application/pdf": [".pdf"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
      "text/markdown": [".md"],
    },
    maxFiles: 1,
    disabled: stage !== "idle",
    onDropRejected: () => {
      setError(
        "Unsupported file type. Only PDF, DOCX, TXT, and MD files are supported."
      );
    },
  });

  const handleUpload = async () => {
    if (!file || !title.trim()) {
      toast.error("Please add a title and select a file");
      return;
    }

    // Pre-flight: reject empty / whitespace-only text files before hitting the network
    if (file.name.toLowerCase().endsWith(".txt") || file.name.toLowerCase().endsWith(".md")) {
      const content = await file.text();
      if (!content.trim()) {
        const emptyMsg = "The file appears to be empty. Please upload a file with content.";
        setError(emptyMsg);
        toast.error(emptyMsg);
        return;
      }
    }

    setError(null);
    setStage("uploading");
    setProgress(0);

    // Keep references so we can cancel them if the upload fails before they fire
    const extractingTimer = setTimeout(() => setStage("extracting"), 800);
    const generatingTimer = setTimeout(() => setStage("generating"), 2000);

    try {
      const data = await meetingsService.uploadTranscript(title, file, setProgress);
      setResult(data);
      setStage("done");
      queryClient.invalidateQueries({ queryKey: ["meetings", "tasks", "dashboard"] });
      toast.success(`${data.tasks.length} task${data.tasks.length !== 1 ? "s" : ""} generated!`);
    } catch (err: unknown) {
      // Cancel pending stage transitions so the error state is not overwritten
      clearTimeout(extractingTimer);
      clearTimeout(generatingTimer);

      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        "Upload failed";
      setError(msg);
      setStage("error");
      toast.error(msg);
    }
  };

  const reset = () => {
    setStage("idle");
    setFile(null);
    setTitle("");
    setProgress(0);
    setResult(null);
    setError(null);
  };

  const currentStageIndex = stages.findIndex((s) => s.key === stage);

  return (
    <div className="w-full space-y-6">
      <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-2xl font-bold tracking-tight">AI Upload</h1>
        <p className="text-muted-foreground text-sm mt-0.5">
          Upload a meeting transcript and let AI extract all action items automatically.
        </p>
      </motion.div>

      {stage === "idle" || stage === "error" ? (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-4">
          {/* Title */}
          <div className="space-y-1.5">
            <label className="text-sm font-medium">Meeting Title</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Q2 Planning Meeting"
              className="w-full px-4 py-2.5 rounded-xl border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 transition"
            />
          </div>

          {/* Dropzone */}
          <div
            {...getRootProps()}
            className={cn(
              "relative border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all",
              isDragActive
                ? "border-indigo-500 bg-indigo-50 dark:bg-indigo-950/20"
                : "border-muted hover:border-indigo-300 hover:bg-muted/30"
            )}
          >
            <input {...getInputProps()} />
            <motion.div
              animate={{ scale: isDragActive ? 1.05 : 1 }}
              transition={{ duration: 0.2 }}
              className="flex flex-col items-center gap-3"
            >
              <div className={cn(
                "w-14 h-14 rounded-2xl flex items-center justify-center",
                isDragActive ? "bg-indigo-100 dark:bg-indigo-900" : "bg-muted"
              )}>
                <Upload className={cn("w-7 h-7", isDragActive ? "text-indigo-500" : "text-muted-foreground")} />
              </div>
              {file ? (
                <div className="flex items-center gap-2">
                  <FileText className="w-4 h-4 text-indigo-500" />
                  <span className="text-sm font-medium">{file.name}</span>
                  <button
                    onClick={(e) => { e.stopPropagation(); setFile(null); }}
                    className="p-0.5 hover:bg-muted rounded"
                  >
                    <X className="w-3.5 h-3.5 text-muted-foreground" />
                  </button>
                </div>
              ) : (
                <>
                  <p className="text-sm font-medium">
                    {isDragActive ? "Drop it here!" : "Drag & drop or click to upload"}
                  </p>
                  <p className="text-xs text-muted-foreground">Supports PDF, DOCX, TXT, MD</p>
                </>
              )}
            </motion.div>
          </div>

          {error && (
            <div className="flex items-center gap-2 p-3 bg-red-50 dark:bg-red-950/20 rounded-xl text-red-600 text-sm">
              <AlertCircle className="w-4 h-4 shrink-0" />
              {error}
            </div>
          )}

          <button
            onClick={handleUpload}
            disabled={!file || !title.trim()}
            className="w-full py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-medium text-sm transition flex items-center justify-center gap-2 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            <Sparkles className="w-4 h-4" /> Generate Tasks with AI
          </button>
        </motion.div>
      ) : stage === "done" && result ? (
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
          {/* Success header */}
          <div
            className="flex items-center gap-3 p-4 rounded-2xl border"
            style={{ background: "linear-gradient(135deg, rgba(16,185,129,0.08), rgba(5,150,105,0.04))" }}
          >
            <div className="w-9 h-9 rounded-xl bg-emerald-500/10 flex items-center justify-center shrink-0">
              <CheckCircle2 className="w-5 h-5 text-emerald-500" />
            </div>
            <div>
              <p className="text-sm font-semibold text-emerald-700 dark:text-emerald-400">
                {result.tasks.length} task{result.tasks.length !== 1 ? "s" : ""} generated!
              </p>
              <p className="text-xs text-emerald-600/70 dark:text-emerald-500/70 mt-0.5">
                {result.skipped.length > 0
                  ? `${result.skipped.length} skipped — no users available.`
                  : result.auto_assigned_tasks?.some((t) => t.auto_assigned)
                  ? `${result.auto_assigned_tasks.filter((t) => t.auto_assigned).length} auto-assigned to least-loaded team member.`
                  : "All action items extracted successfully."}
              </p>
            </div>
          </div>

          {/* Meeting info */}
          <div className="bg-card border rounded-2xl p-4 flex items-center justify-between">
            <div>
              <p className="text-sm font-medium">{result.meeting.title}</p>
              <p className="text-xs text-muted-foreground mt-0.5">Meeting ID #{result.meeting.id}</p>
            </div>
            <Link
              href="/tasks"
              className="flex items-center gap-1.5 text-xs font-medium text-indigo-500 hover:text-indigo-600 transition"
            >
              View Tasks <ArrowRight className="w-3 h-3" />
            </Link>
          </div>

          {/* Generated tasks */}
          {result.tasks.length > 0 && (
            <div className="space-y-2">
              <h3 className="text-sm font-semibold">Generated Tasks</h3>
              {result.tasks.map((task, i) => (
                <motion.div
                  key={task.id}
                  initial={{ opacity: 0, x: -8 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.06 }}
                  className="flex items-start gap-3 p-3 bg-card border rounded-xl"
                >
                  <CheckCircle2 className="w-4 h-4 text-indigo-500 shrink-0 mt-0.5" />
                  <div className="min-w-0">
                    <p className="text-sm font-medium">{task.title}</p>
                    {task.description && (
                      <p className="text-xs text-muted-foreground mt-0.5 truncate">{task.description}</p>
                    )}
                  </div>
                </motion.div>
              ))}
            </div>
          )}

          {/* Auto-assigned tasks notice */}
          {result.auto_assigned_tasks?.some((t) => t.auto_assigned) && (
            <div className="space-y-2">
              <h3 className="text-sm font-semibold text-blue-600 dark:text-blue-400">Auto-Assigned</h3>
              {result.auto_assigned_tasks
                .filter((t): t is AutoAssignedTask => t.auto_assigned)
                .map((item, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, x: -8 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.06 }}
                    className="flex items-start gap-3 p-3 rounded-xl border border-blue-200 dark:border-blue-800"
                    style={{ background: "rgba(59,130,246,0.06)" }}
                  >
                    <UserCheck className="w-4 h-4 text-blue-500 shrink-0 mt-0.5" />
                    <div className="min-w-0">
                      <p className="text-sm font-medium">{item.task.title}</p>
                      <p className="text-xs text-blue-600/80 dark:text-blue-400/80 mt-0.5">
                        No assignee found — assigned to{" "}
                        <span className="font-semibold">{item.auto_assigned_to}</span>{" "}
                        (fewest tasks)
                      </p>
                    </div>
                  </motion.div>
                ))}
            </div>
          )}

          {/* Skipped tasks */}
          {result.skipped.length > 0 && (
            <div className="space-y-2">
              <h3 className="text-sm font-semibold text-muted-foreground">Skipped</h3>
              {result.skipped.map((s, i) => (
                <div key={i} className="flex items-start gap-2 p-3 bg-muted/50 rounded-xl">
                  <AlertCircle className="w-4 h-4 text-amber-500 shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm">{s.title ?? "Untitled"}</p>
                    <p className="text-xs text-muted-foreground">{s.reason}</p>
                  </div>
                </div>
              ))}
            </div>
          )}

          <div className="flex gap-3">
            <button
              onClick={reset}
              className="flex-1 py-2.5 border rounded-xl text-sm font-medium hover:bg-accent transition"
            >
              Upload Another
            </button>
            <Link
              href="/tasks"
              className="flex-1 py-2.5 rounded-xl text-sm font-medium text-white flex items-center justify-center gap-2 transition"
              style={{ background: "linear-gradient(135deg, #6366f1 0%, #7c3aed 100%)" }}
            >
              Go to Tasks <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </motion.div>
      ) : (
        /* Processing stages */
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
          <div className="bg-card border rounded-2xl p-8 space-y-7 relative overflow-hidden">

            {/* Subtle background radial glow */}
            <div
              className="pointer-events-none absolute inset-0 rounded-2xl"
              style={{ background: "radial-gradient(ellipse at 50% 0%, rgba(99,102,241,0.07), transparent 70%)" }}
            />

            {/* Spinner */}
            <div className="flex flex-col items-center text-center gap-3">
              <div className="relative">
                <div
                  className="absolute inset-0 rounded-2xl blur-xl opacity-50"
                  style={{ background: "linear-gradient(135deg, #6366f1, #7c3aed)" }}
                />
                <div
                  className="relative w-14 h-14 rounded-2xl flex items-center justify-center"
                  style={{
                    background: "linear-gradient(135deg, #6366f1 0%, #7c3aed 100%)",
                    boxShadow: "inset 0 1px 0 rgba(255,255,255,0.2)",
                  }}
                >
                  <Loader2 className="w-7 h-7 text-white animate-spin" />
                </div>
              </div>
              <div>
                <p className="text-sm font-semibold">Processing your transcript...</p>
                <p className="text-xs text-muted-foreground mt-0.5">AI is reading and extracting action items</p>
              </div>
            </div>

            {/* Stage steps */}
            <div className="space-y-3">
              {stages.slice(0, 3).map((s, i) => {
                const isDone = currentStageIndex > i;
                const isCurrent = currentStageIndex === i;
                return (
                  <div key={s.key} className="flex items-center gap-3">
                    <div className={cn(
                      "w-6 h-6 rounded-full flex items-center justify-center shrink-0 transition-all duration-300",
                      isDone
                        ? "bg-emerald-500"
                        : isCurrent
                        ? "ring-2 ring-indigo-300 ring-offset-1"
                        : "bg-muted"
                    )}
                    style={isCurrent ? { background: "linear-gradient(135deg, #6366f1, #7c3aed)" } : undefined}
                    >
                      {isDone ? (
                        <CheckCircle2 className="w-3.5 h-3.5 text-white" />
                      ) : isCurrent ? (
                        <Loader2 className="w-3 h-3 text-white animate-spin" />
                      ) : (
                        <span className="text-[10px] text-muted-foreground font-medium">{i + 1}</span>
                      )}
                    </div>
                    <span className={cn(
                      "text-sm transition-colors",
                      isDone ? "text-emerald-600 dark:text-emerald-400" :
                      isCurrent ? "text-foreground font-semibold" :
                      "text-muted-foreground"
                    )}>
                      {s.label}
                    </span>
                    {isCurrent && (
                      <motion.span
                        initial={{ opacity: 0 }}
                        animate={{ opacity: [0.4, 1, 0.4] }}
                        transition={{ duration: 1.5, repeat: Infinity }}
                        className="ml-auto text-[10px] font-medium px-2 py-0.5 rounded-full"
                        style={{ background: "rgba(99,102,241,0.1)", color: "#6366f1" }}
                      >
                        in progress
                      </motion.span>
                    )}
                  </div>
                );
              })}
            </div>

            {/* Progress bar */}
            <div className="h-1 bg-muted rounded-full overflow-hidden">
              <motion.div
                className="h-full rounded-full"
                style={{ background: "linear-gradient(90deg, #6366f1, #7c3aed, #06b6d4)" }}
                initial={{ width: "5%" }}
                animate={{ width: `${Math.max(10, ((currentStageIndex + 1) / 3) * 100)}%` }}
                transition={{ duration: 0.6, ease: "easeOut" }}
              />
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
}
