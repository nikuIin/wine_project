import { PageLinks } from "@shared/pagesLinks";
import { Login } from "@widgets/login";
import { useNavigate } from "react-router";

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <>
      <div className="flex items-center justify-center h-screen">
        <Login
          onSignUpClick={() => {
            navigate(PageLinks.REGISTER);
          }}
          onBack={() => {
            navigate(PageLinks.MAIN_PAGE);
          }}
        />
      </div>
    </>
  );
};
