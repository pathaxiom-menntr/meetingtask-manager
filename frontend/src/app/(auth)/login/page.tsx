"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { motion } from "framer-motion";
import { toast } from "sonner";
import {
  Loader2, Mail, Lock, Eye, EyeOff,
  Sparkles, CheckSquare, Clock, ShieldCheck, Users, AlertCircle,
} from "lucide-react";
import { authService } from "@/services/auth.service";
import { useAuthStore } from "@/store/auth.store";
import { useState } from "react";

const loginSchema = z.object({
  email: z.string().email("Enter a valid email"),
  password: z.string().min(1, "Password is required"),
  team_code: z
    .string()
    .min(3, "Team code must be at least 3 characters")
    .max(50, "Team code is too long"),
});

type LoginForm = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const router = useRouter();
  const { setTokens, setUser } = useAuthStore();
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [serverError, setServerError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginForm>({ resolver: zodResolver(loginSchema) });

  const onSubmit = async (data: LoginForm) => {
    setLoading(true);
    setServerError(null);
    try {
      const tokens = await authService.login(data);
      setTokens(tokens.access_token, tokens.refresh_token);
      const user = await authService.me();
      setUser(user);
      toast.success(`Welcome back, ${user.full_name.split(" ")[0]}!`);
      router.push("/dashboard");
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        "Invalid credentials. Please check your email, password, and team code.";
      setServerError(msg);
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  const features = [
    { icon: Sparkles, label: "AI Summaries" },
    { icon: CheckSquare, label: "Auto Tasks" },
    { icon: Clock, label: "Async Ready" },
  ];

  return (
    <div className="space-y-7">
      {/* Mobile logo */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35, ease: "easeOut" }}
        className="flex items-center gap-2 lg:hidden"
      >
        <div className="relative shrink-0">
          <div
            className="absolute inset-0 rounded-xl blur-md opacity-50"
            style={{ background: "linear-gradient(135deg, #818cf8, #7c3aed)" }}
          />
          <div
            className="relative w-10 h-10 rounded-xl flex items-center justify-center"
            style={{
              background: "linear-gradient(135deg, #6366f1 0%, #7c3aed 100%)",
              boxShadow: "inset 0 1px 0 rgba(255,255,255,0.2), 0 2px 10px rgba(99,102,241,0.35)",
            }}
          >
            <svg width="18" height="18" viewBox="0 0 16 16" fill="none">
              <path
                d="M2 13V3L8 9L14 3V13"
                stroke="white"
                strokeWidth="1.9"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </div>
        </div>
        <div className="flex flex-col leading-none">
          <span className="font-semibold text-base tracking-tight">MeetingTask</span>
          <span className="text-[10px] text-indigo-400 tracking-widest uppercase mt-0.5 font-medium">AI</span>
        </div>
      </motion.div>

      {/* Heading */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35, ease: "easeOut", delay: 0.04 }}
      >
        <h2 className="text-2xl font-bold tracking-tight">Sign in to your account</h2>
        <p className="text-muted-foreground mt-1 text-sm">
          Don&apos;t have an account?{" "}
          <Link href="/register" className="text-indigo-500 hover:text-indigo-600 font-medium">
            Create one free
          </Link>
        </p>
      </motion.div>

      {/* Feature micro-chips */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.4, delay: 0.1 }}
        className="flex items-center gap-4"
      >
        {features.map(({ icon: Icon, label }) => (
          <span key={label} className="flex items-center gap-1 text-xs text-gray-400">
            <Icon className="w-3 h-3 text-indigo-400" />
            {label}
          </span>
        ))}
      </motion.div>

      <motion.form
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35, ease: "easeOut", delay: 0.16 }}
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

        {/* Password */}
        <div className="space-y-1.5">
          <div className="flex items-center justify-between">
            <label className="text-sm font-medium" htmlFor="password">Password</label>
            <Link href="#" className="text-xs text-muted-foreground hover:text-foreground">
              Forgot password?
            </Link>
          </div>
          <div className="relative">
            <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
            <input
              id="password"
              type={showPassword ? "text" : "password"}
              placeholder="••••••••"
              className="w-full pl-10 pr-10 py-2.5 rounded-xl border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 transition"
              {...register("password")}
            />
            <button
              type="button"
              onClick={() => setShowPassword((v) => !v)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition"
              tabIndex={-1}
            >
              {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            </button>
          </div>
          {errors.password && <p className="text-xs text-red-500">{errors.password.message}</p>}
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
          {errors.team_code ? (
            <p className="text-xs text-red-500">{errors.team_code.message}</p>
          ) : (
            <p className="text-xs text-muted-foreground">
              Enter the team code you used when registering.
            </p>
          )}
        </div>

        {/* Inline server error banner */}
        {serverError && (
          <div className="flex items-start gap-2.5 px-4 py-3 rounded-xl bg-red-50 border border-red-200 text-red-700">
            <AlertCircle className="w-4 h-4 mt-0.5 shrink-0 text-red-500" />
            <p className="text-xs leading-relaxed font-medium">{serverError}</p>
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          className="w-full py-2.5 text-white rounded-xl font-medium text-sm transition flex items-center justify-center gap-2 disabled:opacity-60 disabled:cursor-not-allowed"
          style={{
            background: loading
              ? "#818cf8"
              : "linear-gradient(135deg, #6366f1 0%, #7c3aed 100%)",
          }}
        >
          {loading && <Loader2 className="w-4 h-4 animate-spin" />}
          {loading ? "Signing in..." : "Sign in"}
        </button>

        {/* Security note */}
        <div className="flex items-center justify-center gap-1.5 pt-1">
          <ShieldCheck className="w-3 h-3 text-gray-300" />
          <span className="text-xs text-gray-300">Secured with end-to-end encryption</span>
        </div>
      </motion.form>
    </div>
  );
}
