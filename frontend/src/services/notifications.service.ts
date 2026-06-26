import { api } from "./api";

export interface Notification {
  id: number;
  user_id: number;
  title: string;
  message: string;
  type: string;
  task_id: number | null;
  is_read: boolean;
  created_at: string;
}

export const notificationsService = {
  getAll: async (): Promise<Notification[]> => {
    const res = await api.get<Notification[]>("/notifications/");
    return res.data;
  },

  getUnreadCount: async (): Promise<number> => {
    const res = await api.get<{ count: number }>("/notifications/unread-count");
    return res.data.count;
  },

  markRead: async (id: number): Promise<Notification> => {
    const res = await api.patch<Notification>(`/notifications/${id}/read`);
    return res.data;
  },

  markAllRead: async (): Promise<void> => {
    await api.patch("/notifications/mark-all-read");
  },
};
