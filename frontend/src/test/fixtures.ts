import type {
    AuditLog,
    CaseDetail,
    CaseListItem,
    DashboardSummary,
    FraudModelPerformance,
    FraudTrendPoint,
    CustomerLoanStats,
    Loan,
    LoanDetail,
    LoanModelPerformance,
    PagedResponse,
    ThresholdListResponse,
    Transaction,
    TransactionDetail,
    TxnStateHistoryItem,
    User,
} from '~/types/api';
import type { DemoEvent, DemoStatus } from '~/services/demoService';

const timestamp = '2025-04-20T08:30:00.000Z';
const createdAt = '2025-04-20T08:45:00.000Z';
const updatedAt = '2025-04-20T09:00:00.000Z';

export function createPagedResponse<T>(data: T[], overrides: Partial<PagedResponse<T>> = {}): PagedResponse<T> {
    return {
        total: overrides.total ?? data.length,
        page: overrides.page ?? 1,
        limit: overrides.limit ?? 20,
        data,
    };
}

export const adminUser = {
    user_id: 'user-admin',
    username: 'admin',
    full_name: 'Admin User',
    email: 'admin@example.com',
    role: 'ADMIN',
    is_active: true,
    created_at: timestamp,
} satisfies User;

export const analystUser = {
    user_id: 'user-analyst',
    username: 'analyst',
    full_name: 'Analyst User',
    email: 'analyst@example.com',
    role: 'ANALYST',
    is_active: true,
    created_at: timestamp,
} satisfies User;

export const reviewerUser = {
    user_id: 'user-reviewer',
    username: 'reviewer',
    full_name: 'Reviewer User',
    email: 'reviewer@example.com',
    role: 'REVIEWER',
    is_active: true,
    created_at: timestamp,
} satisfies User;

export const operatorUser = {
    user_id: 'user-operator',
    username: 'operator',
    full_name: 'Operator User',
    email: 'operator@example.com',
    role: 'OPERATOR',
    is_active: true,
    created_at: timestamp,
} satisfies User;

export const managerUser = {
    user_id: 'user-manager',
    username: 'manager',
    full_name: 'Manager User',
    email: 'manager@example.com',
    role: 'MANAGER',
    is_active: true,
    created_at: timestamp,
} satisfies User;

export const disabledOperatorUser = {
    ...operatorUser,
    user_id: 'user-disabled-operator',
    username: 'disabled.operator',
    full_name: 'Disabled Operator',
    email: 'disabled.operator@example.com',
    is_active: false,
} satisfies User;

export const userListResponse = createPagedResponse<User>([operatorUser, reviewerUser], {
    total: 2,
    page: 1,
    limit: 20,
});

export const dashboardSummary = {
    transactions: {
        total: 1234,
        approved: 1000,
        rejected: 120,
        manual_review: 80,
        pending: 34,
        today: 48,
        this_week: 230,
    },
    fraud: {
        avg_fraud_score: 0.42,
        rejection_rate: 0.12,
        manual_review_rate: 0.08,
    },
    cases: {
        total_open: 12,
        total_assigned: 6,
        decided_today: 3,
    },
    loans: {
        total_pending: 8,
        total_approved: 14,
        total_rejected: 2,
    },
    as_of: updatedAt,
} satisfies DashboardSummary;

export const fraudTrend = [
    {
        period_label: 'Apr 18',
        period_start: '2025-04-18T00:00:00.000Z',
        total_txn: 100,
        approved: 84,
        rejected: 10,
        manual_review: 6,
        fraud_rate: 0.16,
    },
    {
        period_label: 'Apr 19',
        period_start: '2025-04-19T00:00:00.000Z',
        total_txn: 120,
        approved: 98,
        rejected: 13,
        manual_review: 9,
        fraud_rate: 0.18,
    },
    {
        period_label: 'Apr 20',
        period_start: '2025-04-20T00:00:00.000Z',
        total_txn: 140,
        approved: 115,
        rejected: 15,
        manual_review: 10,
        fraud_rate: 0.18,
    },
] satisfies FraudTrendPoint[];

export const thresholds = {
    fraud: [
        {
            model_name: 'fraud',
            param_name: 'reject_threshold',
            param_value: 0.67,
            description: 'Reject when fraud score crosses this value',
            updated_by: 'analyst.user',
            updated_at: updatedAt,
            version: 3,
        },
        {
            model_name: 'fraud',
            param_name: 'review_threshold',
            param_value: 0.35,
            description: 'Send to manual review above this level',
            updated_by: 'analyst.user',
            updated_at: updatedAt,
            version: 3,
        },
    ],
    loan: [
        {
            model_name: 'loan',
            param_name: 'high_risk_threshold',
            param_value: 0.72,
            description: 'High risk cutoff',
            updated_by: 'manager.user',
            updated_at: updatedAt,
            version: 4,
        },
        {
            model_name: 'loan',
            param_name: 'medium_risk_threshold',
            param_value: 0.48,
            description: 'Medium risk cutoff',
            updated_by: 'manager.user',
            updated_at: updatedAt,
            version: 4,
        },
    ],
} satisfies ThresholdListResponse;

