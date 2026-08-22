import type { Metadata } from "next";
import "./globals.css";
import { AppShell } from "@/app/components/AppShell";
import { ProductProvider } from "@/app/components/ProductProvider";

export const metadata: Metadata = {
  title: { default: "TriageLoop", template: "%s · TriageLoop" },
  description: "Deadline-aware emergency-department waiting-room decision support prototype.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <ProductProvider>
          <AppShell>{children}</AppShell>
        </ProductProvider>
      </body>
    </html>
  );
}
