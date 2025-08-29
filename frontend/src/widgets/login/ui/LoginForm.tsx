import { CloseButton } from "@shared/ui/buttons/closeButton";
import React, { useState, useEffect, useRef } from "react";
import { LoginFeat } from "@features/user";
import { useTranslation } from "react-i18next";
import { Languages, UnauthorizedError } from "@shared/index";
import { DotsLoader } from "@shared/ui/loaders";
import { Message } from "@shared/ui/messages";

import { useDispatch } from "react-redux";
import type { AppDispatch } from "@shared/store";
import { useToast } from "@shared/ui/notifications";

export const MIN_PASSWORD_LENGTH = 8;

const UserIcon = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className="h-5 w-5 text-zinc-600 dark:text-zinc-400"
  >
    <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2" />
    <circle cx="12" cy="7" r="4" />
  </svg>
);

const EyeIcon = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className="h-4 w-4 text-zinc-500 dark:text-zinc-400"
  >
    <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z" />
    <circle cx="12" cy="12" r="3" />
  </svg>
);

const EyeOffIcon = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className="h-4 w-4 text-zinc-500 dark:text-zinc-400"
  >
    <path d="M9.88 9.88a3 3 0 1 0 4.24 4.24" />
    <path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68" />
    <path d="M6.61 6.61A13.526 13.526 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61" />
    <line x1="2" x2="22" y1="2" y2="22" />
  </svg>
);

