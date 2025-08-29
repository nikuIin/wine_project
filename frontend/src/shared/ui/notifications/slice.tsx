import { createSlice, type PayloadAction } from "@reduxjs/toolkit";
import { type Toast } from "@shared/ui/notifications";

interface NotificationState {
  toasts: Toast[] | null;
}

const notificationInitialSlice: NotificationState = {
  toasts: null,
};

const toastSlice = createSlice({
  name: "notification",
  initialState: notificationInitialSlice,
  reducers: {
    setNotification: (state, action: PayloadAction<Toast>) => {
      state.toasts = state.toasts ? [...state.toasts, action.payload] : [action.payload];
    },
    removeNotification: (state, action: PayloadAction<number>) => {
      state.toasts = state.toasts?.filter((toast) => toast.id !== action.payload) || [];
    },
    clearNotifications: (state) => {
      state.toasts = [];
    },
  },
});

export const { setNotification, removeNotification, clearNotifications } = toastSlice.actions;
export const notificationReducer = toastSlice.reducer;
