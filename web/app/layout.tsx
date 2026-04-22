import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

const SITE_NAME = "Thirukkural for Kids";
const SITE_DESCRIPTION =
  "Ancient Tamil wisdom as six-line bedtime stories and folk-art comics, for four-year-olds and the grown-ups reading with them.";

export const metadata: Metadata = {
  title: { default: SITE_NAME, template: `%s · ${SITE_NAME}` },
  description: SITE_DESCRIPTION,
  openGraph: {
    siteName: SITE_NAME,
    title: SITE_NAME,
    description: SITE_DESCRIPTION,
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: SITE_NAME,
    description: SITE_DESCRIPTION,
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen">
        <header className="border-b-2 border-ink/10 bg-cream">
          <div className="mx-auto flex max-w-5xl items-baseline justify-between px-6 py-5">
            <Link href="/" className="font-serif text-xl font-semibold text-indigo">
              Thirukkural for Kids
            </Link>
            <span className="hidden text-sm text-ink/60 sm:inline">
              A kural a day, in six lines.
            </span>
          </div>
        </header>
        <main className="mx-auto max-w-5xl px-6 py-10">{children}</main>
        <footer className="mt-16 border-t-2 border-ink/10 py-8 text-center text-sm text-ink/60">
          Stories &amp; comics licensed CC BY-SA 4.0. Thirukkural is in the public domain.
        </footer>
      </body>
    </html>
  );
}
