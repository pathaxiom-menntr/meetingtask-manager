"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { motion } from "framer-motion";
import { toast } from "sonner";
import { Loader2, Users } from "lucide-react";
import { authService } from "@/services/auth.service";
import { useState } from "react";

const registerSchema = z
  .object({
    full_name: z.string().min(2, "Name must be at least 2 characters"),
    email: z.string().email("Enter a valid email"),
    password: z.string().min(6, "Password must be at least 6 characters"),
    confirm_password: z.string(),
    team_code: z
      .string()
      .min(3, "Team code must be at least 3 characters")
      .max(50, "Team code is too long")
      .regex(/^[a-zA-Z0-9_-]+$/, "Only letters, numbers, hyphens and underscores allowed"),
  })
  .refine((d) => d.password === d.confirm_password, {
    message: "Passwords don't match",
    path: ["confirm_password"],
  });

type RegisterForm = z.infer<typeof registerSchema>;

export default function RegisterPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterForm>({ resolver: zodResolver(registerSchema) });

  const onSubmit = async (data: RegisterForm) => {
    setLoading(true);
    try {
      await authService.register({
        full_name: data.full_name,
        email: data.email,
        password: data.password,
        team_code: data.team_code,
      });
      toast.success("Account created! Please sign in.");
      router.push("/login");
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        "Registration failed";
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  const textFields = [
    { id: "full_name", label: "Full Name", type: "text", placeholder: "Jane Smith" },
    { id: "email", label: "Email", type: "email", placeholder: "you@company.com" },
    { id: "password", label: "Password", type: "password", placeholder: "••••••••" },
    { id: "confirm_password", label: "Confirm Password", type: "password", placeholder: "••••••••" },
  ] as const;

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
      className="space-y-8"
    >
      <div className="flex items-center gap-2 lg:hidden">
        <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center">
          <span className="text-white font-bold text-sm">M</span>
        </div>
        <span className="font-semibold text-lg">Meeting Task Manager</span>
      </div>

      <div>
        <h2 className="text-2xl font-bold tracking-tight">Create your account</h2>
        <p className="text-muted-foreground mt-1 text-sm">
          Already have one?{" "}
          <Link href="/login" className="text-indigo-500 hover:text-indigo-600 font-medium">
            Sign in
          </Link>
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        {textFields.map((field) => (
          <div key={field.id} className="space-y-1.5">
            <label className="text-sm font-medium" htmlFor={field.id}>
              {field.label}
            </label>
            <input
              id={field.id}
              type={field.type}
              placeholder={field.placeholder}
              className="w-full px-4 py-2.5 rounded-xl border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 transition"
              {...register(field.id)}
            />
            {errors[field.id] && (
              <p className="text-xs text-red-500">{errors[field.id]?.message}</p>
            )}
          </div>
        ))}

        {/* Team Code field */}
        <div className="space-y-1.5">
          <label className="text-sm font-medium" htmlFor="team_code">
            Team Code
          </label>
          <div className="relative">
            <Users className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
            <input
              id="team_code"
              type="text"
              placeholder="e.g. ACME-2024"
              className="w-full pl-10 pr-4 py-2.5 rounded-xl border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 transition uppercase-placeholder"
              style={{ textTransform: "uppercase" }}
              {...register("team_code")}
            />
          </div>
          {errors.team_code ? (
            <p className="text-xs text-red-500">{errors.team_code.message}</p>
          ) : (
            <p className="text-xs text-muted-foreground">
              Enter your organization&apos;s team code. All teammates must use the same code.
            </p>
          )}
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-medium text-sm transition flex items-center justify-center gap-2 disabled:opacity-60"
        >
          {loading && <Loader2 className="w-4 h-4 animate-spin" />}
          {loading ? "Creating account..." : "Create account"}
        </button>
      </form>
    </motion.div>
  );
}
