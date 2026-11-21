import type { Metadata } from "next";
import { GeistSans } from "geist/font/sans";
import { GeistMono } from "geist/font/mono";
import { Analytics } from "@vercel/analytics/next";
import { signOutNow } from "./actions";
import { Footer } from "@/components/layout/Footer";
import { Header } from "@/components/layout/Header";
import { ToastProvider } from "@/components/ui/Toast";
import { currentUser } from "@/lib/auth";
import { BRAND } from "@/lib/brand";
import "@/styles/tokens.css";
import "@/styles/base.css";


export const metadata: Metadata = {
  title: { default: `${BRAND.name} — ${BRAND.tagline}`, template: `%s — ${BRAND.name}` },
  description: BRAND.description,
  // Google Search Console ownership of vivaran-kappa.vercel.app, needed for the Google sign-in consent screen.
  verification: { google: "winpmUDxnpwe276C3DpN9iCswXWb_0LsjaNDpzCq3HM" },
};

// Applies a remembered dark theme before paint, so there is no flash.
const THEME_SCRIPT = `try{if(localStorage.getItem("vivaran-theme")==="dark")document.documentElement.dataset.theme="dark"}catch(e){}`;

export default async function RootLayout({ children }: { children: React.ReactNode }) {
  const user = await currentUser();
  return (
    <html lang="en" className={`${GeistSans.variable} ${GeistMono.variable}`} suppressHydrationWarning>
      <head><script dangerouslySetInnerHTML={{ __html: THEME_SCRIPT }} /></head>
      <body>
        <ToastProvider>
          <Header user={user} signOut={signOutNow} />
          {children}
          <Footer />
        </ToastProvider>
        <Analytics />
      </body>
    </html>
  );
}
