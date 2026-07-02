import { apiClient, downloadFile } from "./client";
import type { ExportRequest, ExportResponse } from "@/types/api";

export function exportPdf(body: ExportRequest): Promise<ExportResponse> {
  return apiClient<ExportResponse>("/export", {
    method: "POST",
    body,
  });
}

export async function downloadPdf(runId: string): Promise<void> {
  await downloadFile(`/export/${runId}/download`, `resume-${runId}.pdf`);
}
