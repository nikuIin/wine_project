import React, { useState, useEffect, useRef } from "react";
import { LoginFeat } from "@features/user";
import { useTranslation } from "react-i18next";
import { Languages, UnauthorizedError } from "@shared/index";
import { DotsLoader } from "@shared/ui/loaders";
import { Message } from "@shared/ui/messages";

import { useDispatch } from "react-redux";
import type { AppDispatch } from "@shared/store";
import { useToast } from "@shared/ui/notifications";
import { ArrowLeftIcon, EyeIcon, EyeOffIcon, UserIcon } from "@shared/ui/icons";
import { CloseButton } from "@shared/ui/buttons/closeButton";
import { PageLinks } from "@shared/pagesLinks";
import { useNavigate } from "react-router";

export const MIN_PASSWORD_LENGTH = 8;

export const Login = ({
  onSignUpClick,
  onClose = undefined,
  onBack = undefined,
}: {
  onSignUpClick: () => void;
  onClose?: () => void;
  onBack?: () => void;
}): React.ReactNode => {
  const [showPassword, setShowPassword] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [shake, setShake] = useState(false);
  const [emailError, setEmailError] = useState(false);
  const [passwordError, setPasswordError] = useState(false);
  const formRef = useRef<HTMLDivElement>(null);

  const navigate = useNavigate();

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
    setIsLoading(false);
    setShake(false);
  };

  const handleClose = () => {
    resetForm();
    if (onClose) {
      onClose();
    }
  };

  useEffect(() => {
    if (error || emailError || passwordError) {
      setShake(true);
      const timer = setTimeout(() => setShake(false), 500);
      return () => clearTimeout(timer);
    }
  }, [error, emailError, passwordError]);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setIsLoading(true);
    setError(null);
    setEmailError(false);
    setPasswordError(false);

    if (!email) {
      setEmailError(true);
    }

    if (!password) {
      setPasswordError(true);
    }

    if (!email || !password) {
      setIsLoading(false);
      return;
    }

    try {
      const user = await LoginFeat(
        email,
        password,
        i18n.language || Languages.DEFAULT,
        dispatch,
      );
      if (user) {
        success(
          t("login.successTitleNotification"),
          t("login.successDescriptionNotification"),
        );
        navigate(PageLinks.MAIN_PAGE);
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
    <>
      <div className="relative w-full min-h-screen flex items-center justify-center font-sans overflow-hidden p-4 b">
        <div
          ref={formRef}
          className={`
            relative w-full max-w-4xl p-6 bg-white
            dark:bg-black rounded-lg border border-zinc-200
            dark:border-zinc-800 shadow-lg dark:shadow-zinc-900/50
            transition-all duration-300 ease-in-out ${
              shake
                ? "animate-[shake_0.5s_cubic-bezier(0.36,0.07,0.19,0.97)_both]"
                : ""
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
            height: auto;
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
          @media (min-width: 1024px) {
            .two-column {
              display: grid;
              grid-template-columns: 1fr 1fr;
              gap: 2rem;
              align-items: start;
            }
            .left-column {
              text-align: left;
            }
            .right-column {
              text-align: left;
            }
          }
          `}
          </style>
          <div className="relative two-column">
            <div className="left-column space-y-6 ">
              <div className="relative flex items-center justify-between w-full">
                {onBack ? (
                  <div
                    className="
                    w-7 h-7 flex
                    items-center justify-center
                    rounded-md
                    cursor-pointer
                    transition-colors focus-visible:outline-none
                    text-zinc-200
                    focus-visible:ring-1 focus-visible:ring-zinc-950
                    dark:focus-visible:ring-zinc-300
                    bg-zinc-900 shadow
                    hover:bg-zinc-900/90 dark:bg-zinc-900 dark:text-white
                    dark:hover:bg-zinc-900/90
                    duration-100
                  "
                    onClick={onBack}
                  >
                    <ArrowLeftIcon />
                  </div>
                ) : (
                  <div className="w-7"></div>
                )}
                <div className="lg:hidden inline-flex p-2 bg-zinc-100 dark:bg-zinc-900 rounded-md border border-zinc-200 dark:border-zinc-800">
                  <UserIcon />
                </div>
                {onClose ? (
                  <div className="absolute top-0 right-0 w-7">
                    <CloseButton onClick={handleClose} color="gray" />
                  </div>
                ) : (
                  <div className="w-7"></div>
                )}
              </div>

              <div className="lg:text-left text-center">
                <div
                  className={`animate-height w-10/12 hidden lg:block ${error ? "error-visible" : "error-enter"}`}
                >
                  {error && <Message message={error} styleType="error" />}
                </div>
                <p
                  className={`text-2xl ${!error && "lg:mt-10"} lg:text-4xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-200`}
                >
                  {t("welcomeBack")}
                </p>
                <p className="text-sm lg:text-base text-zinc-600 dark:text-zinc-200 mt-1 mb-5">
                  {t("enterCreds")}
                </p>
              </div>
            </div>

            <div className="right-column space-y-6">
              <div
                className={`animate-height lg:hidden ${error ? "error-visible" : "error-enter"}`}
              >
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
                  {emailError && (
                    <p className="text-xs text-red-500 mt-1">
                      {t("loginForm.requiredField")}
                    </p>
                  )}
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
                  {passwordError && (
                    <p className="text-xs text-red-500 mt-1">
                      {t("loginForm.requiredField")}
                    </p>
                  )}
                </div>
                <button
                  type="submit"
                  disabled={isLoading}
                  className="
                    inline-flex items-center
                    justify-center whitespace-nowrap
                    rounded-md text-sm font-medium
                    cursor-pointer
                    transition-colors focus-visible:outline-none
                    focus-visible:ring-1 focus-visible:ring-zinc-950
                    dark:focus-visible:ring-zinc-300
                    bg-zinc-900 shadow
                    hover:bg-zinc-900/90 dark:bg-zinc-900 dark:text-white
                    dark:hover:bg-zinc-900/90
                    h-9 px-4 py-2 w-full
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
                    onClick={onSignUpClick}
                    className="font-medium text-zinc-900 dark:text-zinc-50 cursor-pointer underline underline-offset-4 hover:text-zinc-700 dark:hover:text-zinc-300 transition-colors"
                  >
                    {t("loginForm.signUp")}
                  </a>
                </p>
                <a className="text-sm font-medium text-zinc-900 dark:text-zinc-50 cursor-pointer underline underline-offset-4 hover:text-zinc-700 dark:hover:text-zinc-300 transition-colors">
                  {t("loginForm.forgotPassword")}
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};
