import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Freelance-OS Control Tower",
  description: "Lead inbox, task board, and manual agent triggers for Freelance-OS."
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
