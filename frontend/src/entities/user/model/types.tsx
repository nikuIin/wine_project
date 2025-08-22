import type { Role } from "@shared";

export type User = {
  user_id: string;
  name: string;
  role: Role;
  avatarUrl?: string;
};
