import { Header } from "@widgets/header";
import React from "react";

export const FullScreenPage: React.FC = () => {
  return (
    <>
      <Header />

      <main className="flex-grow content text-black dark:text-white">
        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">Основной контент</h2>
          <p className="mb-4">
            Здесь располагается основной текст страницы. Можно добавить много параграфов, чтобы заполнить пространство и
            показать прокрутку.
          </p>
          <p className="mb-4">
            Используйте форматирование текста, списки и другие HTML-элементы для лучшего восприятия.
          </p>
          <ul className="list-disc list-inside space-y-2">
            <li>Пункт первый</li>
            <li>Пункт второй с дополнительным описанием</li>
            <li>Подробнее о третьем пункте</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">Дополнительные сведения</h2>
          <p>Страница адаптируется под тему с помощью Tailwind и поддерживает тёмную/светлую тему.</p>
        </section>
      </main>

      <footer className="mt-8 text-center text-sm text-gray-500 dark:text-gray-400">
        © 2025 Ваше приложение. Все права защищены.
      </footer>
    </>
  );
};
