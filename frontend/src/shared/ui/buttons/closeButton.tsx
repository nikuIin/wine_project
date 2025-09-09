export const CloseButton = ({ onClick, color }: { onClick: () => void; color: "white" | "gray" }): React.ReactNode => {
  return (
    <button className="cursor-pointer text-white hover:text-gray-300" onClick={onClick} aria-label="Закрыть">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        className="h-6 w-6"
        fill="none"
        viewBox="0 0 24 24"
        stroke={`${color === "white" ? "#fff" : "gray"}`}
      >
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
      </svg>
    </button>
  );
};
