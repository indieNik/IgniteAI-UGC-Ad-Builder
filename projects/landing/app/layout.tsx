import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: '--font-inter',
  display: 'swap',
});

export const metadata: Metadata = {
  title: "IgniteAI - AI-Powered UGC Ad Video Generator",
  description: "Generate short-form ad videos designed for iteration, testing, and scale. Create variations without shipping product or hiring actors.",
  openGraph: {
    title: "IgniteAI - AI-Powered UGC Ad Video Generator",
    description: "Stop burning cash on creative fatigue. Generate viral ad videos in minutes.",
    images: ["/og-image.png"],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.variable} antialiased`}>{children}</body>
    </html>
  );
}
