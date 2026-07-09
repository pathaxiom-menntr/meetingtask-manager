"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { motion } from "framer-motion";
import { toast } from "sonner";
import { Loader2, Mail, Lock, Eye, EyeOff, Users, ArrowLeft } from "lucide-react";
import { authService } from "@/services/auth.service";
import { useState } from "react";

const changePasswordSchema = z.object({
  email: z.string().email("Enter a valid email"),
  team_code: z.string().min(3, "Team code must be at least 3 characters"),
  old_password: z.string().min(1, "Old password is required"),
  new_password: z.string().min(6, "New password must be at least 6 characters"),
  confirm_password: z.string(),
}).refine((data) => data.new_password === data.confirm_password, {
  message: "Passwords don't match",
  path: ["confirm_password"],
});

type ChangePasswordForm = z.infer<typeof changePasswordSchema>;

export default function ForgotPasswordPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [showOldPassword, setShowOldPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ChangePasswordForm>({ resolver: zodResolver(changePasswordSchema) });

  const onSubmit = async (data: ChangePasswordForm) => {
    setLoading(true);
    try {
      await authService.changePassword({
        email: data.email,
        team_code: data.team_code,
        old_password: data.old_password,
        new_password: data.new_password,
      });
      toast.success("Password changed successfully!");
      router.push("/login");
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        "Failed to change password";
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-7">
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35, ease: "easeOut" }}
      >
        <Link href="/login" className="inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition mb-6">
          <ArrowLeft className="w-4 h-4" />
          Back to login
        </Link>
        <h2 className="text-2xl font-bold tracking-tight">Change Password</h2>
        <p className="text-muted-foreground mt-1 text-sm">
          Enter your current details to change your password.
        </p>
      </motion.div>

      <motion.form
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35, ease: "easeOut", delay: 0.1 }}
        onSubmit={handleSubmit(onSubmit)}
        className="space-y-4"
      >
        {/* Email */}
        <div className="space-y-1.5">
          <label className="text-sm font-medium" htmlFor="email">Email</label>
          <div className="relative">
            <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
            <input
              id="email"
              type="email"
              placeholder="you@company.com"
              className="w-full pl-10 pr-4 py-2.5 rounded-xl border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 transition"
              {...register("email")}
            />
          </div>
          {errors.email && <p className="text-xs text-red-500">{errors.email.message}</p>}
        </div>

        {/* Team Code */}
        <div className="space-y-1.5">
          <label className="text-sm font-medium" htmlFor="team_code">Team Code</label>
          <div className="relative">
            <Users className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
            <input
              id="team_code"
              type="text"
              placeholder="e.g. ACME-2024"
              className="w-full pl-10 pr-4 py-2.5 rounded-xl border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 transition"
              {...register("team_code")}
            />
          </div>
          {errors.team_code && <p className="text-xs text-red-500">{errors.team_code.message}</p>}
        </div>

        {/* Old Password */}
        <div className="space-y-1.5">
          <label className="text-sm font-medium" htmlFor="old_password">Old Password</label>
          <div className="relative">
            <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
            <input
              id="old_password"
              type={showOldPassword ? "text" : "password"}
              placeholder="••••••••"
              className="w-full pl-10 pr-10 py-2.5 rounded-xl border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 transition"
              {...register("old_password")}
            />
            <button
              type="button"
              onClick={() => setShowOldPassword((v) => !v)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition"
              tabIndex={-1}
            >
              {showOldPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            </button>
          </div>
          {errors.old_password && <p className="text-xs text-red-500">{errors.old_password.message}</p>}
        </div>

        {/* New Password */}
        <div className="space-y-1.5">
          <label className="text-sm font-medium" htmlFor="new_password">New Password</label>
          <div className="relative">
            <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
            <input
              id="new_password"
              type={showNewPassword ? "text" : "password"}
              placeholder="••••••••"
              className="w-full pl-10 pr-10 py-2.5 rounded-xl border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 transition"
              {...register("new_password")}
            />
            <button
              type="button"
              onClick={() => setShowNewPassword((v) => !v)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition"
              tabIndex={-1}
            >
              {showNewPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            </button>
          </div>
          {errors.new_password && <p className="text-xs text-red-500">{errors.new_password.message}</p>}
        </div>

        {/* Confirm New Password */}
        <div className="space-y-1.5">
          <label className="text-sm font-medium" htmlFor="confirm_password">Confirm New Password</label>
          <div className="relative">
            <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
            <input
              id="confirm_password"
              type={showNewPassword ? "text" : "password"}
              placeholder="••••••••"
              className="w-full pl-10 pr-10 py-2.5 rounded-xl border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 transition"
              {...register("confirm_password")}
            />
          </div>
          {errors.confirm_password && <p className="text-xs text-red-500">{errors.confirm_password.message}</p>}
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full py-2.5 text-white rounded-xl font-medium text-sm transition flex items-center justify-center gap-2 mt-2 disabled:opacity-60 disabled:cursor-not-allowed"
          style={{
            background: loading
              ? "#818cf8"
              : "linear-gradient(135deg, #6366f1 0%, #7c3aed 100%)",
          }}
        >
          {loading && <Loader2 className="w-4 h-4 animate-spin" />}
          {loading ? "Updating..." : "Change Password"}
        </button>
      </motion.form>
    </div>
  );
}
