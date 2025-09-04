interface PProperties {
  className?: string;
  variant?: PStyleVariant;
  children: React.ReactNode;
  onClick?: () => void;
}

type PStyleVariant = "primary" | "dim" | "smallDim" | "primaryLarge";

const basePrimaryStyles = "text-base-dark dark:text-base-light";

const pStyleVariants: Record<PStyleVariant, string> = {
  primary: `${basePrimaryStyles} text-lg`,
  primaryLarge: `${basePrimaryStyles} text-3xl`,
  dim: "",
  smallDim: "text-dim/20",
};

export const P: React.FC<PProperties> = ({
  className = "",
  variant = "primary",
  children,
  onClick,
}) => {
  return (
    <p
      onClick={onClick}
      className={`${className} ${pStyleVariants[variant]} max-w-[1280px] font-medium`}
    >
      {children}
    </p>
  );
};
