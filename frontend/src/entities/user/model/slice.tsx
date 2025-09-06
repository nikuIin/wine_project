import type { User } from "@entities/user";
import { type PayloadAction, createSlice } from "@reduxjs/toolkit";
import type { UUID } from "@shared/uuid";

interface UserState {
  user: User | null;
}

interface UserUUIDState {
  userUUID: UUID | null;
}

const initialState: UserState = { user: null };
const initialUserUUIDState: UserUUIDState = { userUUID: null };

const userSlice = createSlice({
  name: "user",
  initialState: initialState,
  reducers: {
    setUser: (state, action: PayloadAction<User>) => {
      state.user = action.payload;
    },
    clearUser: (state) => {
      state.user = null;
    },
  },
});

const userUUIDSlice = createSlice({
  name: "userUUID",
  initialState: initialUserUUIDState,
  reducers: {
    setUserUUID: (state, action: PayloadAction<UUID>) => {
      state.userUUID = action.payload;
    },
  },
});

export const { setUser, clearUser } = userSlice.actions;
export const userReducer = userSlice.reducer;

export const { setUserUUID } = userUUIDSlice.actions;
export const userUUIDReducer = userUUIDSlice.reducer;
