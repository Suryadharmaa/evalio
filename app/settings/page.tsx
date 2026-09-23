import { PrivacyControls } from "@/components/settings/privacy-controls";

export default function SettingsPage() {
  return <div className="mx-auto w-full max-w-3xl px-5 py-12 sm:px-8"><p className="text-sm font-semibold text-primary">Account</p><h1 className="mt-2 text-4xl font-bold">Data & privacy settings</h1><PrivacyControls /></div>;
}
