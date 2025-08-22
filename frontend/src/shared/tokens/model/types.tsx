import type { UUID } from "@shared/uuid";
import type { Role } from "@shared";

type TokenPayload = {
  token_id: UUID;
  user_id: UUID;
  role_id: Role;
  fingerprint: string;
  exp: number;
};

export type AccessTokenPayload = TokenPayload;

export type RefreshTokenPayload = TokenPayload & {
  login: string;
  ip: string | null;
};
