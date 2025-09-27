import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "FGSM Adversarial Attack Demo",
  description:
    "Interactive demonstration of Fast Gradient Sign Method (FGSM) adversarial attacks on machine learning models",
  keywords:
    "FGSM, adversarial attacks, machine learning, AI security, deep learning",
  authors: [{ name: "DevNeuron Internship Assessment" }],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </head>
      <body className={inter.className}>{children}</body>
    </html>
  );
}