export const fraudPerformance = {
    period_days: 30,
    score_distribution: {
        approved_count: 84,
        review_count: 9,
        rejected_count: 7,
        total: 100,
        approved_rate: 0.84,
        review_rate: 0.09,
        rejected_rate: 0.07,
        false_positive_count: 3,
        false_positive_rate: 0.03,
    },
    current_thresholds: {
        reject_threshold: 0.67,
        review_threshold: 0.35,
    },
} satisfies FraudModelPerformance;

export const loanPerformance = {
    period_days: 30,
    risk_distribution: {
        low_risk_count: 60,
        medium_risk_count: 25,
        high_risk_count: 15,
        total: 100,
        low_risk_rate: 0.6,
        medium_risk_rate: 0.25,
        high_risk_rate: 0.15,
        approved_count: 52,
        rejected_count: 18,
        pending_count: 30,
    },
    current_thresholds: {
        high_risk_threshold: 0.72,
        medium_risk_threshold: 0.48,
    },
} satisfies LoanModelPerformance;

export const transactionListItem = {
    txn_id: 'txn-001',
    customer_id: 'cust-001',
    merchant_id: 'mer-001',
    amount: 12500,
    currency_code: 'USD',
    status: 'MANUAL_REVIEW',
    fraud_score: 0.62,
    txn_time: timestamp,
    created_at: createdAt,
} satisfies Transaction;

export const transactionDetail = {
    ...transactionListItem,
    card_number_masked: '4111********1111',
    reason_code: 'velocity_spike',
    source_ip: '203.0.113.10',
    updated_at: updatedAt,
} satisfies TransactionDetail;

export const transactionStates = [
    {
        state_hist_id: 'state-001',
        txn_id: 'txn-001',
        old_status: null,
        new_status: 'PENDING',
        changed_by_user_id: null,
        changed_at: timestamp,
        change_reason: 'Submitted',
    },
    {
        state_hist_id: 'state-002',
        txn_id: 'txn-001',
        old_status: 'PENDING',
        new_status: 'MANUAL_REVIEW',
        changed_by_user_id: 'user-reviewer',
        changed_at: updatedAt,
        change_reason: 'Fraud rule hit',
    },
] satisfies TxnStateHistoryItem[];

export const transactionListResponse = createPagedResponse<Transaction>([transactionListItem], {
    total: 1,
    page: 1,
    limit: 20,
});

export const transactionSubmitResponse = {
    txn_id: 'txn-900',
    status: 'APPROVED',
    fraud_score: 0.12,
} as const;

export const caseListItem = {
    case_id: 'case-001',
    txn_id: 'txn-001',
    case_status: 'OPEN',
    assigned_to: null,
    assigned_to_name: null,
    fraud_score: 0.62,
    amount: 12500,
    txn_time: timestamp,
    created_at: createdAt,
} satisfies CaseListItem;

export const caseDetail = {
    case_id: 'case-001',
    txn_id: 'txn-001',
    case_status: 'OPEN',
    assigned_to: null,
    assigned_to_name: null,
    decision: null,
    decision_note: null,
    version: 4,
    transaction: {
        txn_id: 'txn-001',
        amount: 12500,
        currency_code: 'USD',
        fraud_score: 0.72,
        txn_time: timestamp,
        customer_name: 'Alice Johnson',
        merchant_name: 'Metro Market',
        merchant_category: 'Retail',
        merchant_risk_level: 'HIGH',
        channel_name: 'POS',
        source_ip: '203.0.113.15',
        card_number_masked: '4111********1111',
        rule_hits: [
            {
                rule_code: 'R-01',
                rule_name: 'Velocity Spike',
                hit_value: '7 txns / 5m',
                severity: 'HIGH',
            },
        ],
        card_velocity: {
            avg_daily_txn: 7.5,
            total_txn: 42,
            avg_amt: 180.5,
            std_amt: 25.2,
        },
        recent_transactions: [
            {
                txn_id: 'txn-002',
                amount: 220,
                currency_code: 'USD',
                merchant_name: 'Coffee Bar',
                status: 'APPROVED',
                fraud_score: 0.12,
                txn_time: '2025-04-19T10:00:00.000Z',
            },
        ],
    },
    created_at: createdAt,
    decided_at: null,
} satisfies CaseDetail;

export const caseListResponse = createPagedResponse<CaseListItem>([caseListItem], {
    total: 1,
    page: 1,
    limit: 20,
});

export const caseDecisionResponse = {
    case_id: 'case-001',
    txn_id: 'txn-001',
    case_status: 'APPROVED',
    decision: 'APPROVE',
    decided_at: updatedAt,
    version: 5,
} as const;

