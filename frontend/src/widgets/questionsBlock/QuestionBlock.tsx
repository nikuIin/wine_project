import { H2 } from "@shared/ui/texts";
import { AccordionSection } from "@widgets/accordion";
import { QuestionForm } from "@widgets/contactForm";

export const QuestionBlock = () => {
  return (
    <>
      <div className="_container items-center text-center pt-20">
        <H2>Частые вопросы</H2>
        <div className="text-left">
          <AccordionSection />
        </div>
      </div>
      <div className="_container items-center text-center">
        <H2>Не нашли ответа на свой вопрос?</H2>
        <QuestionForm />
      </div>
    </>
  );
};
