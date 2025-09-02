import { useTheme } from "@shared";
import { AuroraText } from "@shared/ui/animations";
import { RippleGrid } from "@shared/ui/backgrounds";
import { BaseButton } from "@shared/ui/buttons";
import { useTranslation } from "react-i18next";

export const MainIntroductionWidget: React.FC = () => {
  const { t } = useTranslation();
  const { theme } = useTheme();

  return (
    <>
      <style>
        {`
            @keyframes aurora {
              0%   { background-position: 0% 50%; }
              50%  { background-position: 100% 50%; }
              100% { background-position: 0% 50%; }
            }
            /* The animation duration is now set via inline styles, so we don't need the --duration variable here. */
            .animate-aurora {
              animation-name: aurora;
              animation-timing-function: ease-in-out;
              animation-iteration-count: infinite;
            }
            @media (prefers-reduced-motion: reduce) {
              .animate-aurora { animation: none; }
            }
          `}
      </style>
      <div className="relative w-full h-[90vh] min-h-[500px] overflow-hidden">
        <RippleGrid
          enableRainbow={false}
          gridColor={theme === "dark" ? "#3f3f46" : "#ffffff"}
          rippleIntensity={0.05}
          gridSize={10}
          gridThickness={15}
          mouseInteraction={true}
          mouseInteractionRadius={1.2}
          opacity={theme === "dark" ? 0.8 : 0.35}
        />
        <div className="absolute inset-0 flex flex-col items-center justify-center text-center z-10">
          <h2 className="lg:text-6xl md:text-5xl text-3xl font-bold text-black dark:text-white mb-4">
            {t("mainIntroduction.firstSloganPart")}{" "}
            <AuroraText
              colors={["#da0c81", "#e83d6f", "#f06a9b", "#ff9ac1", "#9353d3"]}
            >
              {t("mainIntroduction.focusSloganPart")}
            </AuroraText>{" "}
            {t("mainIntroduction.lastSloganPart")}
          </h2>
          <p className="text-lg md:text-xl text-gray-700 dark:text-gray-200 max-w-4xl mb-8">
            {t("mainIntroduction.description")}
          </p>
          <div className="relative flex flex-col sm:flex-row sm:space-x-4 space-y-4 sm:space-y-0">
            <BaseButton variant="aurora">
              {t("mainIntroduction.buttons.getStarted")}
            </BaseButton>
            <BaseButton variant="auroraOutline">
              {t("mainIntroduction.buttons.learnMore")}
            </BaseButton>
          </div>
        </div>
      </div>
    </>
  );
};
