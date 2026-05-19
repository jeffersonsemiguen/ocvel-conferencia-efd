export interface ValidationRun {
  id: string;
  fiscal_period_id: string;
  efd_file_id: string;
  status: string;
  started_at: string;
  finished_at: string | null;
  error: string | null;
  total_findings: number;
  critical_count: number;
  alert_count: number;
  monetary_count: number;
  observation_count: number;
  monetary_tolerance: number;
}

export interface ValidationFinding {
  id: string;
  rule_code: string;
  severity: string;
  finding_type: string;
  title: string;
  description: string | null;
  register_code: string | null;
  field_name: string | null;
  cfop: string | null;
  cst: string | null;
  tax_type: string | null;
  operation_type: string | null;
  efd_value: number | null;
  reference_value: number | null;
  difference_value: number | null;
  status: string;
  created_at: string;
}

export interface CorrectionSuggestion {
  id: string;
  finding_id: string;
  efd_file_id: string;
  validation_run_id: string | null;
  line_number: number;
  register_code: string;
  field_index: number;
  field_name: string;
  original_value: string | null;
  suggested_value: string;
  suggestion_reason: string | null;
  // low | medium | high | critical
  risk_level: string;
  // pending | approved | rejected | applied | canceled | conflict
  status: string;
  // technical | fiscal | structural | informational
  suggestion_type: string;
  // update_field | replace_line | insert_line_after | insert_line_before | delete_line | recalculate_total
  action_type: string;
  rule_code: string | null;
  approved_by: string | null;
  approved_at: string | null;
  rejected_by: string | null;
  rejected_at: string | null;
  rejection_reason: string | null;
  created_at: string;
}

export interface CorrectedFile {
  id: string;
  original_efd_file_id: string;
  generated_filename: string;
  file_hash: string | null;
  applied_suggestions_count: number;
  total_bytes: number | null;
  total_lines: number | null;
  // ready | error | generated | downloaded | archived | invalidated
  status: string;
  generated_at: string;
}

export type BlocoKTipo = "nao_aplica" | "simplificado" | "completo";
export type InventarioRef = "mes_anterior" | "dezembro_ano_anterior" | "customizado";

export interface InscricaoAuxiliar {
  uf: string;
  ie: string;
}

export interface Company {
  id: string;
  cnpj: string;
  name: string;
  trade_name: string | null;
  state_registration: string | null;
  state: string | null;
  is_active: boolean;
  uses_ciap: boolean;
  bloco_k_tipo: BlocoKTipo;
  inventario_mes: number | null;
  inventario_competencia_ref: InventarioRef | null;
  inscricoes_auxiliares: InscricaoAuxiliar[];
  created_at: string;
}

export interface FiscalPeriod {
  id: string;
  company_id: string;
  year: number;
  month: number;
  status: string;
  created_at: string;
}

export interface EfdFile {
  id: string;
  fiscal_period_id: string;
  original_filename: string;
  file_size_bytes: number | null;
  parse_status: string;
  parse_error: string | null;
  total_lines: number | null;
  efd_version: string | null;
  efd_cnpj: string | null;
  efd_company_name: string | null;
  efd_state: string | null;
  efd_start_date: string | null;
  efd_end_date: string | null;
  created_at: string;
}

export interface PdfApuracaoFile {
  id: string;
  fiscal_period_id: string;
  original_filename: string;
  file_size_bytes: number | null;
  total_pages: number | null;
  extraction_status: string;
  extraction_error: string | null;
  average_confidence: number | null;
  created_at: string;
}

export interface PdfExtractedPage {
  page_number: number;
  char_count: number;
  confidence_score: number;
  extraction_method: string;
  extracted_text: string | null;
}

export interface ApuracaoReferenceValue {
  id: string;
  fiscal_period_id: string;
  source_type: string;
  source_label: string | null;
  operation_type: string;
  tax_type: string;
  cfop: string | null;
  cst: string | null;
  csosn: string | null;
  cst_ipi: string | null;
  aliquot: number | null;
  accounting_value: number | null;
  icms_base: number | null;
  icms_amount: number | null;
  icms_st_base: number | null;
  icms_st_amount: number | null;
  ipi_base: number | null;
  ipi_amount: number | null;
  adjustment_code: string | null;
  adjustment_description: string | null;
  source_page: number | null;
  source_row: number | null;
  confidence_score: number | null;
  is_reviewed: boolean;
  reviewed_at: string | null;
  created_at: string;
}
