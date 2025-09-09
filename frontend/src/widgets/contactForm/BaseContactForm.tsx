import { useTranslation } from "react-i18next";
import { DotsLoader } from "@shared/ui/loaders";
import { Message } from "@shared/ui/messages";
import { createOrder } from "@features/contactForm";
import { useSelector } from "react-redux";
import { useToast } from "@shared/ui/notifications";
import { useEffect, useState, type FormEvent } from "react";
import { ArrowLeftIcon } from "@shared/ui/icons";
import { UserIcon } from "lucide-react";
import { CloseButton } from "@shared/ui/buttons/closeButton";

interface BaseFormProps {
  additionalFields?: React.ReactNode;
  onClose?: () => void;
  onBack?: () => void;
  includeQuestion?: boolean;
}

interface FormSwitcherProps {
  setEmail: (email: string) => void;
  setPhone: (phone: string) => void;
  email: string;
  phone: string;
  emailError: boolean;
  phoneError: boolean;
  phoneFormatError: boolean;
  unsupportedSymbolError: boolean;
  availablePhoneSymbols: string;
  setUnsupportedSymbolError: (value: boolean) => void;
  setPhoneFormatError: (value: boolean) => void;
  setPhoneError: (value: boolean) => void;
}

const FormSwitcher = ({
  setEmail,
  setPhone,
  emailError,
  phoneError,
  email,
  phone,
  phoneFormatError,
  unsupportedSymbolError,
  availablePhoneSymbols,
  setUnsupportedSymbolError,
  setPhoneFormatError,
  setPhoneError,
}: FormSwitcherProps) => {
  const [activeTab, setActiveTab] = useState("email");
  const { t } = useTranslation();

  return (
    <div className="space-y-2 text-left transition-all duration-300 ease-in-out">
      <div className="flex justify-start space-x-2 mb-4">
        <button
          type="button"
          onClick={() => {
            setActiveTab("email");
          }}
          className={`
            px-4 py-2 rounded-md text-sm font-medium transition-all duration-300 ease-in-out cursor-pointer
            ${
              activeTab === "email"
                ? "bg-zinc-900 text-white dark:bg-zinc-800 dark:text-zinc-100 shadow"
                : "bg-white dark:bg-zinc-950 text-zinc-600 dark:text-zinc-400 border border-zinc-200 dark:border-zinc-800"
            }
          `}
        >
          {t("contactForm.email", "Email")}
        </button>
        <button
          type="button"
          onClick={() => {
            setActiveTab("phone");
          }}
          className={`
            px-4 py-2 rounded-md text-sm font-medium transition-all duration-300 ease-in-out cursor-pointer
            ${
              activeTab === "phone"
                ? "bg-zinc-900 text-white dark:bg-zinc-800 dark:text-zinc-100 shadow"
                : "bg-white dark:bg-zinc-950 text-zinc-600 dark:text-zinc-400 border border-zinc-200 dark:border-zinc-800"
            }
          `}
        >
          {t("contactForm.phone", "Phone")}
        </button>
      </div>

      <div className="transition-all duration-300 ease-in-out">
        {activeTab === "email" ? (
          <div className="space-y-2">
            <label
              htmlFor="email"
              className={`text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 ${emailError ? "blink" : ""}`}
            >
              {t("contactForm.email", "Email")}
            </label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder={t(
                "contactForm.emailPlaceholder",
                "Enter your email",
              )}
              className={`flex h-9 w-full rounded-md border ${emailError ? "border-red-500" : "border-zinc-200 dark:border-zinc-800"} bg-white dark:bg-zinc-950 px-3 py-5 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-zinc-500 dark:placeholder:text-zinc-400 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-zinc-950 dark:focus-visible:ring-zinc-300 disabled:cursor-not-allowed disabled:opacity-50`}
            />
            {emailError && (
              <p className="text-xs text-red-500 mt-1">
                {t("contactForm.requiredField", "This field is required")}
              </p>
            )}
          </div>
        ) : (
          <div className="space-y-2">
            <label
              htmlFor="phone"
              className={`text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 ${phoneError || phoneFormatError ? "blink" : ""}`}
            >
              {t("contactForm.phone", "Phone Number")}
            </label>
            <input
              type="tel"
              id="phone"
              value={phone}
              onChange={(e) => {
                const phone = e.target.value;
                if (
                  availablePhoneSymbols.includes(phone.slice(-1)) ||
                  phone === ""
                ) {
                  setPhone(phone);
                  setUnsupportedSymbolError(false);
                } else {
                  setUnsupportedSymbolError(true);
                }
                setPhoneFormatError(false);
                setPhoneError(false);
              }}
              placeholder={t(
                "contactForm.phonePlaceholder",
                "Enter your phone number",
              )}
              className={`flex h-9 w-full rounded-md border ${phoneError || phoneFormatError ? "border-red-500" : "border-zinc-200 dark:border-zinc-800"} bg-white dark:bg-zinc-950 px-3 py-5 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-zinc-500 dark:placeholder:text-zinc-400 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-zinc-950 dark:focus-visible:ring-zinc-300 disabled:cursor-not-allowed disabled:opacity-50`}
            />
            {phoneError && (
              <p className="text-xs text-red-500 mt-1">
                {t("contactForm.requiredField", "This field is required")}
              </p>
            )}
            {phoneFormatError && (
              <p className="text-xs text-red-500 mt-1">
                {t("contactForm.phoneFormatError", "Invalid phone format")}
              </p>
            )}
            {unsupportedSymbolError && (
              <p className="text-xs text-red-500 mt-1">
                {t(
                  "contactForm.unsupportedSymbolError",
                  "Only 0123456789+-() and space are allowed",
                )}
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export const BaseContactForm = ({
  additionalFields,
  onClose,
  onBack,
  includeQuestion = false,
}: BaseFormProps) => {
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [email, setEmail] = useState("");
  const [question, setQuestion] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [shake, setShake] = useState(false);
  const [nameError, setNameError] = useState(false);
  const [phoneError, setPhoneError] = useState(false);
  const [emailError, setEmailError] = useState(false);
  const [phoneFormatError, setPhoneFormatError] = useState(false);
  const [unsupportedSymbolError, setUnsupportedSymbolError] = useState(false);
  const [questionError, setQuestionError] = useState(false);
  const [dealCreated, setDealCreated] = useState(false);
  const { t } = useTranslation();
  const { success: successNotification, error: errorNotification } = useToast();

  const userUUID = useSelector((state: any) => {
    return state.persistReducers.userLight.userUUID;
  });

  const sngPhonesRegex =
    /^(\+7|8|\+380|\+375|\+77[0-9]|\+998|\+374|\+994|\+996|\+992|\+993|\+373)(\s|-)?\(?(\d{2,3})\)?(\s|-)?(\d{2,3})(\s|-)?(\d{2})(\s|-)?(\d{2,3})$|^(\+7|8|\+380|\+375|\+77[0-9]|\+998|\+374|\+994|\+996|\+992|\+993|\+373)(\d{7,10})$/;
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  const availablePhoneSymbols = "+0123456789()- ";

  useEffect(() => {
    if (
      error ||
      nameError ||
      phoneError ||
      emailError ||
      phoneFormatError ||
      unsupportedSymbolError ||
      questionError
    ) {
      setShake(true);
      const timer = setTimeout(() => setShake(false), 500);
      return () => clearTimeout(timer);
    }
  }, [
    error,
    nameError,
    phoneError,
    emailError,
    phoneFormatError,
    unsupportedSymbolError,
    questionError,
  ]);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setIsLoading(true);
    setError(null);
    setNameError(false);
    setPhoneError(false);
    setEmailError(false);
    setPhoneFormatError(false);
    setQuestionError(false);

    if (!name) {
      setNameError(true);
    }
    if (!phone && !email) {
      setPhoneError(true);
      setEmailError(true);
    }
    if (phone && !sngPhonesRegex.test(phone)) {
      setPhoneFormatError(true);
    }
    if (email && !emailRegex.test(email)) {
      setEmailError(true);
    }
    if (includeQuestion && !question) {
      setQuestionError(true);
    }
    if (
      !name ||
      (!phone && !email) ||
      (phone && !sngPhonesRegex.test(phone)) ||
      (email && !emailRegex.test(email)) ||
      (includeQuestion && !question)
    ) {
      setIsLoading(false);
      return;
    }

    try {
      if (userUUID !== null) {
        const order = {
          sale_stage_id: 1,
          lead_id: userUUID,
          phone: phone || null,
          email: email || null,
          name: name,
          question: includeQuestion ? question || null : null,
          cost: 0,
          probability: 0,
          priority: 0,
        };
        await createOrder(order);
        successNotification(
          t("contactForm.successCreateOrderNotificationTitle"),
          t("contactForm.successCreateOrderNotificationBody"),
        );
        setDealCreated(true);
      } else {
        console.error("User id not defined");
        errorNotification(
          t("baseErrors.internalErrorTitle"),
          t("baseErrors.internalError"),
        );
      }
    } catch (err) {
      errorNotification(
        t("baseErrors.internalErrorTitle"),
        t("baseErrors.internalError"),
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="relative w-full flex items-center justify-center font-sans overflow-hidden p-4">
      <div
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
          <div className="left-column space-y-6">
            <div className="relative flex items-center justify-between w-full">
              {onBack && (
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
              )}
              {!onBack && <div className="w-7"></div>}
              <div className="lg:hidden inline-flex p-2 bg-zinc-100 dark:bg-zinc-900 rounded-md border border-zinc-200 dark:border-zinc-800">
                <UserIcon />
              </div>
              {onClose && (
                <div className="absolute top-0 right-0 w-7">
                  <CloseButton onClick={onClose} color="gray" />
                </div>
              )}
              {!onClose && <div className="w-7"></div>}
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
                {t("contactForm.title", "Contact Us")}
              </p>
              <p className="text-sm lg:text-base text-zinc-600 dark:text-zinc-200 mt-1 mb-5">
                {t(
                  "contactForm.description",
                  "Please fill in your details below.",
                )}
              </p>
            </div>
          </div>
          <div className="right-column space-y-6">
            <div
              className={`animate-height lg:hidden ${error ? "error-visible" : "error-enter"}`}
            >
              {error && <Message message={error} styleType="error" />}
              {dealCreated && (
                <Message
                  message={t("contactForm.dealCreatedSuccessfully")}
                  styleType="info"
                />
              )}
            </div>
            <form
              className="space-y-4 text-zinc-600 dark:text-zinc-50 transition-all duration-300 ease-in-out"
              onSubmit={handleSubmit}
            >
              <div className="space-y-2 text-left transition-all duration-300 ease-in-out">
                <label
                  htmlFor="name"
                  className={`text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 ${nameError ? "blink" : ""}`}
                >
                  {t("contactForm.name", "Name")}
                </label>
                <input
                  type="text"
                  id="name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder={t(
                    "contactForm.namePlaceholder",
                    "Enter your name",
                  )}
                  className={`flex h-9 w-full rounded-md border ${nameError ? "border-red-500" : "border-zinc-200 dark:border-zinc-800"} bg-white dark:bg-zinc-950 px-3 py-5 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-zinc-500 dark:placeholder:text-zinc-400 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-zinc-950 dark:focus-visible:ring-zinc-300 disabled:cursor-not-allowed disabled:opacity-50`}
                />
                {nameError && (
                  <p className="text-xs text-red-500 mt-1">
                    {t("contactForm.requiredField", "This field is required")}
                  </p>
                )}
              </div>
              <FormSwitcher
                setEmail={setEmail}
                setPhone={setPhone}
                email={email}
                phone={phone}
                emailError={emailError}
                phoneError={phoneError}
                phoneFormatError={phoneFormatError}
                unsupportedSymbolError={unsupportedSymbolError}
                availablePhoneSymbols={availablePhoneSymbols}
                setUnsupportedSymbolError={setUnsupportedSymbolError}
                setPhoneFormatError={setPhoneFormatError}
                setPhoneError={setPhoneError}
              />
              {includeQuestion && (
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
              )}
              {additionalFields}
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
                  <p className="text-zinc-100">
                    {t("contactForm.submit", "Submit")}
                  </p>
                )}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};
