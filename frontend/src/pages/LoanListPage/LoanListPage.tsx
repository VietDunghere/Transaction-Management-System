import { useState } from 'react';
import { useNavigate } from '@tanstack/react-router';
import { useLoans } from '~/hooks/useLoans';
import { useDemoRunning } from '~/hooks/useDemoRunning';
import { useAuthStore } from '~/stores/useAuthStore';
import type { LoanSearchParams } from '~/types/searchParams';
import type { LoanStatus, RiskLevel } from '~/types/api';
import { riskLabel } from '~/types/api';
import { PageHeader } from '~/components/templates/PageHeader/PageHeader';
import { ListPageTemplate } from '~/components/templates/ListPageTemplate/ListPageTemplate';
import { TableShell } from '~/components/ui/TableShell/TableShell';
import { FilterBar } from '~/components/ui/FilterBar/FilterBar';
import { Select } from '~/components/ui/Select/Select';
import { QuickDateFilter } from '~/components/ui/QuickDateFilter/QuickDateFilter';
import type { QuickPeriod } from '~/components/ui/QuickDateFilter/QuickDateFilter';
import { Pagination } from '~/components/ui/Pagination/Pagination';
import { Badge } from '~/components/ui/Badge/Badge';
import { Button } from '~/components/ui/Button/Button';
import { LoadingSkeleton } from '~/components/ui/LoadingSkeleton/LoadingSkeleton';
import { ErrorState } from '~/components/ui/ErrorState/ErrorState';
import { EmptyState } from '~/components/ui/EmptyState/EmptyState';

const statusVariant: Record<LoanStatus, 'success' | 'danger' | 'warning' | 'info' | 'muted'> = {
    PENDING: 'info',
    APPROVED: 'success',
    REJECTED: 'danger',
    DISBURSED: 'info',
    CLOSED: 'muted',
    DEFAULTED: 'danger',
};

const riskVariant: Record<RiskLevel, 'success' | 'warning' | 'danger'> = {
    'LOW RISK': 'success',
    'MEDIUM RISK': 'warning',
    'HIGH RISK': 'danger',
};

const statusOptions = [
    { label: 'All Status', value: '' },
    { label: 'Pending', value: 'PENDING' },
    { label: 'Approved', value: 'APPROVED' },
    { label: 'Rejected', value: 'REJECTED' },
    { label: 'Disbursed', value: 'DISBURSED' },
    { label: 'Closed', value: 'CLOSED' },
    { label: 'Defaulted', value: 'DEFAULTED' },
];

const columns = [
    { key: 'loan_id', label: 'Loan ID' },
    { key: 'customer_id', label: 'Customer', width: '180px' },
    { key: 'amount', label: 'Principal', align: 'left' as const, width: '150px' },
    { key: 'term', label: 'Term' },
    { key: 'risk', label: 'Risk Level', width: '150px' },
    { key: 'status', label: 'Status' },
    { key: 'created_at', label: 'Created' },
];

export function LoanListPage() {
    const navigate = useNavigate();
    const userRole = useAuthStore((s) => s.user?.role);

    const [params, setParams] = useState<LoanSearchParams>({
        page: 1,
        limit: 20,
    });

    const demoRunning = useDemoRunning();
    const { data, isLoading, isError, refetch } = useLoans(params, demoRunning ? 1000 : false);

    const rows = (data?.data ?? []).map((loan) => ({
        loan_id: <span className="text-xs font-mono">{loan.loan_id.slice(0, 8)}...</span>,
        customer_id: (
            <span className="text-sm">
                {loan.customer_name ?? (
                    <span className="font-mono text-xs text-text-tertiary">{loan.customer_id.slice(0, 8)}…</span>
                )}
            </span>
        ),
        amount: (
            <span className="text-sm font-medium">
                {loan.principal_amount.toLocaleString()}
            </span>
        ),
        term: <span className="text-sm">{loan.term_months} months</span>,
        risk: loan.risk_level ? (
            <Badge variant={riskVariant[loan.risk_level]}>{riskLabel[loan.risk_level]}</Badge>
        ) : (
            <span className="text-xs text-text-tertiary">—</span>
        ),
        status: <Badge variant={statusVariant[loan.status]}>{loan.status}</Badge>,
        created_at: (
            <span className="text-xs text-text-secondary">{new Date(loan.created_at).toLocaleDateString()}</span>
        ),
    }));

    const totalPages = data ? Math.ceil(data.total / data.limit) : 0;

    return (
        <ListPageTemplate
            header={
                <PageHeader
                    title="Loans"
                    subtitle={data ? `${data.total} total loans` : undefined}
                    actions={
                        userRole === 'OPERATOR' || userRole === 'REVIEWER' ? (
                            <div className="flex gap-2">
                                <Button variant="ghost" onClick={() => navigate({ to: '/loans/simulate' })}>
                                    Simulate
                                </Button>
                                {userRole === 'OPERATOR' && (
                                    <Button onClick={() => navigate({ to: '/loans/create' })}>Create Loan</Button>
                                )}
                            </div>
                        ) : undefined
                    }
                />
            }
            filterBar={
                <FilterBar>
                    <Select
                        options={statusOptions}
                        value={params.status ?? ''}
                        onChange={(e) =>
                            setParams((p) => ({
                                ...p,
                                status: (e.target.value || undefined) as LoanStatus | undefined,
                                page: 1,
                            }))
                        }
                        placeholder="All Status"
                    />
                    <QuickDateFilter
                        value={params.period as QuickPeriod | undefined}
                        onChange={(period) => setParams((p) => ({ ...p, period, page: 1 }))}
                    />
                </FilterBar>
            }
            table={
                isLoading ? (
                    <LoadingSkeleton variant="table" rows={8} />
                ) : isError ? (
                    <ErrorState onRetry={refetch} />
                ) : rows.length === 0 ? (
                    <EmptyState title="No loans found" description="Try adjusting your filters." />
                ) : (
                    <TableShell
                        columns={columns}
                        data={rows}
                        onRowClick={(_row, idx) => {
                            const loan = data!.data[idx];
                            navigate({ to: '/loans/$loanId', params: { loanId: loan.loan_id } });
                        }}
                    />
                )
            }
            pagination={
                totalPages > 1 ? (
                    <Pagination
                        currentPage={params.page}
                        totalPages={totalPages}
                        onPageChange={(page) => setParams((p) => ({ ...p, page }))}
                    />
                ) : undefined
            }
        />
    );
}
