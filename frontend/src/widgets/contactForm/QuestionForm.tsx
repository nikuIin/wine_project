import React, { useState, useEffect, useRef } from "react";
import { useTranslation } from "react-i18next";
import { DotsLoader } from "@shared/ui/loaders";
import { Message } from "@shared/ui/messages";
import { useToast } from "@shared/ui/notifications";
import { ArrowLeftIcon, UserIcon, PhoneIcon } from "@shared/ui/icons";
import { CloseButton } from "@shared/ui/buttons/closeButton";

export const QuestionForm = ({
  onClose = undefined,
  onBack = undefined,
}: {
  onClose?: () => void;
  onBack?: () => void;
}): React.ReactNode => {
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [question, setQuestion] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [shake, setShake] = useState(false);
  const [nameError, setNameError] = useState(false);
  const [phoneError, setPhoneError] = useState(false);
  const [questionError, setQuestionError] = useState(false);
  const formRef = useRef<HTMLDivElement>(null);

  const { t } = useTranslation();
  const { success } = useToast();

  const resetForm = () => {
    setName("");
    setPhone("");
    setQuestion("");
    setError(null);
    setNameError(false);
    setPhoneError(false);
    setQuestionError(false);
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
    if (error || nameError || phoneError || questionError) {
      setShake(true);
      const timer = setTimeout(() => setShake(false), 500);
      return () => clearTimeout(timer);
    }
  }, [error, nameError, phoneError, questionError]);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setIsLoading(true);
    setError(null);
    setNameError(false);
    setPhoneError(false);
    setQuestionError(false);

    if (!name) {
      setNameError(true);
    }
    if (!phone) {
      setPhoneError(true);
    }
    if (!question) {
      setQuestionError(true);
    }

    if (!name || !phone || !question) {
      setIsLoading(false);
      return;
    }

    try {
      // Simulate form submission (replace with actual API call)
      await new Promise((resolve) => setTimeout(resolve, 1000));
      success(
        t("contactForm.successTitleNotification"),
        t("contactForm.successDescriptionNotification"),
      );
      resetForm();
    } catch (err) {
      setError(t("baseErrors.internalError"));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <div className="relative w-full flex items-center justify-center font-sans overflow-hidden p-4">
        <div
          ref={formRef}
          className={`
            relative w-full max-w-[862px] p-6 bg-white
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
            <div className="left-column space-y-6">
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
                  {t("contactForm.title")}
                </p>
                <p className="text-sm lg:text-base text-zinc-600 dark:text-zinc-200 mt-1 mb-5">
                  {t("contactForm.description")}
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
                    htmlFor="name"
                    className={`text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 ${nameError ? "blink" : ""}`}
                  >
                    {t("contactForm.name")}
                  </label>
                  <input
                    type="text"
                    id="name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder={t("contactForm.namePlaceholder")}
                    className={`flex h-9 w-full rounded-md border ${nameError ? "border-red-500" : "border-zinc-200 dark:border-zinc-800"} bg-white dark:bg-zinc-950 px-3 py-5 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-zinc-500 dark:placeholder:text-zinc-400 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-zinc-950 dark:focus-visible:ring-zinc-300 disabled:cursor-not-allowed disabled:opacity-50`}
                  />
                  {nameError && (
                    <p className="text-xs text-red-500 mt-1">
                      {t("contactForm.requiredField")}
                    </p>
                  )}
                </div>
                <div className="space-y-2 transition-all duration-300 ease-in-out">
                  <label
                    htmlFor="phone"
                    className={`text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 ${phoneError ? "blink" : ""}`}
                  >
                    {t("contactForm.phone")}
                  </label>
                  <div className="relative">
                    <input
                      type="tel"
                      id="phone"
                      value={phone}
                      onChange={(e) => setPhone(e.target.value)}
                      placeholder={t("contactForm.phonePlaceholder")}
                      className={`flex h-9 w-full rounded-md border ${phoneError ? "border-red-500" : "border-zinc-200 dark:border-zinc-800"} bg-white dark:bg-zinc-950 px-3 py-5 pr-10 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-zinc-500 dark:placeholder:text-zinc-400 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-zinc-950 dark:focus-visible:ring-zinc-300 disabled:cursor-not-allowed disabled:opacity-50`}
                    />
                    <div className="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-500 dark:text-zinc-400">
                      <PhoneIcon />
                    </div>
                  </div>
                  {phoneError && (
                    <p className="text-xs text-red-500 mt-1">
                      {t("contactForm.requiredField")}
                    </p>
                  )}
                </div>
                <div className="space-y-2 transition-all duration-300 ease-in-out">
                  <label
                    htmlFor="question"
                    className={`text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 ${questionError ? "blink" : ""}`}
                  >
                    {t("contactForm.question")}
                  </label>
                  <textarea
                    id="question"
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    placeholder={t("contactForm.questionPlaceholder")}
                    className={`flex min-h-[100px] w-full rounded-md border ${questionError ? "border-red-500" : "border-zinc-200 dark:border-zinc-800"} bg-white dark:bg-zinc-950 px-3 py-2 text-sm shadow-sm transition-colors placeholder:text-zinc-500 dark:placeholder:text-zinc-400 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-zinc-950 dark:focus-visible:ring-zinc-300 disabled:cursor-not-allowed disabled:opacity-50`}
                  />
                  {questionError && (
                    <p className="text-xs text-red-500 mt-1">
                      {t("contactForm.requiredField")}
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
                    <p className="text-zinc-100">{t("contactForm.submit")}</p>
                  )}
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};
