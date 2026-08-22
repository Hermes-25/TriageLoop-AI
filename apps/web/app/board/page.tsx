import type { Metadata } from "next";
import { PatientBoard } from "@/app/components/PatientBoard";

export const metadata: Metadata = { title: "Live board" };

export default function BoardPage() {
  return <PatientBoard />;
}
