import { useState } from "react";
import { type NotificationType } from "./toast";
import { useDispatch } from "react-redux";
import { type AppDispatch } from "@shared/store";
import { setNotification } from "@shared/ui/notifications";

export type Toast = {
  id: number;
  type: NotificationType;
  title: string;
  message?: string;
  showIcon: boolean;
  duration?: number;
};

export function useToast() {
  const [notifications, setNotifications] = useState<Toast[]>([]);
  const dispatch = useDispatch<AppDispatch>();

  const addToast = (type: NotificationType, title: string, message?: string, duration?: number) => {
    const id = Math.floor(Math.random() * Number.MAX_SAFE_INTEGER);
    const newToast = {
      id,
      type,
      title,
      message,
      showIcon: true,
      duration,
    };

    dispatch(setNotification(newToast));
    // setNotifications((prev) => [...prev, newToast]);
  };

  const removeToast = (id: number) => {
    setNotifications((prev) => prev.filter((toast) => toast.id !== id));
  };

  const success = (title: string, message?: string, duration = 3000) => addToast("success", title, message, duration);

  const error = (title: string, message?: string, duration = 5000) => addToast("error", title, message, duration);

  const warning = (title: string, message?: string, duration = 4000) => addToast("warning", title, message, duration);

  const info = (title: string, message?: string, duration = 4000) => addToast("info", title, message, duration);

  const loading = (title: string, message?: string) => addToast("loading", title, message);

  return {
    notifications,
    success,
    error,
    warning,
    info,
    loading,
    removeToast,
  };
}
