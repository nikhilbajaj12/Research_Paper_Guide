export interface ComplianceIssue {
  issue_id: string;
  category: string;
  severity: 'critical' | 'warning' | 'info';
  message: string;
  location?: string;
  suggested_fix?: string;
  needs_verification: boolean;
}

export interface RecommendationDetail {
  issue: string;
  location: string;
  severity: string;
  suggested_action: string;
  explanation: string;
  category: string;
  can_auto_fix: boolean;
}

export interface ComplianceReport {
  project_id?: string;
  paper_id: string;
  conference_id: string;
  overall_status: string;
  readiness_score: number;
  issues: ComplianceIssue[];
  passed_checks: string[];
  warnings_count: number;
  critical_count: number;
  fix_suggestions?: FixSuggestion[];
  recommendations?: RecommendationDetail[];
}

export interface FixSuggestion {
  issue_id: string;
  can_auto_fix: boolean;
  suggested_action: string;
  replacement_text?: string | null;
  explanation: string;
}
