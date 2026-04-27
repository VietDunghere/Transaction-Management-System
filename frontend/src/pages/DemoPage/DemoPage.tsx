import { useState, useEffect, useRef, useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Play, Square, Loader2 } from 'lucide-react';
import { toast } from 'sonner';

import { PageHeader } from '~/components/templates/PageHeader/PageHeader';
import { Card } from '~/components/ui/Card/Card';
import { Button } from '~/components/ui/Button/Button';
import { Badge } from '~/components/ui/Badge/Badge';
import { StatCard } from '~/components/ui/StatCard/StatCard';
import { SectionHeader } from '~/components/ui/SectionHeader/SectionHeader';
import { TableShell } from '~/components/ui/TableShell/TableShell';

import { demoService } from '~/services/demoService';
import type { DemoStartConfig, DemoStatus, DemoEvent } from '~/services/demoService';

const RESULT_BADGE: Record<string, 'success' | 'danger' | 'warning' | 'info' | 'muted'> = {
    APPROVED: 'success',
    REJECTED: 'danger',
    MANUAL_REVIEW: 'warning',
    PENDING: 'info',
    ERROR: 'danger',
};

const EVENT_COLUMNS = [
    { key: 'seq', label: '#', width: '60px', align: 'right' as const },
    { key: 'type', label: 'Type', width: '80px' },
    { key: 'result', label: 'Result', width: '140px' },
    { key: 'score', label: 'Score', width: '100px', align: 'right' as const },
    { key: 'amount', label: 'Amount', width: '120px', align: 'right' as const },
    { key: 'info', label: 'Info' },
];

function formatScore(score: number | null): string {
    return score != null ? score.toFixed(4) : '—';
}

