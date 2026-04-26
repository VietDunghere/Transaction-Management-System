import { z } from 'zod';

// ---- Shared ----

const paginationSchema = {
    page: z.number().int().min(1).default(1).catch(1),
    limit: z.number().int().min(1).max(100).default(20).catch(20),
};

// ---- Transactions ----

export const transactionSearchSchema = z.object({
    ...paginationSchema,
    status: z.enum(['PENDING', 'APPROVED', 'REJECTED', 'MANUAL_REVIEW']).optional().catch(undefined),
    merchant_id: z.string().optional().catch(undefined),
    from_date: z.string().optional().catch(undefined),
    to_date: z.string().optional().catch(undefined),
    min_amount: z.number().optional().catch(undefined),
    max_amount: z.number().optional().catch(undefined),
    period: z.enum(['D', 'W', 'M']).optional().catch(undefined),
});
export type TransactionSearchParams = z.infer<typeof transactionSearchSchema>;

// ---- Cases ----

export const caseSearchSchema = z.object({
    ...paginationSchema,
    case_status: z.enum(['OPEN', 'ASSIGNED', 'APPROVED', 'REJECTED', 'CLOSED']).optional().catch(undefined),
    assigned_to: z.string().optional().catch(undefined),
    period: z.enum(['D', 'W', 'M']).optional().catch(undefined),
});
export type CaseSearchParams = z.infer<typeof caseSearchSchema>;

// ---- Users ----

export const userSearchSchema = z.object({
    ...paginationSchema,
    role: z.enum(['OPERATOR', 'REVIEWER', 'ANALYST', 'MANAGER', 'ADMIN']).optional().catch(undefined),
    is_active: z.boolean().optional().catch(undefined),
});
export type UserSearchParams = z.infer<typeof userSearchSchema>;

// ---- Loans ----

export const loanSearchSchema = z.object({
    ...paginationSchema,
    customer_id: z.string().optional().catch(undefined),
    status: z.enum(['PENDING', 'APPROVED', 'REJECTED', 'DISBURSED', 'CLOSED', 'DEFAULTED']).optional().catch(undefined),
    period: z.enum(['D', 'W', 'M']).optional().catch(undefined),
});
export type LoanSearchParams = z.infer<typeof loanSearchSchema>;

// ---- Audit Logs ----

export const auditLogSearchSchema = z.object({
    ...paginationSchema,
    event_type: z.string().optional().catch(undefined),
    entity_type: z.enum(['Transaction', 'User', 'ReviewCase', 'Loan']).optional().catch(undefined),
    actor_user_id: z.string().optional().catch(undefined),
    from_date: z.string().optional().catch(undefined),
    to_date: z.string().optional().catch(undefined),
});
export type AuditLogSearchParams = z.infer<typeof auditLogSearchSchema>;
