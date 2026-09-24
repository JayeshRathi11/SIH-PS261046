import type { Metadata } from "next";
import "./globals.css";
import { AppProvider } from "@/context/AppContext";

export const metadata: Metadata = {
  title: "AyuTrial-CTMS | NPvCC Clinical Portal & CDSCO Workstation",
  description:
    "Regulatory-Grade Ayurvedic Clinical Trial Management System, 21 CFR Part 11 ALCOA+ Cryptographic Ledger, DPDP Act 2023 Consent & BioBERT MedDRA Coding Workstation",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        <link
          href="https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@500;600;700;800&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
        <link
          href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="bg-background text-on-surface antialiased min-h-screen flex flex-col font-sans selection:bg-secondary-container selection:text-on-secondary-fixed">
        <AppProvider>{children}</AppProvider>
      </body>
    </html>
  );
}
