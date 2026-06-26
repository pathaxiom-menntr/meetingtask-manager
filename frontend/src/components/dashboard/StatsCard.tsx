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
  indigo: "bg-indigo-50 text-indigo-600 dark:bg-indigo-950 dark:text-indigo-400",
  emerald: "bg-emerald-50 text-emerald-600 dark:bg-emerald-950 dark:text-emerald-400",
  amber: "bg-amber-50 text-amber-600 dark:bg-amber-950 dark:text-amber-400",
  rose: "bg-rose-50 text-rose-600 dark:bg-rose-950 dark:text-rose-400",
};

export function StatsCard({ label, value, icon: Icon, color = "indigo", suffix, index = 0 }: StatsCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.08, ease: "easeOut" }}
      className="bg-card rounded-2xl p-5 border shadow-sm hover:shadow-md transition-shadow"
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-muted-foreground font-medium">{label}</p>
          <p className="text-3xl font-bold mt-1 tracking-tight">
            {value}
            {suffix && <span className="text-lg font-medium text-muted-foreground ml-1">{suffix}</span>}
          </p>
        </div>
        <div className={cn("w-10 h-10 rounded-xl flex items-center justify-center", colorMap[color])}>
          <Icon className="w-5 h-5" />
        </div>
      </div>
    </motion.div>
  );
}
