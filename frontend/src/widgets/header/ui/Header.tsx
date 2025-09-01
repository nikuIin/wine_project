import { Link } from "react-router-dom";
import { ThemeSwitcher } from "@widgets/theme";
import { UserProfileButton } from "@widgets/login";
import { LanguageSwitcher } from "@widgets/languageSwitcher";
import { useTranslation } from "react-i18next";
import { PageLinks } from "@shared/pagesLinks";

export const Header: React.FC = () => {
  const { t } = useTranslation();

  return (
    <header className="fixed top-0 left-0 right-0 z-50 w-full bg-base-light dark:bg-base-dark shadow">
      <div className="_container flex items-center justify-between py-4">
        {/* Лого и название */}
        <Link
          to="/"
          className="font-bold text-xl text-gray-900 dark:text-gray-100"
        >
          {t("header.title")}
        </Link>

        {/* Навигация */}
        <nav className="flex gap-6">
          <Link
            to="/"
            className="text-gray-700 dark:text-gray-200 hover:underline transition"
          >
            {t("header.mainPage")}
          </Link>
          <Link
            to="/about"
            className="text-gray-700 dark:text-gray-200 hover:underline transition"
          >
            {t("header.aboutProject")}
          </Link>
        </nav>

        <div className="flex gap-6">
          <UserProfileButton
            pathIsLogin={PageLinks.PROFILE_PAGE}
            pathIsNotLogin={PageLinks.LOGIN_PAGE}
            signUpPath={PageLinks.REGISTER}
          />
          <ThemeSwitcher />
          <LanguageSwitcher />
        </div>
      </div>
    </header>
  );
};
