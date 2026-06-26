import { api } from "./api";
import type { User, PaginationParams } from "@/types";

export const usersService = {
  getUsers: async (params?: PaginationParams): Promise<User[]> => {
    const res = await api.get<User[]>("/users/", { params });
    return res.data;
  },

  getUserById: async (id: number): Promise<User> => {
    const res = await api.get<User>(`/users/${id}`);
    return res.data;
  },
};
