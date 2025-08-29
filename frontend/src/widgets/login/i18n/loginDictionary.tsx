import { MIN_PASSWORD_LENGTH } from "@widgets/login/ui/LoginForm";

export const ruLoginDictionary = {
  welcomeBack: "С возвращением!",
  enterCreds: "Введите свои данные для входа.",
  register: "Зарегистрироваться",
  loginForm: {
    email: "Email",
    password: "Пароль",
    emailPlaceholder: "name@example.ru",
    passwordPlaceholder: "Введите свой пароль.",
    signIn: "Войти",
    dontHaveAccount: "Ещё не зарегистрированы?",
    signUp: "Зарегистрироваться",
    forgotPassword: "Забыли пароль?",
    unauthorizedError: "Неверный email или пароль",
    requiredField: "Поле обязательно к заполнению",
    passwordLengthError: `Минимальная длина пароля ${MIN_PASSWORD_LENGTH} символов`,
  },
};
export const enLoginDictionary = {
  welcomeBack: "Welcome back!",
  enterCreds: "Enter your credentials to sign in.",
  register: "Register",
  loginForm: {
    email: "Email",
    password: "Password",
    emailPlaceholder: "name@example.com",
    passwordPlaceholder: "Enter your password",
    signIn: "Sign In",
    dontHaveAccount: "Don't have an account?",
    signUp: "Sign Up",
    forgotPassword: "Forgot your password?",
    unauthorizedError: "Invalid email or password",
    requiredField: "This field is required",
    passwordLengthError: `Minimum password length is ${MIN_PASSWORD_LENGTH} characters`,
  },
};
export const kzLoginDictionary = {
  welcomeBack: "Қайта қош келдіңіз!",
  enterCreds: "Кіру үшін анықтамаларыңызды енгізіңіз.",
  register: "Тіркелу",
  loginForm: {
    email: "Email",
    password: "Құпия сөз",
    emailPlaceholder: "name@example.kz",
    passwordPlaceholder: "Құпия сөзіңізді енгізіңіз",
    signIn: "Кіру",
    dontHaveAccount: "Тіркелмегенсіз бе?",
    signUp: "Тіркелу",
    forgotPassword: "Құпия сөзді ұмыттыңыз ба?",
    unauthorizedError: "Дұрыс емес email немесе құпия сөз",
    requiredField: "Бұл өріс міндетті",
    passwordLengthError: `Құпия сөздің ең аз ұзындығы ${MIN_PASSWORD_LENGTH} таңба`,
  },
};
