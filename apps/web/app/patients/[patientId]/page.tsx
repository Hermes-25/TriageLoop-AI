import { redirect } from "next/navigation";

export default async function PatientPage({ params }: { params: Promise<{ patientId: string }> }) {
  const { patientId } = await params;
  redirect(`/board?patient=${encodeURIComponent(patientId)}`);
}
