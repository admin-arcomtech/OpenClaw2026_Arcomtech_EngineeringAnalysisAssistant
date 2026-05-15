import { BottomNav } from "@/components/nav/BottomNav";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen pb-nav">
      <main className="max-w-lg mx-auto">{children}</main>
      <BottomNav />
    </div>
  );
}
