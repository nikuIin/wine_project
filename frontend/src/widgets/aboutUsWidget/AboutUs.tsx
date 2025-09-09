import { useTheme } from "@shared/index";
import { PageLinks } from "@shared/pagesLinks";
import { TiltedCard } from "@shared/ui/cards";
import { CircularGallery } from "@shared/ui/carousels";
import { H2, P, TextPressure } from "@shared/ui/texts";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router";

interface CircularGalaryItem {
  image: string;
  text: string;
}
const circularGalaryItems: CircularGalaryItem[] = [
  {
    image: "/src/assets/circularGalary/card1.jpeg",
    text: "Изысканное белое вино",
  },
  {
    image: "/src/assets/circularGalary/card2.jpeg",
    text: "Насыщенное красное вино",
  },
  {
    image: "/src/assets/circularGalary/card3.jpeg",
    text: "Незабываемый вкус",
  },
  {
    image: "/src/assets/circularGalary/card4.jpeg",
    text: "Стиль",
  },
  {
    image: "/src/assets/circularGalary/card5.jpeg",
    text: "Гармония вкуса",
  },
  {
    image: "/src/assets/circularGalary/card6.jpeg",
    text: "Эстетичность",
  },
  {
    image: "/src/assets/circularGalary/card7.jpeg",
    text: "Прагматичность",
  },
];

export const AboutUs: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { theme } = useTheme();

  return (
    <>
      <div className="_container text-left overflow-x-hidden">
        <H2 className="lg:hidden block mb-8 text-3xl font-bold text-gray-800">
          {t("aboutUs.title")}
        </H2>
        <div
          className="lg:block hidden"
          style={{ position: "relative", height: "400x" }}
        >
          <TextPressure
            text={"О  нас"}
            fontFamily="Noto Sans Display"
            flex={true}
            alpha={false}
            stroke={false}
            width={true}
            weight={true}
            italic={true}
            textColor={theme === "light" ? "black" : "white"}
            strokeColor="#ff0000"
            minFontSize={36}
          />
        </div>
        <div className="text-left w-full flex flex-col md:flex-row mb-12 justify-between">
          <P
            variant="primaryLarge"
            className="lg:w-1/2 max-w-2xl text-2xl leading-relaxex"
          >
            {t("aboutUs.firstDescriptionPart")}
          </P>
          <div className="flex flex-col justify-end lg:mt-0 mt-2">
            <P
              onClick={() => {
                navigate(PageLinks.ABOUT_US_PAGE);
              }}
              className="items-end cursor-pointer"
            >
              <u>Больше о наc</u>
            </P>
          </div>
        </div>
      </div>
      <div className="relative h-[450px] mb-12">
        <CircularGallery
          items={circularGalaryItems}
          bend={-2}
          textColor={theme === "light" ? "black" : "white"}
          borderRadius={0.05}
          scrollEase={0.02}
        />
      </div>
      <div className="_container text-left w-full flex lg:flex-row flex-col items-center lg:items-between lg:justify-between mb-12 gap-5">
        <div className="items-center justify-left flex flex-col">
          <TiltedCard
            imageSrc="/src/assets/circularGalary/wine-video.mp4"
            altText="Вина хотите?"
            captionText="Вина хотите?"
            containerHeight="300px"
            containerWidth="300px"
            imageHeight="300px"
            imageWidth="300px"
            rotateAmplitude={12}
            scaleOnHover={1.2}
            showMobileWarning={false}
            showTooltip={true}
            displayOverlayContent={true}
            overlayContent={
              <p className="m-5 text-base-light font-bold bg-base-dark/50 py-2 px-5 border-base-dark rounded-full">
                Kendrick Lamar - GNX
              </p>
            }
          />
        </div>
        <P
          variant="primaryLarge"
          className="lg:w-2/3 max-w-2xl text-2xl leading-relaxex"
        >
          {t("aboutUs.secondDescriptionPart")}
        </P>
      </div>
    </>
  );
};
