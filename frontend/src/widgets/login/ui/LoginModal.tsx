import { Login } from "@widgets/login";
import { Modal } from "@shared/ui/modal";

export const LoginModal = ({ open, onClose }: { open: boolean; onClose: () => void }) => {
  return <Modal element={Login({ onClose })} open={open} onClose={onClose}></Modal>;
};
