import type { User } from "@entities/user";
import { type PayloadAction, createSlice } from "@reduxjs/toolkit";

interface UserState {
  user: User | null;
}

const initialState: UserState = { user: null };

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

export const { setUser, clearUser } = userSlice.actions;
export const userReducer = userSlice.reducer;
