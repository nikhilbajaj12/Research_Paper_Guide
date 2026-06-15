export interface ConferenceBrief {
  id: string;
  abbr: string;
  name: string;
  start_date: string;
  submission_deadline: string;
  location: string;
  flag?: string;
  conference_type?: string;
  topics?: string[];
  description?: string | null;
}

export interface ConferenceGuidelines {
  conference_id: string;
  max_pages: number;
  requires_anonymity: boolean;
  reference_format: string;
  required_sections?: string[];
}

export interface Conference extends ConferenceBrief {
  url?: string;
  guidelines?: ConferenceGuidelines;
  notification_date?: string | null;
  acceptance_rate?: number | null;
  max_pages?: number;
  requires_anonymity?: boolean;
  reference_format?: string;
}
