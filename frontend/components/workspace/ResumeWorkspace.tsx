"use client";

import { useState } from "react";

import { downloadPdf, exportPdf } from "@/lib/api/export";
import { tailorResume } from "@/lib/api/tailor";
import type { AtsScore } from "@/types/api";

function formatApiError(err: unknown): string {
  if (!(err instanceof Error)) {
    return "Generation failed";
  }

  try {
    const payload = JSON.parse(err.message) as { detail?: string | { msg?: string }[] };
    if (typeof payload.detail === "string") {
      return payload.detail;
    }
    if (Array.isArray(payload.detail) && payload.detail[0]?.msg) {
      return payload.detail[0].msg;
    }
  } catch {
    // fall through
  }

  return err.message || "Generation failed";
}

export function ResumeWorkspace() {
  const [jobDescription, setJobDescription] = useState("");
  const [runId, setRunId] = useState<string | null>(null);
  const [markdown, setMarkdown] = useState("");
  const [atsScore, setAtsScore] = useState<AtsScore | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const canGenerate = jobDescription.trim().length > 0 && !isGenerating;
  const canDownload = Boolean(runId) && !isExporting && !isGenerating;

  async function handleGenerate() {
    setIsGenerating(true);
    setError(null);
    setRunId(null);
    setMarkdown("");
    setAtsScore(null);

    try {
      const result = await tailorResume({ job_description: jobDescription });
      setRunId(result.run_id);
      setMarkdown(result.markdown);
      setAtsScore(result.ats_score);
    } catch (err) {
      setError(formatApiError(err));
    } finally {
      setIsGenerating(false);
    }
  }

  async function handleDownload() {
    if (!runId) {
      return;
    }

    setIsExporting(true);
    setError(null);

    try {
      await exportPdf({ run_id: runId });
      await downloadPdf(runId);
    } catch (err) {
      setError(formatApiError(err));
    } finally {
      setIsExporting(false);
    }
  }

  return (
    <div className="space-y-6">
      <section className="space-y-3">
        <label htmlFor="job-description" className="block text-sm font-medium text-neutral-200">
          Job description
        </label>
        <textarea
          id="job-description"
          value={jobDescription}
          onChange={(event) => setJobDescription(event.target.value)}
          rows={10}
          placeholder="Paste the job description here"
          className="w-full rounded border border-neutral-700 bg-neutral-900 p-3 text-sm text-neutral-100 placeholder:text-neutral-500"
        />
        <div className="flex flex-wrap items-center gap-3">
          <button
            type="button"
            onClick={handleGenerate}
            disabled={!canGenerate}
            className="rounded border border-neutral-100 bg-neutral-100 px-4 py-2 text-sm text-neutral-900 disabled:cursor-not-allowed disabled:border-neutral-700 disabled:bg-neutral-800 disabled:text-neutral-500"
          >
            Generate
          </button>
          {isGenerating && (
            <span className="text-sm text-neutral-400">Generating resume... (30–60s)</span>
          )}
        </div>
      </section>

      {atsScore && (
        <section className="space-y-2 rounded border border-neutral-800 bg-neutral-900/50 p-4">
          <div className="flex items-baseline gap-2">
            <h2 className="text-sm font-medium text-neutral-200">ATS score</h2>
            <span className="text-lg font-semibold text-neutral-100">{atsScore.score}/100</span>
          </div>
          <p className="text-xs text-neutral-500">
            Based on technical requirements and soft skills extracted from the job posting
            {atsScore.total_keywords ? ` (${atsScore.total_keywords} keywords)` : ""}.
          </p>
          {atsScore.matched_keywords.length > 0 && (
            <p className="text-sm text-neutral-300">
              Matched: {atsScore.matched_keywords.join(", ")}
            </p>
          )}
          {atsScore.missing_keywords.length > 0 && (
            <p className="text-sm text-neutral-400">
              Missing: {atsScore.missing_keywords.join(", ")}
            </p>
          )}
        </section>
      )}

      <section>
        <button
          type="button"
          onClick={handleDownload}
          disabled={!canDownload}
          className="rounded border border-neutral-300 px-4 py-2 text-sm text-neutral-100 disabled:cursor-not-allowed disabled:border-neutral-800 disabled:text-neutral-600"
        >
          {isExporting ? "Preparing PDF..." : "Download PDF"}
        </button>
      </section>

      {error && <p className="text-sm text-red-400">{error}</p>}

      <section className="space-y-2">
        <h2 className="text-sm font-medium text-neutral-200">Resume preview</h2>
        {markdown ? (
          <pre className="max-h-[32rem] overflow-auto rounded border border-neutral-800 bg-neutral-900 p-4 text-sm whitespace-pre-wrap text-neutral-200">
            {markdown}
          </pre>
        ) : (
          <p className="text-sm text-neutral-500">Generated resume will appear here.</p>
        )}
      </section>
    </div>
  );
}
