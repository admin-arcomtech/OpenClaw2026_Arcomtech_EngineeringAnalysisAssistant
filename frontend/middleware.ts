import { NextRequest, NextResponse } from "next/server";

const PUBLIC_PATHS = ["/", "/_next", "/favicon.ico", "/api"];
const ADMIN_ONLY = ["/admin"];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Allow public paths
  if (PUBLIC_PATHS.some((p) => pathname.startsWith(p))) {
    return NextResponse.next();
  }

  // Token is stored in localStorage (client-side only), so middleware
  // uses a cookie fallback set during login for SSR redirect guard.
  // If no cookie present, redirect to login.
  const token = request.cookies.get("arcom_token")?.value;
  if (!token) {
    const loginUrl = new URL("/", request.url);
    loginUrl.searchParams.set("redirect", pathname);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
