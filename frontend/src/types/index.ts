// All application TypeScript types

export interface User {
  id: number;
  full_name: string;
  email: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  full_name: string;
  email: string;
  password: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export type TaskPriority = "low" | "medium" | "high" | "critical";
export type TaskStatus = "pending" | "completed";

export interface Task {
  id: number;
  title: string;
  description: string | null;
  status: TaskStatus;
  priority: TaskPriority;
  assignee_id: number;
  assigned_by: number;
  meeting_id: number | null;
  due_date: string | null;
  created_at: string;
  completed_at: string | null;
}

export interface TaskCreate {
  title: string;
  description?: string;
  assignee_id: number;
  meeting_id?: number;
  priority?: string;
  due_date?: string;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  assignee_id?: number;
  priority?: string;
  due_date?: string;
}

export interface Meeting {
  id: number;
  title: string;
  transcript: string;
  uploaded_by: number;
  created_at: string;
}

export interface MeetingCreate {
  title: string;
  transcript: string;
}

export interface SkippedTask {
  title: string | null;
  assignee_name: string | null;
  reason: string;
}

export interface MeetingUploadResponse {
  meeting: Meeting;
  tasks: Task[];
  skipped: SkippedTask[];
}

export interface DashboardStats {
  total_meetings: number;
  total_tasks: number;
  pending_tasks: number;
  completed_tasks: number;
  completion_rate: number;
}

export interface PaginationParams {
  skip?: number;
  limit?: number;
}
