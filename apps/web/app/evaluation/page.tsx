import type { Metadata } from "next";
import { EvaluationView } from "@/app/components/EvaluationView";

export const metadata: Metadata = { title: "Evidence" };

export default function EvaluationPage() { return <EvaluationView />; }
