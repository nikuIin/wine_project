import { createEvent } from "effector";
import { type User } from "@entities/user";

export const setUser = createEvent<User>();
export const clearUser = createEvent();
