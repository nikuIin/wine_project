import { type AppDispatch, type RootState } from "@shared/store";
import {
  Notification,
  removeNotification,
  type Toast,
} from "@shared/ui/notifications";
import { Header } from "@widgets/header";
import { MainIntroductionWidget } from "@widgets/mainIntroductionWidget";
import React from "react";
import { useDispatch, useSelector } from "react-redux";

export const FullScreenPage: React.FC = () => {
  const notificationList = useSelector((state: RootState) => {
    return state.notificationReducer.toasts;
  });
  const dispatch = useDispatch<AppDispatch>();

  return (
    <>
      <Header />
      {/* Toast Container */}
      <div className="fixed bottom-4 right-4 z-50 space-y-2">
        {notificationList
          ? notificationList.map((toast: Toast) => (
              <Notification
                key={toast.id}
                {...toast}
                onClose={() => dispatch(removeNotification(toast.id))}
              />
            ))
          : null}
      </div>
      <div className="header-margin">
        <MainIntroductionWidget />
      </div>
    </>
  );
};
