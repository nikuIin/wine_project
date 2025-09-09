export const Role = {
  USER: 1,
  ADMIN: 2,
  AUTHOR: 3,
  MANAGER: 4,
} as const;

export type Role = typeof Role;
