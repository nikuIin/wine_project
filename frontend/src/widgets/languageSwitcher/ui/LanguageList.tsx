import { AnimatedList } from "@shared/ui/lists";
import { Locales } from "@shared/enums";
import { BaseModal } from "@shared/ui/modal";
import { useTranslation } from "react-i18next";
import { changeLanguage } from "i18next";
import { Languages } from "@shared/index";
import { Notification, useToast } from "@shared/ui/notifications";
import { LanguageIcon } from "@shared/ui/icons";
import { CloseButton } from "@shared/ui/buttons/closeButton";

export const LanguageList = ({ open, onClose }: { open: boolean; onClose: () => void }) => {
  const languageList = Object.values(Locales).map((locale) => ({
    tag: locale.tag,
    name: locale.name,
    flagEmoji: locale.flagEmoji,
  }));

  const { notifications, success, warning, removeToast } = useToast();

  const { t } = useTranslation();

  return (
    <div>
      <BaseModal open={open} onClose={onClose}>
        <div>
          <div className="relative text-center space-y-3">
            <div className="absolute top-0 right-0">
              {/* Close window button */}
              <CloseButton onClick={onClose} color="gray" />
            </div>
            <div className="inline-flex p-2 bg-zinc-100 dark:bg-zinc-900 rounded-md border border-zinc-200 dark:border-zinc-800">
              <LanguageIcon />
            </div>
            <div>
              <p className="text-2xl font-semibold tracking-tight text-zinc-900 dark:text-white">
                {t("chooseLanguage")}
              </p>
            </div>
          </div>
          <div className="pt-4">
            <AnimatedList
              items={languageList.map((locale) => locale.name + " " + locale.flagEmoji)}
              onItemSelect={(item) => {
                const selectedLocale = languageList.find((locale) => locale.name + " " + locale.flagEmoji === item);
                if (selectedLocale) {
                  changeLanguage(selectedLocale.tag);
                  success(t("notification.success.status"), t("notification.success.message"));
                } else {
                  changeLanguage(Languages.DEFAULT);
                  warning(t("notification.warning.status"), t("notification.warning.message"));
                }
                onClose();
              }}
              className="w-[75]"
              enableArrowNavigation={true}
              displayScrollbar={false}
              showGradients={false}
            />
          </div>
        </div>
      </BaseModal>
      {/* Toast Container */}
      <div className="fixed bottom-4 right-4 z-50 space-y-2">
        {notifications.map((toast) => (
          <Notification key={toast.id} {...toast} onClose={() => removeToast(toast.id)} />
        ))}
      </div>
    </div>
  );
};
