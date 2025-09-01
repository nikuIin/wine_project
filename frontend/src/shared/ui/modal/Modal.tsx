import { useEffect } from "react";

export const Modal = ({
  open,
  onClose,
  element,
}: {
  open: boolean;
  onClose: () => void;
  element: React.ReactNode | Element;
}) => {
  useEffect(() => {
    if (!open) return;

    function onKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape") {
        onClose();
      }
    }
    window.addEventListener("keydown", onKeyDown);
    // document.body.style.overflow = "hidden"; // отключение скролла

    return () => {
      window.removeEventListener("keydown", onKeyDown);
      document.body.style.overflow = "";
    };
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 flex items-center justify-center z-50">
      <div
        className="fixed inset-0 dark:bg-black/50 backdrop-blur-sm"
        aria-hidden="true"
      />
      <>{element}</>
    </div>
  );
};