export const Login = ({ onClose }: { onClose: () => void }): React.ReactNode => {
  const [showPassword, setShowPassword] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [shake, setShake] = useState(false);
  const [emailError, setEmailError] = useState(false);
  const [passwordError, setPasswordError] = useState(false);
  const [passwordLenError, setPasswordLenError] = useState(false);
  const formRef = useRef<HTMLDivElement>(null);
  const { i18n, t } = useTranslation();
  const { success } = useToast();

  const dispatch = useDispatch<AppDispatch>();

  const resetForm = () => {
    setEmail("");
    setPassword("");
    setError(null);
    setEmailError(false);
    setPasswordError(false);
    setShowPassword(false);
    setPasswordLenError(false);
    setIsLoading(false);
    setShake(false);
  };

  const handleClose = () => {
    resetForm();
    onClose();
  };

  useEffect(() => {
    if (error || emailError || passwordError || passwordLenError) {
      setShake(true);
      const timer = setTimeout(() => setShake(false), 500);
      return () => clearTimeout(timer);
    }
  }, [error, emailError, passwordError, passwordLenError]);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setIsLoading(true);
    setError(null);
    setEmailError(false);
    setPasswordError(false);
    setPasswordLenError(false);

    if (!email) {
      setEmailError(true);
    }

    const passwordLengthConstraint = password.length >= MIN_PASSWORD_LENGTH;
    if (!password) {
      setPasswordError(true);
    } else if (!passwordLengthConstraint) {
      setPasswordLenError(true);
    }

    if (!email || !password || !passwordLengthConstraint) {
      setIsLoading(false);
      return;
    }

    try {
      const user = await LoginFeat(email, password, i18n.language || Languages.DEFAULT, dispatch);
      if (user) {
        success("Вход успешен", "лалалаалал");
        onClose();
      }
    } catch (err) {
      if (err instanceof UnauthorizedError) {
        setError(t("loginForm.unauthorizedError"));
      } else {
        setError(t("baseErrors.internalError"));
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="relative w-full flex items-center justify-center font-sans overflow-hidden">
      <div
        ref={formRef}
        className={`relative w-full max-w-sm p-6 space-y-6 bg-white dark:bg-black rounded-lg border border-zinc-200 dark:border-zinc-800 shadow-lg dark:shadow-zinc-900/50 transition-all duration-300 ease-in-out ${
          shake ? "animate-[shake_0.5s_cubic-bezier(0.36,0.07,0.19,0.97)_both]" : ""
        }`}
      >
        <style>
          {`
            @keyframes shake {
              0%, 100% { transform: translateX(0); }
              10%, 30%, 50%, 70%, 90% { transform: translateX(-2px); }
              20%, 40%, 60%, 80% { transform: translateX(2px); }
            }
            .animate-height {
              transition: height 0.3s ease-in-out, opacity 0.3s ease-in-out, margin 0.3s ease-in-out;
              overflow: hidden;
            }
            .error-enter {
              height: 0;
              opacity: 0;
              margin-bottom: 0;
            }
            .error-visible {
              opacity: 1;
              margin-bottom: 1rem;
            }
            @keyframes blink {
              0%, 100% { opacity: 1; }
              50% { opacity: 0.5; }
            }
            .blink {
              animation: blink 1s infinite;
            }
          `}
        </style>
        <div className="relative text-center space-y-3 transition-all duration-300 ease-in-out">
          <div className="absolute top-0 right-0">
            <CloseButton onClick={handleClose} color="gray" />
          </div>
          <div className="inline-flex p-2 bg-zinc-100 dark:bg-zinc-900 rounded-md border border-zinc-200 dark:border-zinc-800">
            <UserIcon />
          </div>
          <div>
            <p className="text-2xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-200">{t("welcomeBack")}</p>
            <p className="text-sm text-zinc-600 dark:text-zinc-200 mt-1">{t("enterCreds")}</p>
          </div>
        </div>
        <div className={`animate-height ${error ? "error-visible" : "error-enter"}`}>
          {error && <Message message={error} styleType="error" />}
        </div>
        <form
          className="space-y-4 text-zinc-600 dark:text-zinc-50 transition-all duration-300 ease-in-out"
          onSubmit={handleSubmit}
        >
          <div className="space-y-2 transition-all duration-300 ease-in-out">
            <label
              htmlFor="email"
              className={`text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 ${emailError ? "blink" : ""}`}
            >
              {t("loginForm.email")}
            </label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder={t("loginForm.emailPlaceholder")}
              className={`flex h-9 w-full rounded-md border ${emailError ? "border-red-500" : "border-zinc-200 dark:border-zinc-800"} bg-white dark:bg-zinc-950 px-3 py-5 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-zinc-500 dark:placeholder:text-zinc-400 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-zinc-950 dark:focus-visible:ring-zinc-300 disabled:cursor-not-allowed disabled:opacity-50`}
            />
            {emailError && <p className="text-xs text-red-500 mt-1">{t("loginForm.requiredField")}</p>}
          </div>
          <div className="space-y-2 transition-all duration-300 ease-in-out">
            <label
              htmlFor="password"
              className={`text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 ${passwordError ? "blink" : ""}`}
            >
              {t("loginForm.password")}
            </label>
            <div className="relative">
              <input
                type={showPassword ? "text" : "password"}
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder={t("loginForm.passwordPlaceholder")}
                className={`flex h-9 w-full rounded-md border ${passwordError ? "border-red-500" : "border-zinc-200 dark:border-zinc-800"} bg-white dark:bg-zinc-950 px-3 py-5 pr-10 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-zinc-500 dark:placeholder:text-zinc-400 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-zinc-950 dark:focus-visible:ring-zinc-300 disabled:cursor-not-allowed disabled:opacity-50`}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 hover:text-zinc-900 dark:hover:text-zinc-100 transition-colors"
              >
                {showPassword ? <EyeOffIcon /> : <EyeIcon />}
              </button>
            </div>
          </div>
          {passwordError && <p className="text-xs text-red-500 mt-1">{t("loginForm.requiredField")}</p>}
          {passwordLenError && <p className="text-xs text-red-500 mt-1">{t("loginForm.passwordLengthError")}</p>}
          <button
            type="submit"
            disabled={isLoading}
            className="
              inline-flex items-center
              justify-center whitespace-nowrap
              rounded-md text-sm font-medium
              transition-colors focus-visible:outline-none
              focus-visible:ring-1 focus-visible:ring-zinc-950
              dark:focus-visible:ring-zinc-300
              bg-zinc-900 shadow
              hover:bg-zinc-900/90 dark:bg-zinc-900 dark:text-white
              dark:hover:bg-zinc-900/90 h-9 px-4 py-2 w-full
            "
          >
            {isLoading ? (
              <DotsLoader className="text-zinc-100" />
            ) : (
              <p className="text-zinc-100">{t("loginForm.signIn")}</p>
            )}
          </button>
        </form>
        <div className="text-center space-y-2 transition-all duration-300 ease-in-out">
          <p className="text-sm text-zinc-600 dark:text-zinc-400">
            {t("loginForm.dontHaveAccount")}{" "}
            <a
              href="#"
              className="font-medium text-zinc-900 dark:text-zinc-50 underline underline-offset-4 hover:text-zinc-700 dark:hover:text-zinc-300 transition-colors"
            >
              {t("loginForm.signUp")}
            </a>
          </p>
          <a
            href="#"
            className="text-sm font-medium text-zinc-900 dark:text-zinc-50 underline underline-offset-4 hover:text-zinc-700 dark:hover:text-zinc-300 transition-colors"
          >
            {t("loginForm.forgotPassword")}
          </a>
        </div>
      </div>
    </div>
  );
};
