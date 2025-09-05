import { useTheme } from "@shared/index";
import { ScrollVelocity } from "@shared/ui/texts";
import React from "react";

// Interface for wine card data
interface WineCard {
  imageUrl: string;
  title: string;
  description: string;
}

// Factory function to create wine card data
const createWineCard = (
  imageUrl: string,
  title: string,
  description: string,
): WineCard => ({
  imageUrl,
  title,
  description,
});

// Wine card component
const WineCardComponent: React.FC<{ card: WineCard }> = ({ card }) => {
  const { theme } = useTheme();

  // Dynamic classes based on theme
  const bgColor = theme === "dark" ? "bg-base-dark" : "bg-base-light";
  const textColor = theme === "dark" ? "text-base-light" : "text-base-dark";

  return (
    <div
      className={`group ${bgColor} rounded-xl shadow-lg hover:shadow-xl p-5 flex flex-col items-center text-center transition-all duration-300 ease-in-out hover:h-[480px] h-[400px] w-full max-w-xs relative overflow-hidden`}
    >
      <h3
        className={`text-lg font-semibold ${textColor} mb-3 h-14 flex items-center justify-center text-center z-10 leading-tight`}
      >
        <span dangerouslySetInnerHTML={{ __html: card.title }} />
      </h3>
      <p
        className={`text-xs ${textColor} mb-4 absolute top-20 opacity-0 group-hover:opacity-100 transition-all duration-300 ease-in-out transform group-hover:translate-y-0 translate-y-4 w-full px-5`}
      >
        {card.description}
      </p>
      <div className="relative flex flex-col items-center w-full h-full">
        <img
          src={card.imageUrl}
          alt={card.title.replace(/<br>/g, " ")}
          className="w-full h-60 object-contain rounded-md transition-all duration-300 ease-in-out group-hover:translate-y-28 z-0"
        />
      </div>
    </div>
  );
};

// Main widget component
export const MarketableWines: React.FC = () => {
  // Create wine card data using factory
  const wineCards: WineCard[] = [
    createWineCard(
      "https://levgolitsin.ru/upload/iblock/deb/qoh7vy911sgfyz3p3wq3ticcfqhdwldw/about-5block-1.png",
      "Наследие мастера<br>«Левъ Голицынъ»",
      "«Лев Голицын» станет прекрасным сопровождением любого праздника. Изысканные вина от экстра брют до полусладкого подчеркнут вкус самых разных блюд и закусок.",
    ),
    createWineCard(
      "https://levgolitsin.ru/upload/iblock/8e6/ini2d04v69iz6okaogr5tqg71zhf744j/about-5block-2.png",
      "Левъ Голицынъ.<br>Коронационное",
      "Коллекция игристых вин для особого случая. Элегантные вина с завораживающим утончённым вкусом и устойчивым мелким перляжем.",
    ),
    createWineCard(
      "https://levgolitsin.ru/upload/iblock/173/1kf0m008awabqosjt1iyjiu3o47sbyt6/about-5block-3.png",
      "Левъ Голицынъ<br>Брют Зеро Метод Классик",
      "Сложное и изысканное игристое вино. Оно произведено методом вторичного брожения в бутылках с выдержкой на осадке не менее девяти месяцев.",
    ),
  ];

  return (
    <>
      <div className="mt-20">
        <ScrollVelocity
          texts={["Ходовые вина   ", "Ходовые вина   "]}
          velocity={140}
        />
      </div>

      <div className="container mx-auto px-4 py-8">
        <h2 className="text-3xl md:text-4xl font-bold text-center mb-8 leading-tight text-base-dark dark:text-base-light">
          «Левъ Голицынъ» — не просто игристое вино. Это магия, которая поможет
          вам создать свои собственные неповторимые моменты
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 justify-items-center">
          {wineCards.map((card, index) => (
            <WineCardComponent key={index} card={card} />
          ))}
        </div>
      </div>
    </>
  );
};
