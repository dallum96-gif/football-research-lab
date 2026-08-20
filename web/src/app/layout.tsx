import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Football Research Laboratory",
  description: "Foundation spike for the FRL visual research platform.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en-GB">
      <body>{children}</body>
    </html>
  );
}
