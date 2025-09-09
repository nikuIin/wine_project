import { combineReducers, configureStore } from "@reduxjs/toolkit";
import { userReducer, userUUIDReducer } from "@entities/user/model";
import { notificationReducer } from "@shared/ui/notifications";
import {
  FLUSH,
  PAUSE,
  PERSIST,
  persistReducer,
  PURGE,
  REGISTER,
  REHYDRATE,
} from "redux-persist";
import storage from "redux-persist/lib/storage";
import persistStore from "redux-persist/lib/persistStore";

const rootReducers = combineReducers({
  user: userReducer,
  userLight: userUUIDReducer,
});

const persistConfig = {
  key: "root",
  whitelist: ["user", "userLight"],
  storage,
};

const persistReducers = persistReducer(persistConfig, rootReducers);

export const store = configureStore({
  reducer: { persistReducers, notificationReducer },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: [FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER],
      },
    }),
});

export const persistor = persistStore(store);
