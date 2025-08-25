import { Link } from "react-router-dom";
import { ThemeSwitcher } from "@widgets/theme";
import { UserProfileButton } from "@widgets/login";
import { LanguageSwitcher } from "@widgets/languageSwitcher";

export const Header: React.FC = () => {
  return (
    <header className="fixed top-0 left-0 right-0 z-50 w-full bg-base-light dark:bg-base-dark shadow">
      <div className="_container flex items-center justify-between py-4">
        {/* Лого и название */}
        <Link to="/" className="font-bold text-xl text-gray-900 dark:text-gray-100">
          Янтарное
        </Link>

        {/* Навигация */}
        <nav className="flex gap-6">
          <Link to="/" className="text-gray-700 dark:text-gray-200 hover:underline transition">
            Главная
          </Link>
          <Link to="/about" className="text-gray-700 dark:text-gray-200 hover:underline transition">
            О проекте
          </Link>
        </nav>

        <div className="flex gap-6">
          <UserProfileButton />
          <ThemeSwitcher />
          <LanguageSwitcher />
        </div>
      </div>
    </header>
  );
};
