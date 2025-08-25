"use client";
import { Modal } from "./Modal";

export const BaseModal = ({
  open,
  onClose,
  children,
}: {
  open: boolean;
  onClose: () => void;
  children: React.ReactNode;
}): React.ReactNode | null => {
  const element: React.ReactNode = (
    <>
      <div className="fixed inset-0 flex items-center justify-center z-50 font-sans" onClick={onClose}>
        {/* Background with subtle blur and dark mode support */}
        <div className="fixed inset-0 bg-zinc-100/50 dark:bg-black/50 backdrop-blur-sm" aria-hidden="true" />
        {/* Modal card with glassmorphism, shadcn-like styling, and hover effects */}
        <div
          className="relative z-50 w-full max-w-sm p-6 bg-white/40 dark:bg-black/40 rounded-lg border border-zinc-200 dark:border-zinc-800 shadow-lg dark:shadow-zinc-900/50 overflow-auto max-h-[90vh]"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Content area with consistent typography */}
          <div className="text-zinc-900 dark:text-zinc-50">{children}</div>
        </div>
      </div>
    </>
  );

  return <Modal open={open} onClose={onClose} element={element} />;
};
