import { RentangleBorderButton } from "@shared/ui/buttons";
import PersonIcon from "@mui/icons-material/Person";
import { useTheme } from "@shared/index";
import { useSelector } from "react-redux";
import type { RootState } from "@shared/store";
import { useNavigate } from "react-router";
import type { PageLink } from "@shared/pagesLinks";

export const UserProfileButton: React.FC<{
  pathIsNotLogin: PageLink;
  pathIsLogin: PageLink;
  signUpPath: PageLink;
}> = ({ pathIsNotLogin, pathIsLogin }) => {
  const { theme } = useTheme();
  const user = useSelector((state: RootState) => {
    return state.persistReducers.user;
  });
  const navigate = useNavigate();

  const handleButtonClick = () => {
    if (user.user) {
      navigate(pathIsLogin);
    } else {
      navigate(pathIsNotLogin);
    }
  };

  return (
    <>
      <RentangleBorderButton
        mainColor="dark"
        onClick={() => handleButtonClick()}
      >
        <PersonIcon
          sx={
            theme === "light"
              ? { color: "var(--color-base-light)" }
              : { color: "var(--color-base-dark)" }
          }
        />
      </RentangleBorderButton>
    </>
  );
};
