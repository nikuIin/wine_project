import { UnauthorizedError } from "@shared/index";
import type { AppDispatch } from "@shared/store";
import {
  ArrowLeftIcon,
  ArrowRightIcon,
  CheckIcon,
  EyeIcon,
  EyeOffIcon,
  LockIcon,
  MailIcon,
  UserIcon,
} from "@shared/ui/icons";
import { CloseButton } from "@shared/ui/buttons/closeButton";
import { Message } from "@shared/ui/messages";
import { useState, useEffect, useRef } from "react";
import { useDispatch } from "react-redux";
import { useTranslation } from "react-i18next";
import { useToast } from "@shared/ui/notifications";
import { IsEmailBusy, IsLoginBusy, Register } from "@features/user";
import { PageLinks } from "@shared/pagesLinks";
import { useNavigate } from "react-router";

export const RegisterForm = ({
  onSignInClick,
  onClose = undefined,
  onBack = undefined,
}: {
  onSignInClick: () => void;
  onClose?: () => void;
  onBack?: () => void;
}) => {
  const [showPassword, setShowPassword] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [login, setLogin] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [step, setStep] = useState(1);
  const [error, setError] = useState<string | null>(null);
  const [loginError, setLoginError] = useState(false);
  const [emailError, setEmailError] = useState(false);
  const [passwordError, setPasswordError] = useState(false);
  const [passwordLenError, setPasswordLenError] = useState(false);
  const [unsupportedSymbolsError, setUnsupportedSymbolsError] = useState(false);
  const [shake, setShake] = useState(false);
  const [loginBusy, setLoginBusy] = useState<boolean>();
  const [emailBusy, setEmailBusy] = useState<boolean>();
  const formRef = useRef<HTMLDivElement>(null);
  const { t } = useTranslation();
  const { success } = useToast();
  const dispatch = useDispatch<AppDispatch>();
  const submitConstraint = !loginBusy && login && email && password;
  const navigate = useNavigate();

  const resetForm = () => {
    setEmail("");
    setPassword("");
    setLogin("");
    setError(null);
    setLoginError(false);
    setEmailError(false);
    setPasswordError(false);
    setPasswordLenError(false);
    setShowPassword(false);
    setIsLoading(false);
    setShake(false);
    setStep(1);
    setLoginBusy(undefined);
    setEmailBusy(undefined);
  };

  const handleClose = () => {
    resetForm();
    if (onClose) onClose();
  };

  const handleKeyDown = async (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (step < 4) {
        await handleNext();
      } else {
        await handleSubmit(e);
      }
    }
  };

  const handleNext = async () => {
    setError(null);
    setLoginError(false);
    setEmailError(false);
    setPasswordError(false);
    setPasswordLenError(false);

    if (step === 1) {
      if (!login) {
        setLoginError(true);
        return;
      }

      if (await handleLoginCheck(login)) {
        setLoginError(true);
        return;
      }
    }
    if (step === 2) {
      if (!email) {
        setEmailError(true);
        return;
      } else {
        console.log(await handleEmailCheck(email));
        if (await handleEmailCheck(email)) {
          setEmailError(true);
          return;
        }
      }
      if (!password) {
        setPasswordError(true);
        return;
      }
    }
    if (step < 3) {
      setStep(step + 1);
    }
  };

  const handleLoginCheck = async (login: string) => {
    try {
      setIsLoading(true);
      const isBusy = await IsLoginBusy(login);
      setLoginBusy(isBusy);
      if (isBusy) {
        setLoginError(true);
      }
      setIsLoading(false);
      return isBusy;
    } catch (error) {
      console.error(error);
      setError(t("baseErrors.internalError"));
      setIsLoading(false);
    }
  };

  const handleEmailCheck = async (email: string) => {
    try {
      setIsLoading(true);
      const isBusy = await IsEmailBusy(email);
      setEmailBusy(isBusy);
      setIsLoading(false);
      return isBusy;
    } catch (error) {
      console.error(error);
      setError(t("baseErrors.internalError"));
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    if (!submitConstraint) {
      return;
    }

    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      await Register(login, password, email, dispatch);
      success(t("registerForm.success"), t("registerForm.successMessage"));
      navigate(PageLinks.MAIN_PAGE);
    } catch (err) {
      if (err instanceof UnauthorizedError) {
        setError(t("registerForm.unauthorizedError"));
      } else {
        setError(t("baseErrors.internalError"));
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (
      error ||
      loginError ||
      emailError ||
      passwordError ||
      passwordLenError ||
      unsupportedSymbolsError
    ) {
      setShake(true);
      const timer = setTimeout(() => setShake(false), 500);
      return () => clearTimeout(timer);
    }
  }, [
    error,
    loginError,
    emailError,
    passwordError,
    passwordLenError,
    unsupportedSymbolsError,
  ]);

  return (
    <>
      <div className="relative w-full h-screen min-h-screen flex-col flex items-center justify-center font-sans overflow-hidden p-4">
        <div className="mb-3 w-full max-w-4xl p-1">
          <div className="flex justify-between items-center mb-3">
            <span className="text-sm font-medium text-zinc-900 dark:text-zinc-200">
              {t("registerForm.step", { step, total: 3 })}
            </span>
            <span className="text-sm text-zinc-600 dark:text-zinc-400">
              {Math.round((step / 3) * 100)}%
            </span>
          </div>
          <div className="w-full bg-zinc-200 dark:bg-zinc-800 rounded-full h-2 overflow-hidden">
            <div
              className="signin-progress bg-zinc-900 dark:bg-zinc-100 h-2 rounded-full transition-all duration-500 ease-out"
              style={{
                width: `${(step / 3) * 100}%`,
              }}
            />
          </div>
        </div>{" "}
        <div
          ref={formRef}
          className={`
            relative w-full max-w-4xl p-6 bg-white
            lg:h-96
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
          .signin-progress {
            transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
          }
          @keyframes slideIn {
            from { opacity: 0; transform: translateX(20px); }
            to { opacity: 1; transform: translateX(0); }
          }
          .signin-step {
            animation: slideIn 0.3s ease-out;
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
          <div className="relative two-column h-full">
            <div className="left-column space-y-6">
              <div className="relative flex items-center justify-between w-full">
                {onBack ? (
                  <div
                    className="
                    flex p-2 gap-3
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
                    <p className="hidden lg:block font-bold">
                      {t("registerForm.backToLogin")}
                    </p>
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
                  className={`text-xl ${!error && "mt-10"} lg:text-4xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-200`}
                >
                  {t("registerForm.createAccount")}
                </p>
                <p className="text-sm lg:text-base text-zinc-600 dark:text-zinc-200 mt-1 mb-5">
                  {step === 1 && t("registerForm.step1Description")}
                  {step === 2 && t("registerForm.step2Description")}
                  {step === 3 && t("registerForm.step3Description")}
                </p>
              </div>
            </div>
            <div className="right-column space-y-6 lg:h-full lg:items-left lg:justify-center lg:flex lg:flex-col">
              <div
                className={`animate-height lg:hidden ${error ? "error-visible" : "error-enter"}`}
              >
                {error && <Message message={error} styleType="error" />}
              </div>
              <form
                onSubmit={handleSubmit}
                onKeyDown={handleKeyDown}
                className="space-y-4 text-zinc-600 dark:text-zinc-50 transition-all duration-300 ease-in-out"
              >
                {step === 1 && (
                  <div className="signin-step space-y-4">
                    <div className="space-y-2 relative">
                      <label
                        htmlFor="fullName"
                        className={`text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 ${loginError ? "blink" : ""}`}
                      >
                        {t("registerForm.fullName")}
                      </label>
                      <div className="relative">
                        <input
                          id="fullName"
                          type="text"
                          value={login}
                          onChange={(e) => {
                            const value = e.target.value;
                            if (!/^[a-zA-Z0-9_]*$/.test(value)) {
                              setUnsupportedSymbolsError(true);
                            } else {
                              setUnsupportedSymbolsError(false);
                              setLoginError(false);
                              setLoginBusy(false);
                              setLogin(value);
                            }
                          }}
                          placeholder={t("registerForm.fullNamePlaceholder")}
                          className={`flex h-9 w-full rounded-md border ${
                            loginError && login
                              ? "border-red-500"
                              : login && !loginError
                                ? "border-white"
                                : "border-zinc-200 dark:border-zinc-800"
                          } bg-white dark:bg-zinc-950 px-3 py-5 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-zinc-500 dark:placeholder:text-zinc-400 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-zinc-950 dark:focus-visible:ring-zinc-300 disabled:cursor-not-allowed disabled:opacity-50`}
                        />
                      </div>
                      {loginError && (
                        <p className="text-xs text-red-500 mt-1">
                          {loginBusy
                            ? t("registerForm.loginBusyError")
                            : t("registerForm.requiredField")}
                        </p>
                      )}
                      {unsupportedSymbolsError && (
                        <p className="text-xs text-red-500 mt-1">
                          {t("registerForm.unsoportedSymbolsError")}
                        </p>
                      )}
                    </div>
                    <button
                      type="button"
                      onClick={handleNext}
                      disabled={isLoading || !login || loginBusy}
                      className="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-zinc-950 dark:focus-visible:ring-zinc-300 bg-zinc-900 shadow hover:bg-zinc-900/90 dark:bg-zinc-900 dark:text-white dark:hover:bg-zinc-900/90 h-9 px-4 py-2 w-full disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                    >
                      {isLoading ? (
                        <div className="flex items-center justify-center gap-2">
                          <div className="animate-spin rounded-full h-4 w-4 border-2 border-white dark:border-zinc-900 border-t-transparent"></div>
                          {t("registerForm.checkingLogin")}
                        </div>
                      ) : (
                        <>
                          {t("registerForm.nextStep")}
                          <ArrowRightIcon />
                        </>
                      )}
                    </button>
                  </div>
                )}
                {step === 2 && (
                  <div className="signin-step space-y-4">
                    <div className="space-y-2">
                      <label
                        htmlFor="email"
                        className={`text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 ${emailError ? "blink" : ""}`}
                      >
                        {t("registerForm.email")}
                      </label>
                      <div className="relative">
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-zinc-400 dark:text-zinc-500">
                          <MailIcon />
                        </div>
                        <input
                          id="email"
                          type="email"
                          value={email}
                          onChange={(e) => setEmail(e.target.value)}
                          placeholder={t("registerForm.emailPlaceholder")}
                          className={`flex h-9 w-full rounded-md border ${emailError ? "border-red-500" : "border-zinc-200 dark:border-zinc-800"} bg-white dark:bg-zinc-950 px-3 py-5 pl-9 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-zinc-500 dark:placeholder:text-zinc-400 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-zinc-950 dark:focus-visible:ring-zinc-300 disabled:cursor-not-allowed disabled:opacity-50`}
                        />
                      </div>
                      {emailError && !emailBusy ? (
                        <p className="text-xs text-red-500 mt-1">
                          {t("registerForm.requiredField")}
                        </p>
                      ) : (
                        emailError &&
                        emailBusy && (
                          <p className="text-xs text-red-500 mt-1">
                            {t("registerForm.emailBusyError")}
                          </p>
                        )
                      )}
                    </div>
                    <div className="space-y-2">
                      <label
                        htmlFor="password"
                        className={`text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 ${passwordError || passwordLenError ? "blink" : ""}`}
                      >
                        {t("registerForm.password")}
                      </label>
                      <div className="relative">
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-zinc-400 dark:text-zinc-500">
                          <LockIcon />
                        </div>
                        <input
                          id="password"
                          type={showPassword ? "text" : "password"}
                          value={password}
                          onChange={(e) => setPassword(e.target.value)}
                          placeholder={t("registerForm.passwordPlaceholder")}
                          className={`flex h-9 w-full rounded-md border ${passwordError || passwordLenError ? "border-red-500" : "border-zinc-200 dark:border-zinc-800"} bg-white dark:bg-zinc-950 px-3 py-5 pl-9 pr-10 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-zinc-500 dark:placeholder:text-zinc-400 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-zinc-950 dark:focus-visible:ring-zinc-300 disabled:cursor-not-allowed disabled:opacity-50`}
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
                          {t("registerForm.requiredField")}
                        </p>
                      )}
                      {passwordLenError && (
                        <p className="text-xs text-red-500 mt-1">
                          {t("registerForm.passwordLengthError")}
                        </p>
                      )}
                    </div>
                    <button
                      type="button"
                      onClick={handleNext}
                      disabled={!email || !password}
                      className="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-zinc-950 dark:focus-visible:ring-zinc-300 bg-zinc-900 shadow hover:bg-zinc-900/90 dark:bg-zinc-900 dark:text-white dark:hover:bg-zinc-900/90 h-9 px-4 py-2 w-full disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                    >
                      {t("registerForm.nextStep")}
                      <ArrowRightIcon />
                    </button>
                  </div>
                )}
                {step === 3 && (
                  <div className="signin-step space-y-4">
                    <div className="bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 p-4 rounded-md">
                      <h3 className="font-medium text-zinc-900 dark:text-zinc-100 mb-3 flex items-center gap-2">
                        <CheckIcon />
                        {t("registerForm.reviewDetails")}
                      </h3>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between items-center py-1">
                          <span className="text-zinc-600 dark:text-zinc-400">
                            {t("registerForm.fullName")}
                          </span>
                          <span className="text-zinc-900 dark:text-zinc-100 font-medium">
                            {login}
                          </span>
                        </div>
                        <div className="flex justify-between items-center py-1">
                          <span className="text-zinc-600 dark:text-zinc-400">
                            {t("registerForm.email")}
                          </span>
                          <span className="text-zinc-900 dark:text-zinc-100 font-medium">
                            {email}
                          </span>
                        </div>
                        <div className="flex justify-between items-center py-1">
                          <span className="text-zinc-600 dark:text-zinc-400">
                            {t("registerForm.password")}
                          </span>
                          <span className="text-zinc-900 dark:text-zinc-100 font-medium">
                            ••••••••
                          </span>
                        </div>
                      </div>
                    </div>
                    <button
                      type="submit"
                      disabled={isLoading}
                      className="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-zinc-950 dark:focus-visible:ring-zinc-300 bg-zinc-900 shadow hover:bg-zinc-900/90 dark:bg-zinc-900 dark:text-white dark:hover:bg-zinc-900/90 h-9 px-4 py-2 w-full disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {isLoading ? (
                        <div className="flex items-center justify-center gap-2">
                          <div className="animate-spin rounded-full h-4 w-4 border-2 border-white dark:border-zinc-900 border-t-transparent"></div>
                          {t("registerForm.creatingAccount")}
                        </div>
                      ) : (
                        t("registerForm.createAccount")
                      )}
                    </button>
                  </div>
                )}
                {step > 1 && (
                  <button
                    type="button"
                    onClick={() => setStep(step - 1)}
                    className="mt-4 w-full text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-100 transition-colors text-sm font-medium flex items-center justify-center gap-2"
                  >
                    <ArrowLeftIcon />
                    {t("registerForm.back")}
                  </button>
                )}
              </form>
              <div className="text-center space-y-1 transition-all duration-300 ease-in-out">
                <p className="text-sm text-zinc-600 dark:text-zinc-400 flex flex-col">
                  {t("registerForm.alreadyHaveAccount")}{" "}
                  <a
                    onClick={onSignInClick}
                    className="font-medium text-zinc-900 dark:text-zinc-50 cursor-pointer underline underline-offset-4 hover:text-zinc-700 dark:hover:text-zinc-300 transition-colors"
                  >
                    {t("registerForm.signIn")}
                  </a>
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default RegisterForm;
