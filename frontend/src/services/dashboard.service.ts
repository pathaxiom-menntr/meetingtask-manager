import { api } from "./api";
import type { DashboardStats } from "@/types";

export const dashboardService = {
  getStats: async (): Promise<DashboardStats> => {
    const res = await api.get<DashboardStats>("/dashboard/");
    return res.data;
  },
};
