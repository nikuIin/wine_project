import { createStore } from "effector/effector.umd";
import type { User } from "@entities/user";
import { clearUser, setUser } from "@entities/user";

export const $currentUser = createStore<User | null>(null)
  .on(setUser, (_, user) => user)
  .on(clearUser, () => null);

export const $isAuth = $currentUser.map(Boolean);
