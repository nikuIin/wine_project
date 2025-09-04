import { CircularGallery } from "@shared/ui/carousels";
import { H2 } from "@shared/ui/texts/baseTitles";
import { useTranslation } from "react-i18next";

export const ConfidenceIndicator: React.FC = () => {
  const { t } = useTranslation();

  return (
    <>
      <div className="container mx-auto px-4 py-8">
        <H2 className="text-center">{t("confidenceIndicator.title")}</H2>
      </div>
      <div className="h-80 w-full rounded-2xl">
        <div className="h-full w-full overflow-hidden rounded-xl transition-transform duration-500 hover:scale-[1.01]">
          <CircularGallery
            bend={3}
            textColor="#ffffff"
            borderRadius={0.05}
            scrollEase={0.02}
          />
        </div>
      </div>
    </>
  );
};
