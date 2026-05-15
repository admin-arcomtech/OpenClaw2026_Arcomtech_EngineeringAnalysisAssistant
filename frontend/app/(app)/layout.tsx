import { BottomNav } from "@/components/nav/BottomNav";
import { OfflineBanner } from "@/components/ui/OfflineBanner";
import { NotificationBell } from "@/components/nav/NotificationBell";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen pb-nav">
      <OfflineBanner />
      <header className="fixed top-0 right-0 z-30 p-3 max-w-lg mx-auto w-full flex justify-end pointer-events-none">
        <div className="pointer-events-auto">
          <NotificationBell />
        </div>
      </header>
      <main className="max-w-lg mx-auto pt-12">{children}</main>
      <BottomNav />
    </div>
  );
}
