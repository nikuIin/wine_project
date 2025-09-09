export const CheckIcon = ({ className = "" }: { className?: string }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="16"
    height="16"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className={className}
  >
    <polyline points="20,6 9,17 4,12"></polyline>
  </svg>
);

export const CrossIcon = ({ className = "" }: { className?: string }) => (
  <svg
    fill="currentColor"
    width="16"
    height="16"
    viewBox="0 0 24 24"
    id="cross"
    data-name="Line Color"
    xmlns="http://www.w3.org/2000/svg"
    className={className}
  >
    <line id="primary" x1="19" y1="19" x2="5" y2="5"></line>
    <line
      id="primary-2"
      data-name="primary"
      x1="19"
      y1="5"
      x2="5"
      y2="19"
    ></line>
  </svg>
);
