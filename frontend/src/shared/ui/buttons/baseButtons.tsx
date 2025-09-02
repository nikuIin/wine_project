import { useNavigate } from "react-router";
import React, { useState, useEffect } from "react";

type Variant = "fill" | "outline" | "aurora" | "auroraOutline";

interface BaseButtonStyles {
  children: React.ReactNode;
  onClick?: () => void;
  to?: string;
  anchor?: string;
  variant?: Variant;
  className?: string;
}

interface Ripple {
  x: number;
  y: number;
  size: number;
  id: number;
}

const variantStyles: Record<Variant, string> = {
  fill: "bg-main text-base-light dark:bg-main dark:text-base-dark hover:bg-main-hover",
  outline:
    "border-3 border-main text-main dark:border-main dark:text-main hover:bg-main dark:hover:text-base-dark hover:text-base-light",
  aurora: "aurora-gradient",
  auroraOutline:
    "aurora-outline border-3 text-main dark:text-main dark:hover:text-base-dark hover:text-base-light",
};

export const BaseButton: React.FC<BaseButtonStyles> = ({
  children,
  onClick,
  to,
  anchor,
  variant = "fill",
  className,
}) => {
  const navigate = useNavigate();
  const [ripples, setRipples] = useState<Ripple[]>([]);

  useEffect(() => {
    const styleId = "custom-button-animation-style";
    if (document.getElementById(styleId)) return;

    const style = document.createElement("style");
    style.id = styleId;
    style.innerHTML = `
      @keyframes ripple-effect {
        from { transform: scale(0); opacity: 1; }
        to { transform: scale(2); opacity: 0; }
      }
      .animate-ripple {
        animation: ripple-effect 0.7s ease-out forwards;
      }
      @keyframes aurora-gradient-move {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
      }
      .aurora-gradient {
        background: linear-gradient(120deg, #da0c81, #e83d6f, #f06a9b, #ff9ac1, #da0c81);
        background-size: 200% 200%;
        animation: aurora-gradient-move 10s ease-in-out infinite;
        color: #fff;
        box-shadow: 0 0 16px #da0c81aa;
        transition: background 0.3s, color 0.3s;
      }
      .aurora-outline {
        position: relative;
        border-radius: 0.375rem; /* rounded-md */
        background: transparent;
        color: #da0c81;
        z-index: 0;
        overflow: visible;
      }

      .aurora-outline::before {
        content: '';
        position: absolute;
        top: -3px;
        left: -3px;
        right: -3px;
        bottom: -3px;
        border-radius: 0.375rem;
        padding: 3px; /* толщина обводки */
        background: linear-gradient(120deg, #da0c81, #e83d6f, #f06a9b, #ff9ac1, #da0c81);
        -webkit-mask:
          linear-gradient(#fff 0 0) content-box,
          linear-gradient(#fff 0 0);
        -webkit-mask-composite: destination-out;
        mask-composite: exclude;
        z-index: -1;
        animation: aurora-gradient-move 10s ease-in-out infinite;
        pointer-events: none;
        transition: background 0.3s ease;
      }

      /* Hover — заливка внутри с анимацией */
      .aurora-outline:hover {
        color: #fff;
        background: linear-gradient(120deg, #da0c81, #e83d6f, #f06a9b, #ff9ac1, #da0c81);
        animation: aurora-gradient-move 10s ease-in-out infinite;
      }
    `;
    document.head.appendChild(style);
  }, []);

  const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    const button = event.currentTarget;
    const rect = button.getBoundingClientRect();
    const rippleSize = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - rippleSize / 2;
    const y = event.clientY - rect.top - rippleSize / 2;

    const newRipple: Ripple = { x, y, size: rippleSize, id: Date.now() };
    setRipples((currentRipples) => [...currentRipples, newRipple]);

    setTimeout(() => {
      setRipples((currentRipples) =>
        currentRipples.filter((r) => r.id !== newRipple.id),
      );
    }, 700);

    if (to) {
      navigate(to);
    } else if (onClick) {
      onClick();
    } else if (anchor) {
      const element = document.getElementById(location.hash.replace("#", ""));

      setTimeout(() => {
        window.scrollTo({
          behavior: element ? "smooth" : "auto",
          top: element ? element.offsetTop : 0,
        });
      }, 100);
    }
  };

  const rippleColor = "bg-base-light/30 dark:bg-base-dark/20";

  return (
    <button
      onClick={handleClick}
      className={`${variantStyles[variant]} w-40 px-2 py-1 font-bold rounded-md cursor-pointer duration-300 relative overflow-visible ${className}`} // overflow-visible у кнопки
    >
      <div
        className="ripple-container relative rounded-md overflow-hidden z-0"
        style={{ inset: 0, position: "absolute" }}
      >
        <div className="absolute inset-0 z-0">
          {ripples.map((ripple) => (
            <span
              key={ripple.id}
              className={`absolute rounded-full animate-ripple ${rippleColor}`}
              style={{
                left: ripple.x,
                top: ripple.y,
                width: ripple.size,
                height: ripple.size,
                zIndex: 0,
              }}
            />
          ))}
        </div>
      </div>
      <span className="relative z-10">{children}</span>
    </button>
  );
};
