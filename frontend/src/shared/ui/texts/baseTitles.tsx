interface HeaderProps {
  children: React.ReactNode;
  variant?: HeaderVariantStyle;
  className?: string;
}

type HeaderVariantStyle = "primary" | "secondary" | "outline" | "dimSmall";

const variantStyles: Record<HeaderVariantStyle, string> = {
  primary:
    "text-zinc-900 dark:text-zinc-100 font-bold lg:text-5xl md:text-4xl text-2xl",
  secondary: "",
  outline: "",
  dimSmall: "text-dim/80 text-lg font-normal",
};

export const H2: React.FC<HeaderProps> = ({
  children,
  variant = "primary",
  className,
}) => {
  return (
    <h2 className={`${variantStyles[variant]} ${className} mb-4`}>
      {children}
    </h2>
  );
};
