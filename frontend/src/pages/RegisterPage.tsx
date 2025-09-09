import { PageLinks } from "@shared/pagesLinks";
import { RegisterForm } from "@widgets/login";
import { useNavigate } from "react-router";

export const RegisterPage: React.FC = () => {
  const navigate = useNavigate();

  const navigateToSignIn = () => {
    navigate(PageLinks.LOGIN_PAGE);
  };

  return (
    <>
      <RegisterForm
        onSignInClick={navigateToSignIn}
        onBack={navigateToSignIn}
      />
    </>
  );
};
