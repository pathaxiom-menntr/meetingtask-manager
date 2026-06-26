"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import type { LucideIcon } from "lucide-react";

interface StatsCardProps {
  label: string;
  value: number | string;
  icon: LucideIcon;
  color?: "indigo" | "emerald" | "amber" | "rose";
  suffix?: string;
  index?: number;
}

const colorMap = {
  indigo: {
    icon: "bg-gradient-to-br from-indigo-400 to-indigo-600 text-white shadow-sm shadow-indigo-200 dark:shadow-indigo-900/40",
    border: "border-t-indigo-500",
  },
  emerald: {
    icon: "bg-gradient-to-br from-emerald-400 to-emerald-600 text-white shadow-sm shadow-emerald-200 dark:shadow-emerald-900/40",
    border: "border-t-emerald-500",
  },
  amber: {
    icon: "bg-gradient-to-br from-amber-400 to-amber-500 text-white shadow-sm shadow-amber-200 dark:shadow-amber-900/40",
    border: "border-t-amber-500",
  },
  rose: {
    icon: "bg-gradient-to-br from-rose-400 to-rose-600 text-white shadow-sm shadow-rose-200 dark:shadow-rose-900/40",
    border: "border-t-rose-500",
  },
};

export function StatsCard({ label, value, icon: Icon, color = "indigo", suffix, index = 0 }: StatsCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.08, ease: "easeOut" }}
      className={cn(
        "bg-card rounded-2xl p-5 border border-t-2 shadow-sm hover:shadow-md hover:-translate-y-0.5 transition-all",
        colorMap[color].border
      )}
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-muted-foreground font-medium">{label}</p>
          <p className="text-3xl font-bold mt-1 tracking-tight">
            {value}
            {suffix && <span className="text-lg font-medium text-muted-foreground ml-1">{suffix}</span>}
          </p>
        </div>
        <div className={cn("w-10 h-10 rounded-xl flex items-center justify-center", colorMap[color].icon)}>
          <Icon className="w-5 h-5" />
        </div>
      </div>
    </motion.div>
  );
}
