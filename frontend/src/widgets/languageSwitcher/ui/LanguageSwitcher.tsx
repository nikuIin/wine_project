import { useTheme } from "@shared/index";
import { LanguageIcon } from "@shared/ui/icons";
import { RentangleBorderButton } from "@shared/ui/buttons";
import { LanguageList } from "@widgets/languageSwitcher";
import { useState } from "react";

export const LanguageSwitcher: React.FC = () => {
  const { theme } = useTheme();
  const [openLanguageList, setLanguageListOpen] = useState(false);

  return (
    <div className="flex items-center">
      <RentangleBorderButton
        mainColor="light"
        onClick={() => setLanguageListOpen(true)}
      >
        <LanguageIcon
          className={theme === "light" ? "text-base-dark" : "text-base-light"}
        />
      </RentangleBorderButton>
      <LanguageList
        open={openLanguageList}
        onClose={() => setLanguageListOpen(false)}
      ></LanguageList>
    </div>
  );
};
