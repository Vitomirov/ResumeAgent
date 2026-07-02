import { ResumeWorkspace } from "@/components/workspace/ResumeWorkspace";

export default function HomePage() {
  return (
    <main className="mx-auto max-w-3xl px-4 py-8 text-neutral-100">
      <h1 className="mb-6 text-xl font-semibold">ResumeAgent</h1>
      <ResumeWorkspace />
    </main>
  );
}
