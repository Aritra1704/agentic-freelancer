import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Freelance-OS Control Tower",
  description: "Task board and manual agent trigger dashboard for Freelance-OS."
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
