import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Freelance-OS Control Tower",
  description: "Lead pipeline, strategy, and delivery dashboard for Freelance-OS."
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