export const assignCaseResponse = {
    case_id: 'case-001',
    case_status: 'ASSIGNED',
    assigned_to: reviewerUser.user_id,
    created_at: createdAt,
} as const;

export const loanListItem = {
    loan_id: 'loan-001',
    customer_id: 'cust-001',
    customer_name: 'Alice Johnson',
    status: 'PENDING',
    principal_amount: 250000,
    currency_code: 'USD',
    interest_rate: 12.5,
    term_months: 24,
    pd_score: 0.18,
    risk_level: 'LOW RISK',
    created_at: createdAt,
} satisfies Loan;

export const loanDetail = {
    loan_id: 'loan-001',
    customer_id: 'cust-001',
    customer_name: 'Alice Johnson',
    status: 'PENDING',
    principal_amount: 250000,
    currency_code: 'USD',
    interest_rate: 12.5,
    term_months: 24,
    pd_score: 0.18,
    risk_level: 'LOW RISK',
    created_at: createdAt,
    purpose: 'Debt Consolidation',
    monthly_payment: 11876,
    maturity_date: '2027-04-20T00:00:00.000Z',
    reviewed_by: null,
    reviewed_at: null,
    version: 1,
    customer_job: 'Engineer',
    customer_kyc_status: 'VERIFIED',
    customer_income_level: 'High',
    customer_loan_stats: {
        total_loans: 3,
        approved: 2,
        rejected: 1,
        active: 1,
    } satisfies CustomerLoanStats,
    person_age: 34,
    person_income: 120000,
    person_home_ownership: 'OWN',
    person_emp_length: 8,
    loan_grade: 'B',
    loan_intent: 'DEBTCONSOLIDATION',
    cb_person_default_on_file: 'N',
    cb_person_cred_hist_length: 12,
} satisfies LoanDetail;

export const loanListResponse = createPagedResponse<Loan>([loanListItem], {
    total: 1,
    page: 1,
    limit: 20,
});

export const loanCreateResponse = {
    loan_id: 'loan-900',
} as const;

export const loanDecisionResponse = {
    loan_id: 'loan-001',
    status: 'APPROVED',
    monthly_payment: 11876,
    maturity_date: '2027-04-20T00:00:00.000Z',
    reviewed_at: updatedAt,
    version: 2,
} as const;

export const loanSimulationResponse = {
    pd_score: 0.22,
    risk_level: 'LOW RISK',
    decision: 'APPROVE',
    confidence: 0.93,
} as const;

export const auditLogListItem = {
    log_id: 'log-001',
    event_type: 'USER_ROLE_UPDATED',
    entity_type: 'User',
    entity_id: 'user-operator',
    actor_user_id: 'user-admin',
    actor_name: 'Admin User',
    event_ts: updatedAt,
    detail: {
        before: 'OPERATOR',
        after: 'REVIEWER',
        reason: 'Promotion',
    },
} satisfies AuditLog;

export const auditLogDetail = {
    ...auditLogListItem,
    event_type: 'CASE_ASSIGNED',
    entity_type: 'ReviewCase',
    entity_id: 'case-001',
    detail: {
        assigned_to: reviewerUser.user_id,
        note: 'Manual triage required',
    },
} satisfies AuditLog;

export const auditLogListResponse = createPagedResponse<AuditLog>([auditLogListItem], {
    total: 1,
    page: 1,
    limit: 20,
});

export const demoEvents = [
    {
        seq: 1,
        type: 'TXN',
        result: 'APPROVED',
        score: 0.12,
        amount: 2500,
        info: 'Low risk transaction',
        timestamp: timestamp,
    },
    {
        seq: 2,
        type: 'LOAN',
        result: 'MANUAL_REVIEW',
        score: 0.51,
        amount: 100000,
        info: 'Medium risk loan',
        timestamp: updatedAt,
    },
] satisfies DemoEvent[];

export const demoStatusStopped = {
    running: false,
    started_by: null,
    started_at: null,
    config: null,
    sent: 0,
    stats: {
        TXN_APPROVED: 0,
        TXN_REJECTED: 0,
        TXN_MANUAL_REVIEW: 0,
        LOAN_PENDING: 0,
        ERROR: 0,
    },
    recent_events: [],
} satisfies DemoStatus;

export const demoStatusRunning = {
    running: true,
    started_by: adminUser.username,
    started_at: updatedAt,
    config: {
        rate: 2,
        count: 50,
        loan_pct: 20,
    },
    sent: 2,
    stats: {
        TXN_APPROVED: 1,
        TXN_REJECTED: 0,
        TXN_MANUAL_REVIEW: 1,
        LOAN_PENDING: 1,
        ERROR: 0,
    },
    recent_events: demoEvents,
} satisfies DemoStatus;
