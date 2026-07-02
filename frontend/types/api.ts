export type TailorRequest = {
  job_description: string;
};

export type AtsScore = {
  score: number;
  matched_keywords: string[];
  missing_keywords: string[];
  total_keywords?: number;
};

export type TailorResponse = {
  run_id: string;
  markdown: string;
  ats_score: AtsScore;
};

export type ExportRequest = {
  run_id: string;
};

export type ExportResponse = {
  run_id: string;
  pdf_path: string;
};
