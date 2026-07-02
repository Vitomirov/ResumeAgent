import { apiClient } from "./client";
import type { TailorRequest, TailorResponse } from "@/types/api";

export function tailorResume(body: TailorRequest): Promise<TailorResponse> {
  return apiClient<TailorResponse>("/tailor", {
    method: "POST",
    body,
  });
}
