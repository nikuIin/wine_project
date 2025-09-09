import { BaseContactForm } from "@widgets/contactForm";

interface QuestionFormProps {
  onClose?: () => void;
  onBack?: () => void;
}

export const QuestionForm = ({ onClose, onBack }: QuestionFormProps) => {
  return <BaseContactForm includeQuestion onClose={onClose} onBack={onBack} />;
};
