import { MinimalThemeSwithcer } from "@widgets/theme";
import { CloseIcon, LogoIcon, MenuIcon } from "@shared/ui/icons";
import { LanguageSwitcher } from "@widgets/languageSwitcher";
import { useTranslation } from "react-i18next";
import { PageLinks } from "@shared/pagesLinks";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import { BaseButton } from "@shared/ui/buttons";
import { useDispatch, useSelector } from "react-redux";
import { type AppDispatch, type RootState } from "@shared/store";
import { LightRegistration } from "@features/user";

interface NavLinkProps {
  href: string;
  children: React.ReactNode;
  isActive?: boolean;
}

const NavLink: React.FC<NavLinkProps> = ({
  href,
  children,
  isActive = false,
}) => (
  <a
    href={href}
    className={`px-3 py-2 rounded-md text-sm font-medium transition-colors duration-300 ${
      isActive
        ? "text-main"
        : "text-gray-600 dark:text-gray-300 hover:text-main"
    }`}
  >
    {children}
  </a>
);

interface MobileMenuProps {
  isOpen: boolean;
  navItems: NavLinkProps[];
}

const MobileMenu: React.FC<MobileMenuProps> = ({ isOpen, navItems }) => {
  const { t } = useTranslation();

  return (
    <>
      <div
        className={`
      md:hidden absolute top-full left-0 w-full bg-white/95 dark:bg-black/95 backdrop-blur-sm border-t border-gray-200 dark:border-gray-700 shadow-lg
      transition-all duration-300 ease-in-out
      ${isOpen ? "opacity-100 translate-y-0" : "opacity-0 -translate-y-4 pointer-events-none"}
  `}
      >
        <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3 flex flex-col">
          {navItems.map((item, index) => (
            <NavLink key={index} href={item.href} isActive={item.isActive}>
              {item.children}
            </NavLink>
          ))}
        </div>
        <div className="pt-4 pb-4 border-t border-gray-200 dark:border-gray-700">
          <div className="px-5">
            <BaseButton variant="outline" className="w-full">
              {t("header.contactUs")}
            </BaseButton>
          </div>
        </div>
      </div>
      <div className="md:hidden fixed bottom-4 right-5 transform bg-base-light dark:bg-base-dark rounded-full p-2 shadow-lg flex flex-col gap-2">
        <LanguageSwitcher />
        <MinimalThemeSwithcer />
      </div>
    </>
  );
};

type ActiveLink = "Blog" | "Login";

export const Header: React.FC<{ activeLink?: ActiveLink }> = ({
  activeLink = undefined,
}) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const { t } = useTranslation();
  const navigate = useNavigate();

  const userLight = useSelector((state: RootState) => {
    return state.persistReducers.userLight;
  });
  const dispatch = useDispatch<AppDispatch>();

  const handleUserRegister = async () => {
    try {
      await LightRegistration(dispatch);
    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => {
    const registerUser = async () => {
      await handleUserRegister();
    };
    if (!userLight.userUUID) {
      registerUser();
    } else {
      console.log(userLight.userUUID);
    }
  }, []);

  const navItems: NavLinkProps[] = [
    {
      href: PageLinks.LOGIN_PAGE,
      children: t("header.signInPlaceholder"),
      isActive: activeLink === "Login",
    },
    {
      href: PageLinks.BLOG_PAGE,
      children: t("header.blogPlaceholder"),
      isActive: activeLink === "Blog",
    },
  ];

  return (
    <header className="fixed top-0 left-0 right-0 z-50">
      <div className="max-w-9xl mx-auto _container">
        <div className="flex items-center justify-between h-20">
          {/* Logo */}
          <div className="flex-shrink-0 w-[280px] flex items-center gap-2">
            <div className="bg-base-light dark:bg-base-dark flex rounded items-center py-1 px-2">
              <LogoIcon />
              <h1
                onClick={() => {
                  navigate(PageLinks.MAIN_PAGE);
                }}
                className="text-xl font-bold text-gray-900 dark:text-white cursor-pointer"
              >
                {t("header.organizationName")}
              </h1>
            </div>
          </div>

          {/* Nav */}
          <div className="w-[300px] flex items-center justify-center">
            <nav className="hidden md:flex w-1/2 justify-center items-center bg-gray-100/50 dark:bg-gray-800/50 p-1 space-x-1 rounded-full">
              {navItems.map((item, index) => (
                <NavLink key={index} href={item.href} isActive={item.isActive}>
                  {item.children}
                </NavLink>
              ))}
            </nav>
          </div>

          {/* Right buttons */}
          <div className="hidden md:flex gap-5 items-center justify-between">
            <BaseButton variant="outline">{t("header.contactUs")}</BaseButton>
            <LanguageSwitcher />
            <MinimalThemeSwithcer />
          </div>

          <div className="md:hidden">
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="inline-flex items-center justify-center p-2 rounded-md text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-main"
              aria-expanded={isMenuOpen}
              aria-controls="mobile-menu"
            >
              <span className="sr-only">Open main menu</span>
              {isMenuOpen ? <CloseIcon /> : <MenuIcon />}
            </button>
          </div>
        </div>
      </div>
      <MobileMenu isOpen={isMenuOpen} navItems={navItems} />
    </header>
  );
};
