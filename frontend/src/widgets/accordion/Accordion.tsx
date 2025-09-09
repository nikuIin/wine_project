"use client";

import React, { useState } from "react";
import {
  GlassWater,
  Grape,
  Barrel,
  ThermometerSun,
  Sprout,
  Truck,
  Beaker,
  Award,
} from "lucide-react";
import { useTranslation } from "react-i18next";

const faqData = [
  {
    icon: <GlassWater size={20} className="text-gray-500 dark:text-gray-400" />,
    key: "wineTypes",
  },
  {
    icon: <Grape size={20} className="text-gray-500 dark:text-gray-400" />,
    key: "grapeVarieties",
  },
  {
    icon: <Barrel size={20} className="text-gray-500 dark:text-gray-400" />,
    key: "wineAging",
  },
  {
    icon: (
      <ThermometerSun size={20} className="text-gray-500 dark:text-gray-400" />
    ),
    key: "climateImpact",
  },
  {
    icon: <Sprout size={20} className="text-gray-500 dark:text-gray-400" />,
    key: "organicWine",
  },
  {
    icon: <Truck size={20} className="text-gray-500 dark:text-gray-400" />,
    key: "wineTransport",
  },
  {
    icon: <Beaker size={20} className="text-gray-500 dark:text-gray-400" />,
    key: "wineTesting",
  },
  {
    icon: <Award size={20} className="text-gray-500 dark:text-gray-400" />,
    key: "wineAwards",
  },
];

interface AccordionItemProps {
  item: {
    icon: React.ReactNode;
    key: string;
  };
  isOpen: boolean;
  onToggle: () => void;
}

const AccordionItem: React.FC<AccordionItemProps> = ({
  item,
  isOpen,
  onToggle,
}) => {
  const { t } = useTranslation();

  return (
    <div className="border-b border-zinc-200 dark:border-zinc-700 last:border-b-0">
      <button
        className="flex cursor-pointer items-center justify-between w-full p-6 text-left focus:outline-none hover:bg-zinc-200 dark:hover:bg-zinc-800 transition-colors duration-700"
        onClick={onToggle}
      >
        <div className="flex items-center space-x-4">
          {item.icon}
          <span className="text-base font-medium text-gray-800 dark:text-gray-200">
            {t(`questions.${item.key}`)}
          </span>
        </div>
        <svg
          className={`transform transition-transform duration-300 text-gray-500 dark:text-gray-400 ${isOpen ? "rotate-180" : ""}`}
          width="20"
          height="20"
          viewBox="0 0 20 20"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M5 7.5L10 12.5L15 7.5"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </button>
      <div
        className={`overflow-hidden transition-all duration-300 ease-in-out ${
          isOpen ? "max-h-96" : "max-h-0"
        }`}
      >
        <div className="p-4 pl-12">
          <p className="text-gray-600 dark:text-gray-300">
            {t(`questions.${item.key}Answer`)}
          </p>
        </div>
      </div>
    </div>
  );
};

export default function AccordionSection() {
  const [openIndex, setOpenIndex] = useState<number | null>(2);

  const handleToggle = (index: number) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  return (
    <div className="flex w-full items-center justify-center">
      <div className="w-full max-w-4xl">
        <div className="border border-b-zinc-100 dark:border-zinc-700 rounded-lg">
          {faqData.map((item, index) => (
            <AccordionItem
              key={index}
              item={item}
              isOpen={openIndex === index}
              onToggle={() => handleToggle(index)}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
