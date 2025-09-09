const Styles = {
  error: "bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800 text-red-600 dark:text-red-200",
  info: "bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800 text-blue-600 dark:text-blue-200",
};

type StyleType = keyof typeof Styles;

export const Message = ({
  message,
  styleType,
  className = "",
}: {
  message: string;
  styleType: StyleType;
  className?: string;
}): React.ReactNode => {
  return (
    <div
      className={`p-3 border rounded-md text-sm ${Styles[styleType]} ${className} relative overflow-hidden`}
      style={
        styleType === "error"
          ? {
              background: "conic-gradient(from red, transparent 75%, red, transparent 50%)",
              animation: "shimmer-spin 2.5s linear",
            }
          : {}
      }
    >
      {message}
    </div>
  );
};
