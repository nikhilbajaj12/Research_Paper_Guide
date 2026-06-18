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

export interface AssistantMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
}

export interface AssistantChatRequest {
  conference?: Record<string, any>;
  compliance_score: number;
  critical_issues: ComplianceIssue[];
  warnings: ComplianceIssue[];
  passed_checks: string[];
  recommendations: RecommendationDetail[];
  user_message: string;
}

export interface AssistantChatResponse {
  answer: string;
}

export interface FixStep {
  step_id: string;
  agent: string;
  action: string;
  target: string;
  details: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
}

export interface ExecutionPlan {
  plan_id: string;
  steps: FixStep[];
  summary: string;
}

export interface AgentResult {
  agent: string;
  success: boolean;
  changes_made: string[];
  error?: string | null;
}

export interface BeforeAfterScore {
  before_score: number;
  after_score: number;
  improvement: number;
  before_status: string;
  after_status: string;
}

export interface AuditEntry {
  timestamp: string;
  event: string;
  agent?: string;
  change?: string;
  error?: string;
  [key: string]: any;
}

export interface FixPipelineResult {
  plan: ExecutionPlan;
  agent_results: AgentResult[];
  score_comparison?: BeforeAfterScore | null;
  package_path?: string | null;
  package_download_url?: string | null;
  fixed_file_path?: string | null;
  audit_log: AuditEntry[];
  success: boolean;
  error?: string | null;
}

export interface AutoFixRequest {
  paper_id: string;
  conference_id: string;
  command: string;
  steps?: string[];
}

export interface AutoFixStatusResponse {
  pipeline_id: string;
  status: 'running' | 'completed' | 'failed';
  progress: number;
  result?: FixPipelineResult | null;
  error?: string | null;
}
