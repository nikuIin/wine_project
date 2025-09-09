export const LanguageIcon = ({
  width = "24px",
  height = "24px",
  stroke = "currentColor",
  strokeWidth = "1.5",
  className = "",
  fill = "none",
  color = "currentColor",
  title = "Language",
}) => (
  <svg
    width={width}
    height={height}
    viewBox="0 0 24 24"
    role="img"
    xmlns="http://www.w3.org/2000/svg"
    aria-labelledby="languageIconTitle"
    stroke={stroke}
    strokeWidth={strokeWidth}
    strokeLinecap="square"
    strokeLinejoin="miter"
    fill={fill}
    color={color}
    className={className}
  >
    <title id="languageIconTitle">{title}</title>
    <circle cx="12" cy="12" r="10" />
    <path
      strokeLinecap="round"
      d="M12,22 C14.6666667,19.5757576 16,16.2424242 16,12 C16,7.75757576 14.6666667,4.42424242 12,2 C9.33333333,4.42424242 8,7.75757576 8,12 C8,16.2424242 9.33333333,19.5757576 12,22 Z"
    />
    <path strokeLinecap="round" d="M2.5 9L21.5 9M2.5 15L21.5 15" />
  </svg>
);
