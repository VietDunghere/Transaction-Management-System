// ---- Enums / Literals ----

export type Role = 'OPERATOR' | 'REVIEWER' | 'MANAGER' | 'ADMIN';

export type TransactionStatus = 'PENDING' | 'APPROVED' | 'REJECTED' | 'MANUAL_REVIEW';

export type CaseStatus = 'OPEN' | 'ASSIGNED' | 'APPROVED' | 'REJECTED' | 'CLOSED';

export type CaseDecision = 'APPROVE' | 'REJECT';

export type LoanStatus = 'PENDING' | 'SCORING' | 'APPROVED' | 'REJECTED' | 'MANUAL_REVIEW';

export type LoanDecision = 'APPROVE' | 'REJECT';

export type RiskLevel = 'LOW RISK' | 'MEDIUM RISK' | 'HIGH RISK';

export type EtlJobStatus = 'RUNNING' | 'SUCCESS' | 'FAILED';

export type AuditEntityType = 'Transaction' | 'User' | 'ReviewCase' | 'Loan';

// ---- Common ----

export interface PagedResponse<T> {
    total: number;
    page: number;
    limit: number;
    data: T[];
}

export interface ErrorResponse {
    code: string;
    message: string;
    path: string;
}

export interface MessageResponse {
    message: string;
}

// ---- UC02: Auth ----

export interface User {
    user_id: string;
    username: string;
    full_name: string;
    email: string;
    role: Role;
    is_active: boolean;
    created_at: string;
}

export interface LoginRequest {
    username: string;
    password: string;
}

export interface LoginResponse {
    access_token: string;
    refresh_token: string;
    token_type: string;
    expires_in: number;
    user_id: string;
    username: string;
    full_name: string;
    role: Role;
}

export interface RefreshRequest {
    refresh_token: string;
}

export interface RefreshResponse {
    access_token: string;
    token_type: string;
    expires_in: number;
}

export interface ChangePasswordRequest {
    current_password: string;
    new_password: string;
    confirm_password: string;
}

export interface MeResponse {
    user_id: string;
    username: string;
    full_name: string | null;
    role: Role;
    is_active: boolean;
}

// ---- UC03: Transactions ----

export interface Transaction {
    txn_id: string;
    customer_id: string;
    merchant_id: string;
    amount: number;
    currency_code: string;
    status: TransactionStatus;
    fraud_score: number;
    txn_time: string;
    created_at: string;
}

export interface TransactionDetail extends Transaction {
    card_number_masked: string;
    reason_code: string;
    source_ip: string;
    updated_at: string;
}

export interface TransactionSubmitRequest {
    customer_id: string;
    merchant_id: string;
    channel_id: number;
    card_number_masked: string;
    amount: number;
    currency_code: string;
    txn_time: string;
    source_ip: string;
}

export interface TransactionSubmitResponse {
    txn_id: string;
    status: TransactionStatus;
    fraud_score: number;
    reason_code: string;
    created_at: string;
}

export interface StateHistoryEntry {
    state_hist_id: string;
    txn_id: string;
    old_status: TransactionStatus | null;
    new_status: TransactionStatus;
    changed_at: string;
    changed_by_user_id: string | null;
}

// ---- UC04: Users ----

export interface CreateUserRequest {
    username: string;
    full_name: string;
    email: string;
    password: string;
    role: Exclude<Role, 'ADMIN'>;
}

export interface UpdateRoleRequest {
    role: Exclude<Role, 'ADMIN'>;
}

export interface UpdateRoleResponse {
    user_id: string;
    role: Role;
    updated_at: string;
}

// ---- UC05: Cases ----

export interface CaseListItem {
    case_id: string;
    txn_id: string;
    case_status: CaseStatus;
    assigned_to: string | null;
    transaction?: {
        txn_id: string;
        amount: number;
        fraud_score: number;
        merchant_id: string;
    } | null;
    created_at: string;
}

export interface CaseDetail {
    case_id: string;
    txn_id: string;
    case_status: CaseStatus;
    assigned_to: string | null;
    decision: CaseDecision | null;
    decision_note: string | null;
    version: number;
    transaction: {
        txn_id: string;
        customer_id: string;
        merchant_id: string;
        amount: number;
        fraud_score: number;
        txn_time: string;
    };
    created_at: string;
    decided_at: string | null;
}

