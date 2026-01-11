import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { MsalProvider } from "@/app/components/MsalProvider";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Multi-Cloud Operations Dashboard",
  description: "Dashboard for managing multi-cloud operations and costs",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <MsalProvider>
          {children}
        </MsalProvider>
      </body>
    </html>
  );
}
