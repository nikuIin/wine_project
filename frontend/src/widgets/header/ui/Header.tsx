import { Link } from "react-router-dom";
import { ThemeSwitcher } from "@widgets/theme";

export const Header: React.FC = () => {
  return (
    <header className="fixed top-0 left-0 right-0 z-50 w-full bg-white dark:bg-gray-900 shadow">
      <div className="_container flex items-center justify-between py-4">
        {/* Лого и название */}
        <Link to="/" className="font-bold text-xl text-gray-900 dark:text-gray-100">
          Вина со всего мира
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

        {/* Переключатель темы */}
        <ThemeSwitcher />
      </div>
    </header>
  );
};
