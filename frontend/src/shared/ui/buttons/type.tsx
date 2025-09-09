export type ButtonProps = {
  children: React.ReactNode;
  onClick?: () => void;
  mainColor: string;
  to?: string;
};

export { CloseButton } from "./closeButton";
