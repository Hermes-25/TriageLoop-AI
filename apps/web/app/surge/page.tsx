import type { Metadata } from "next";
import { CapacityView } from "@/app/components/CapacityView";

export const metadata: Metadata = { title: "Capacity truth" };

export default function SurgePage() { return <CapacityView />; }
