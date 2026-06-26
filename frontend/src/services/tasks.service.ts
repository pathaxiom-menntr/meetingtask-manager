import { api } from "./api";
import type { Task, TaskCreate, TaskUpdate, PaginationParams } from "@/types";

export const tasksService = {
  getTasks: async (params?: PaginationParams): Promise<Task[]> => {
    const res = await api.get<Task[]>("/tasks/", { params });
    return res.data;
  },

  getTaskById: async (id: number): Promise<Task> => {
    const res = await api.get<Task>(`/tasks/${id}`);
    return res.data;
  },

  createTask: async (data: TaskCreate): Promise<Task> => {
    const res = await api.post<Task>("/tasks/", data);
    return res.data;
  },

  updateTask: async (id: number, data: TaskUpdate): Promise<Task> => {
    const res = await api.put<Task>(`/tasks/${id}`, data);
    return res.data;
  },

  completeTask: async (id: number): Promise<Task> => {
    const res = await api.patch<Task>(`/tasks/${id}/complete`);
    return res.data;
  },

  deleteTask: async (id: number): Promise<void> => {
    await api.delete(`/tasks/${id}`);
  },

  getTasksByUser: async (userId: number, params?: PaginationParams): Promise<Task[]> => {
    const res = await api.get<Task[]>(`/tasks/user/${userId}`, { params });
    return res.data;
  },

  getTasksByMeeting: async (meetingId: number, params?: PaginationParams): Promise<Task[]> => {
    const res = await api.get<Task[]>(`/tasks/meeting/${meetingId}`, { params });
    return res.data;
  },
};
