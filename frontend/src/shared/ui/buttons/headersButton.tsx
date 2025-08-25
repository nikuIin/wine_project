import { useNavigate } from "react-router";
import { type ButtonProps } from "@shared/ui/buttons/type";

export const RentangleBorderButton: React.FC<ButtonProps> = ({ children, onClick, mainColor, to }) => {
  const navigate = useNavigate();

  const handleClick = () => {
    if (to) {
      navigate(to); // Navigate to the specified path
    }
    if (onClick) {
      onClick(); // Execute custom click handler if provided
    }
  };
  return (
    <button
      className={`
        ${mainColor === "light" ? "bg-base-light dark:bg-base-dark" : "bg-base-dark dark:bg-base-light"}
        w-9 h-9 rounded-xl
        transition-transform duration-300 cursor-pointer
        hover:scale-110
      `}
      onClick={handleClick}
    >
      {children}
    </button>
  );
};
