import { api } from "./api";
import type { LoginRequest, RegisterRequest, AuthTokens, User } from "@/types";

export const authService = {
  login: async (data: LoginRequest): Promise<AuthTokens> => {
    const res = await api.post<AuthTokens>("/auth/login", data);
    return res.data;
  },

  register: async (data: RegisterRequest): Promise<User> => {
    const res = await api.post<User>("/auth/register", data);
    return res.data;
  },

  refresh: async (refresh_token: string): Promise<AuthTokens> => {
    const res = await api.post<AuthTokens>("/auth/refresh", { refresh_token });
    return res.data;
  },

  me: async (): Promise<User> => {
    const res = await api.get<User>("/auth/me");
    return res.data;
  },
};
