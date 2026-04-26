// ---- Enums / Literals ----

export type Role = 'OPERATOR' | 'REVIEWER' | 'ANALYST' | 'MANAGER' | 'ADMIN';

export type TransactionStatus = 'PENDING' | 'APPROVED' | 'REJECTED' | 'MANUAL_REVIEW';

export type CaseStatus = 'OPEN' | 'ASSIGNED' | 'APPROVED' | 'REJECTED' | 'CLOSED';

export type CaseDecision = 'APPROVE' | 'REJECT';

export type LoanStatus = 'PENDING' | 'APPROVED' | 'REJECTED' | 'DISBURSED' | 'CLOSED' | 'DEFAULTED';

export type LoanDecision = 'APPROVE' | 'REJECT';

export type RiskLevel = 'LOW RISK' | 'MEDIUM RISK' | 'HIGH RISK';

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

export interface TxnStateHistoryItem {
    state_hist_id: string;
    txn_id: string;
    old_status: string | null;
    new_status: string;
    changed_by_user_id: string | null;
    changed_at: string;
    change_reason: string | null;
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
    assigned_to_name: string | null;
    fraud_score: number | null;
    amount: number | null;
    txn_time: string | null;
    created_at: string;
}

export interface CaseRuleHit {
    rule_code: string;
    rule_name: string | null;
    hit_value: string | null;
    severity: string | null;
}

export interface CaseDetail {
    case_id: string;
    txn_id: string;
    case_status: CaseStatus;
    assigned_to: string | null;
    assigned_to_name: string | null;
    decision: CaseDecision | null;
    decision_note: string | null;
    version: number;
    transaction: {
        txn_id: string;
        amount: number;
        currency_code: string;
        fraud_score: number | null;
        txn_time: string;
        customer_name: string | null;
        merchant_name: string | null;
        merchant_category: string | null;
        merchant_risk_level: string | null;
        channel_name: string | null;
        source_ip: string | null;
        card_number_masked: string | null;
        rule_hits: CaseRuleHit[];
        card_velocity: {
            avg_daily_txn: number;
            total_txn: number;
            avg_amt: number;
            std_amt: number;
        } | null;
        recent_transactions: {
            txn_id: string;
            amount: number;
            currency_code: string;
            merchant_name: string | null;
            status: string;
            fraud_score: number | null;
            txn_time: string;
        }[];
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
    customer_name: string | null;
    status: LoanStatus;
    principal_amount: number;
    currency_code: string;
    interest_rate: number;
    term_months: number;
    pd_score: number | null;
    risk_level: RiskLevel | null;
    created_at: string;
}

export interface CustomerLoanStats {
    total_loans: number;
    approved: number;
    rejected: number;
    active: number;
}

export interface LoanDetail extends Loan {
    purpose: string;
    monthly_payment: number | null;
    maturity_date: string | null;
    reviewed_by: string | null;
    reviewed_at: string | null;
    // Customer info
    customer_name: string | null;
    customer_job: string | null;
    customer_kyc_status: string | null;
    customer_income_level: string | null;
    customer_loan_stats: CustomerLoanStats | null;
    // Applicant profile for reviewer context
    person_age: number | null;
    person_income: number | null;
    person_home_ownership: string | null;
    person_emp_length: number | null;
    loan_grade: string | null;
    loan_intent: string | null;
    cb_person_default_on_file: string | null;
    cb_person_cred_hist_length: number | null;
}

export interface LoanDecisionRequest {
    decision: LoanDecision;
    review_note: string;
    version: number;
}

export interface LoanDecisionResponse {
    loan_id: string;
    status: LoanStatus;
    monthly_payment: number | null;
    maturity_date: string | null;
    reviewed_at: string | null;
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

// ---- Analyst: Thresholds ----

export interface ThresholdItem {
    model_name: string;
    param_name: string;
    param_value: number;
    description: string | null;
    updated_by: string | null;
    updated_at: string;
    version: number;
}

export interface ThresholdListResponse {
    fraud: ThresholdItem[];
    loan: ThresholdItem[];
}

export interface ThresholdUpdateItem {
    model_name: 'fraud' | 'loan';
    param_name: string;
    param_value: number;
}

export interface ThresholdUpdateRequest {
    updates: ThresholdUpdateItem[];
}

// ---- Analyst: Model Performance ----

export interface FraudScoreDistribution {
    approved_count: number;
    review_count: number;
    rejected_count: number;
    total: number;
    approved_rate: number;
    review_rate: number;
    rejected_rate: number;
    false_positive_count: number;
    false_positive_rate: number;
}

export interface FraudModelPerformance {
    period_days: number;
    score_distribution: FraudScoreDistribution;
    current_thresholds: Record<string, number>;
}

export interface LoanRiskDistribution {
    low_risk_count: number;
    medium_risk_count: number;
    high_risk_count: number;
    total: number;
    low_risk_rate: number;
    medium_risk_rate: number;
    high_risk_rate: number;
    approved_count: number;
    rejected_count: number;
    pending_count: number;
}

export interface LoanModelPerformance {
    period_days: number;
    risk_distribution: LoanRiskDistribution;
    current_thresholds: Record<string, number>;
}
