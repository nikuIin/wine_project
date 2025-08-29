import { RentangleBorderButton } from "@shared/ui/buttons";
import PersonIcon from "@mui/icons-material/Person";
import { useTheme } from "@shared/index";
import { LoginModal } from "@widgets/login";
import { useSelector } from "react-redux";
import type { RootState } from "@shared/store";
import { useNavigate } from "react-router";
import { useState } from "react";
import { PageLinks } from "@shared/pagesLinks";

export const UserProfileButton: React.FC = () => {
  const { theme } = useTheme();
  const [isSignUpFormOpen, setSignUpFormOpen] = useState<boolean>(false);
  const user = useSelector((state: RootState) => {
    return state.persistReducers.user;
  });
  const navigate = useNavigate();

  const handleButtonClick = () => {
    if (user.user) {
      navigate(PageLinks.PROFILE_PAGE);
    } else {
      setSignUpFormOpen(true);
    }
  };

  return (
    <>
      <RentangleBorderButton mainColor="dark" onClick={() => handleButtonClick()}>
        <PersonIcon
          sx={theme === "light" ? { color: "var(--color-base-light)" } : { color: "var(--color-base-dark)" }}
        />
      </RentangleBorderButton>
      <LoginModal open={isSignUpFormOpen} onClose={() => setSignUpFormOpen(false)} />
    </>
  );
};
