import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Drone Control Station",
  description: "Glassmorphism drone controls with serverless telemetry endpoints"
};

import { SkipLink } from "./components/skip-link";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <SkipLink />
        {children}
      </body>
    </html>
  );
}