export interface AssignCaseResponse {
    case_id: string;
    case_status: CaseStatus;
    assigned_to: string;
    created_at: string;
}

export interface CaseDecisionRequest {
    decision: CaseDecision;
    decision_note: string;
    version: number;
}

export interface CaseDecisionResponse {
    case_id: string;
    txn_id: string;
    case_status: CaseStatus;
    decision: CaseDecision;
    decided_at: string;
    version: number;
}

// ---- UC06: Loans ----

export interface Loan {
    loan_id: string;
    customer_id: string;
    status: LoanStatus;
    principal_amount: number;
    currency_code: string;
    interest_rate: number;
    term_months: number;
    pd_score: number | null;
    risk_level: RiskLevel | null;
    created_at: string;
}

export interface LoanDetail extends Loan {
    purpose: string;
    monthly_payment: number | null;
    maturity_date: string | null;
    reviewed_by: string | null;
    reviewed_at: string | null;
}

export interface CreateLoanRequest {
    customer_id: string;
    principal_amount: number;
    currency_code: string;
    interest_rate: number;
    term_months: number;
    purpose: string;
}

export interface LoanSimulateRequest {
    person_age: number;
    person_income: number;
    person_home_ownership: string;
    person_emp_length: number;
    loan_amount: number;
    loan_grade: string;
    loan_intent: string;
    cb_person_default_on_file: string;
    cb_person_cred_hist_length: number;
    requested_term_months: number;
}

export interface LoanSimulateResponse {
    pd_score: number;
    risk_level: RiskLevel;
    decision: string;
    confidence: number;
}

export interface LoanDecisionRequest {
    decision: LoanDecision;
    review_note: string;
    version: number;
}

export interface LoanDecisionResponse {
    loan_id: string;
    status: LoanStatus;
    decision: LoanDecision;
    monthly_payment: number;
    maturity_date: string;
    reviewed_at: string;
    version: number;
}

// ---- UC07: Audit Logs ----

export interface AuditLog {
    log_id: string;
    event_type: string;
    entity_type: AuditEntityType;
    entity_id: string;
    actor_user_id: string;
    actor_name: string;
    event_ts: string;
    detail_json: string | Record<string, unknown>;
}

// ---- UC08: Dashboard & Reports ----

export interface TransactionStats {
    total: number;
    approved: number;
    rejected: number;
    manual_review: number;
    pending: number;
    today: number;
    this_week: number;
}

export interface FraudStats {
    avg_fraud_score: number | null;
    rejection_rate: number;
    manual_review_rate: number;
}

export interface CaseStats {
    total_open: number;
    total_assigned: number;
    decided_today: number;
}

export interface LoanStats {
    total_pending: number;
    total_approved: number;
    total_rejected: number;
}

export interface DashboardSummary {
    transactions: TransactionStats;
    fraud: FraudStats;
    cases: CaseStats;
    loans: LoanStats;
    as_of: string;
}

export interface FraudTrendPoint {
    period_label: string;
    period_start: string;
    total_txn: number;
    approved: number;
    rejected: number;
    manual_review: number;
    fraud_rate: number;
}

export interface FraudTrendResponse {
    period: string;
    lookback_days: number;
    data: FraudTrendPoint[];
    as_of: string;
}

export interface TransactionReportEntry {
    txn_id: string;
    customer_id: string;
    merchant_id: string;
    amount: number;
    currency_code: string;
    status: TransactionStatus;
    fraud_score: number;
    txn_time: string;
}

export interface FraudReportEntry {
    date: string;
    total_txn: number;
    approved: number;
    rejected: number;
    manual_review: number;
    fraud_count: number;
    fraud_rate: number;
}

// ---- UC09: ETL ----

export interface EtlJob {
    job_id: string;
    target_date: string;
    job_type: string;
    status: EtlJobStatus;
    records_extracted: number | null;
    records_transformed: number | null;
    records_loaded: number | null;
    started_at: string;
    completed_at: string | null;
    error_message: string | null;
}

export interface TriggerEtlRequest {
    target_date: string;
    job_type: string;
}
