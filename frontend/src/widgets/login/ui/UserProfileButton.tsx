import React, { useState } from "react";
import { RentangleBorderButton } from "@shared/ui/buttons";
import PersonIcon from "@mui/icons-material/Person";
import { useTheme } from "@shared/index";
import { LoginModal } from "@widgets/login";

export const UserProfileButton: React.FC = () => {
  const { theme } = useTheme();
  const [isSignUpFormOpen, setSignUpFormOpen] = useState<boolean>(false);

  return (
    <>
      <RentangleBorderButton mainColor="dark" onClick={() => setSignUpFormOpen(true)}>
        <PersonIcon
          sx={theme === "light" ? { color: "var(--color-base-light)" } : { color: "var(--color-base-dark)" }}
        />
      </RentangleBorderButton>
      <LoginModal open={isSignUpFormOpen} onClose={() => setSignUpFormOpen(false)} />
    </>
  );
};
