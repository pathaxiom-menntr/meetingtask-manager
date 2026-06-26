import { api } from "./api";
import type { Meeting, MeetingCreate, MeetingUploadResponse, PaginationParams } from "@/types";

export const meetingsService = {
  getMeetings: async (params?: PaginationParams): Promise<Meeting[]> => {
    const res = await api.get<Meeting[]>("/meetings/", { params });
    return res.data;
  },

  getMeetingById: async (id: number): Promise<Meeting> => {
    const res = await api.get<Meeting>(`/meetings/${id}`);
    return res.data;
  },

  createMeeting: async (data: MeetingCreate): Promise<Meeting> => {
    const res = await api.post<Meeting>("/meetings/", data);
    return res.data;
  },

  uploadTranscript: async (
    title: string,
    file: File,
    onUploadProgress?: (progress: number) => void
  ): Promise<MeetingUploadResponse> => {
    const formData = new FormData();
    formData.append("file", file);

    const res = await api.post<MeetingUploadResponse>(
      `/meetings/upload?title=${encodeURIComponent(title)}`,
      formData,
      {
        headers: { "Content-Type": "multipart/form-data" },
        onUploadProgress: (e) => {
          if (e.total && onUploadProgress) {
            onUploadProgress(Math.round((e.loaded * 100) / e.total));
          }
        },
      }
    );
    return res.data;
  },

  updateMeeting: async (id: number, data: Partial<MeetingCreate>): Promise<Meeting> => {
    const res = await api.put<Meeting>(`/meetings/${id}`, data);
    return res.data;
  },

  deleteMeeting: async (id: number): Promise<void> => {
    await api.delete(`/meetings/${id}`);
  },
};
