import { AuroraText } from "@shared/ui/animations";
import { H2 } from "@shared/ui/texts";
import { ContactForm } from "@widgets/contactForm";

export const ContactWidget: React.FC = () => {
  return (
    <div className="_container text-center pt-20">
      <H2 variant="primaryBig">
        <span className="text-main font-bold">
          <AuroraText
            colors={["#da0c81", "#e83d6f", "#f06a9b", "#ff9ac1", "#9353d3"]}
            className="bg-base-dark dark:bg-base-light px-6 py-5 rounded-3xl -rotate-2"
          >
            Связаться
          </AuroraText>
        </span>{" "}
        с нами
      </H2>
      <ContactForm />
    </div>
  );
};
