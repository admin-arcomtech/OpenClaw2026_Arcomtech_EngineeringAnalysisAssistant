import { BottomNav } from "@/components/nav/BottomNav";
import { OfflineBanner } from "@/components/ui/OfflineBanner";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen pb-nav">
      <OfflineBanner />
      <main className="max-w-lg mx-auto">{children}</main>
      <BottomNav />
    </div>
  );
}
