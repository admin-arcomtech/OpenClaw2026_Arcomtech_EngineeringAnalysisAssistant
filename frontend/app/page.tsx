import { LoginForm } from "@/components/auth/LoginForm";

export default function LoginPage() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center px-4 bg-gradient-to-b from-brand-light to-white">
      <div className="w-full max-w-sm">
        {/* Logo / App Name */}
        <div className="text-center mb-10">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-brand rounded-2xl shadow-lg mb-4">
            <svg className="w-9 h-9 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8}
                d="M9 3H5a2 2 0 00-2 2v4m6-6h10a2 2 0 012 2v4M9 3v18m0 0h10a2 2 0 002-2V9M9 21H5a2 2 0 01-2-2V9m0 0h18" />
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-gray-900">Arcom EI</h1>
          <p className="text-sm text-gray-500 mt-1">Engineering Intelligence Platform</p>
        </div>

        {/* Login Card */}
        <div className="bg-white rounded-2xl shadow-md px-6 py-8">
          <h2 className="text-lg font-semibold text-gray-800 mb-6">Masuk ke sistem</h2>
          <LoginForm />
        </div>

        <p className="text-center text-xs text-gray-400 mt-6">
          © 2026 Arcomtech — Confidential
        </p>
      </div>
    </main>
  );
}
