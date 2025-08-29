import type { RoleType } from "@shared";

export type User = {
  user_id: string;
  name: string;
  role: RoleType;
  avatarUrl?: string;
};