function formatAmount(amount: number): string {
    return amount.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function eventToRow(e: DemoEvent) {
    return {
        seq: <span className="text-text-secondary text-sm">{e.seq}</span>,
        type: (
            <Badge variant={e.type === 'LOAN' ? 'info' : 'muted'} className="text-xs">
                {e.type}
            </Badge>
        ),
        result: (
            <Badge variant={RESULT_BADGE[e.result] ?? 'muted'} dot>
                {e.result}
            </Badge>
        ),
        score: <span className="font-mono text-sm">{formatScore(e.score)}</span>,
        amount: <span className="font-mono text-sm">${formatAmount(e.amount)}</span>,
        info: <span className="text-sm text-text-secondary truncate max-w-50 inline-block">{e.info}</span>,
    };
}

export function DemoPage() {
    const queryClient = useQueryClient();
    const tableRef = useRef<HTMLDivElement>(null);

    // ── Config state ──
    const [rate, setRate] = useState(1);
    const [count, setCount] = useState<string>('');
    const [loanPct, setLoanPct] = useState(20);

    // ── Polling: enabled only when running ──
    const [polling, setPolling] = useState(false);

    const { data: status } = useQuery<DemoStatus>({
        queryKey: ['demo', 'status'],
        queryFn: () => demoService.getStatus(),
        refetchInterval: polling ? 1000 : false,
        refetchIntervalInBackground: true,
    });

    const isRunning = status?.running ?? false;

    // Sync polling state with server running state
    useEffect(() => {
        if (status) setPolling(status.running);
    }, [status]);

    // Auto-scroll event table to top when new events arrive
    useEffect(() => {
        if (tableRef.current) {
            tableRef.current.scrollTop = 0;
        }
    }, [status?.sent]);

    // ── Mutations ──
    const startMut = useMutation({
        mutationFn: (config: DemoStartConfig) => demoService.start(config),
        onSuccess: () => {
            setPolling(true);
            queryClient.invalidateQueries({ queryKey: ['demo', 'status'] });
            toast.success('Demo started');
        },
        onError: (err: { response?: { status?: number; data?: { message?: string } } }) => {
            if (err.response?.status === 409) {
                toast.error('Demo is already running');
                setPolling(true);
            } else {
                toast.error(err.response?.data?.message ?? 'Failed to start demo');
            }
        },
    });

    const stopMut = useMutation({
        mutationFn: () => demoService.stop(),
        onSuccess: () => {
            setPolling(false);
            queryClient.invalidateQueries({ queryKey: ['demo', 'status'] });
            toast.success('Demo stopped');
        },
        onError: () => toast.error('Failed to stop demo'),
    });

    const handleStart = useCallback(() => {
        const parsedCount = count.trim() === '' ? null : parseInt(count, 10);
        if (parsedCount !== null && (isNaN(parsedCount) || parsedCount < 1)) {
            toast.error('Count must be a positive number or empty for unlimited');
            return;
        }
        startMut.mutate({ rate, count: parsedCount, loan_pct: loanPct });
    }, [rate, count, loanPct, startMut]);

    const handleStop = useCallback(() => {
        stopMut.mutate();
    }, [stopMut]);

    // ── Stats ──
    const stats = status?.stats ?? {};
    const sent = status?.sent ?? 0;
    const events = status?.recent_events ?? [];
    const reversedEvents = [...events].reverse();

    return (
        <div className="flex flex-col gap-6">
            <PageHeader title="Demo Runner" subtitle="Generate fake transactions and loans for testing" />

            {/* Config / Control Card */}
            <Card>
                <div className="flex flex-col gap-6">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <SectionHeader title={isRunning ? 'Running' : 'Configuration'} />
                            {isRunning && (
                                <Badge variant="success" dot>
                                    Live — {status?.started_by}
                                </Badge>
                            )}
                        </div>
                        {isRunning ? (
                            <Button
                                variant="danger"
                                icon={<Square size={16} />}
                                onClick={handleStop}
                                loading={stopMut.isPending}
                            >
                                Stop Demo
                            </Button>
                        ) : (
                            <Button icon={<Play size={16} />} onClick={handleStart} loading={startMut.isPending}>
                                Start Demo
                            </Button>
                        )}
                    </div>

                    {/* Config form — always visible, disabled when running */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div className="flex flex-col gap-2">
                            <label className="text-sm font-medium text-text-secondary">Rate (req/s): {rate}</label>
                            <input
                                type="range"
                                min={0.5}
                                max={10}
                                step={0.5}
                                value={rate}
                                onChange={(e) => setRate(parseFloat(e.target.value))}
                                disabled={isRunning}
                                className="w-full accent-text-primary"
                            />
                            <div className="flex justify-between text-xs text-text-secondary">
                                <span>0.5</span>
                                <span>10</span>
                            </div>
                        </div>

                        <div className="flex flex-col gap-2">
                            <label className="text-sm font-medium text-text-secondary">Count (empty = unlimited)</label>
                            <input
                                type="number"
                                min={1}
                                max={10000}
                                value={count}
                                onChange={(e) => setCount(e.target.value)}
                                disabled={isRunning}
                                placeholder="Unlimited"
                                className="w-full rounded-lg border border-border-default bg-primary px-4 py-2.5 text-sm text-text-primary placeholder:text-text-secondary focus:outline-none focus:ring-1 focus:ring-text-primary disabled:opacity-50"
                            />
                        </div>

                        <div className="flex flex-col gap-2">
                            <label className="text-sm font-medium text-text-secondary">Loan %: {loanPct}%</label>
                            <input
                                type="range"
                                min={0}
                                max={100}
                                step={5}
                                value={loanPct}
                                onChange={(e) => setLoanPct(parseInt(e.target.value, 10))}
                                disabled={isRunning}
                                className="w-full accent-text-primary"
                            />
                            <div className="flex justify-between text-xs text-text-secondary">
                                <span>0% (all TXN)</span>
                                <span>100% (all Loan)</span>
                            </div>
                        </div>
                    </div>
                </div>
            </Card>

            {/* Stats Row */}
            <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
                <StatCard label="Sent" value={sent.toLocaleString()} accent="purple" />
                <StatCard label="Approved" value={(stats.TXN_APPROVED ?? 0).toLocaleString()} accent="blue" />
                <StatCard label="Rejected" value={(stats.TXN_REJECTED ?? 0).toLocaleString()} accent="purple" />
                <StatCard label="Review" value={(stats.TXN_MANUAL_REVIEW ?? 0).toLocaleString()} accent="blue" />
                <StatCard label="Loans" value={(stats.LOAN_PENDING ?? 0).toLocaleString()} accent="purple" />
                <StatCard label="Errors" value={(stats.ERROR ?? 0).toLocaleString()} accent="blue" />
            </div>

            {/* Event Log */}
            <Card noPadding>
                <div className="px-8 pt-6 pb-2 flex items-center justify-between">
                    <SectionHeader title="Recent Events" />
                    {isRunning && (
                        <div className="flex items-center gap-2 text-sm text-text-secondary">
                            <Loader2 size={14} className="animate-spin" />
                            Polling every 1s
                        </div>
                    )}
                </div>
                <div ref={tableRef} className="max-h-[480px] overflow-y-auto">
                    {reversedEvents.length > 0 ? (
                        <TableShell columns={EVENT_COLUMNS} data={reversedEvents.map(eventToRow)} />
                    ) : (
                        <div className="px-8 py-12 text-center text-text-secondary text-sm">
                            No events yet. Start the demo to generate data.
                        </div>
                    )}
                </div>
            </Card>
        </div>
    );
}
