import { useState } from 'react';
import { AlertTriangle, CheckCircle, Plus, TrendingUp } from 'lucide-react';

import {
    Button,
    Input,
    Select,
    Textarea,
    Badge,
    Card,
    Modal,
    TableShell,
    StatCard,
    KeyValueRow,
    TimelineItem,
    SectionHeader,
    SearchBox,
    FilterBar,
    DateRangeShell,
    Pagination,
    LoadingSkeleton,
    EmptyState,
    ErrorState,
} from '~/components/ui';

import { PageHeader, ListPageTemplate, DashboardTemplate } from '~/components/templates';

/* ============================================================
   UI Demo Page — Internal showcase of all components
   ============================================================ */

export function UIDemoPage() {
    const [modalOpen, setModalOpen] = useState(false);
    const [currentPage, setCurrentPage] = useState(3);
    const [searchTerm, setSearchTerm] = useState('');

    return (
        <div className="max-w-4xl mx-auto space-y-16">
            <PageHeader title="UI Component Library" subtitle="Internal demo — all Huza Fraud reusable components" />

            {/* ===================== SECTION: Primitives ===================== */}
            <section>
                <SectionHeader title="1. Primitive Components" />

                {/* Buttons */}
                <Card className="mb-6">
                    <h3 className="text-sm font-semibold mb-4">Buttons</h3>
                    <div className="flex flex-wrap gap-3">
                        <Button variant="primary">Primary</Button>
                        <Button variant="secondary">Secondary</Button>
                        <Button variant="danger">Danger</Button>
                        <Button variant="ghost">Ghost</Button>
                        <Button variant="primary" icon={<Plus size={14} />}>
                            With Icon
                        </Button>
                        <Button variant="primary" loading>
                            Loading
                        </Button>
                        <Button variant="primary" disabled>
                            Disabled
                        </Button>
                    </div>
                    <div className="flex flex-wrap gap-3 mt-3">
                        <Button variant="primary" size="sm">
                            Small
                        </Button>
                        <Button variant="primary" size="md">
                            Medium
                        </Button>
                        <Button variant="primary" size="lg">
                            Large
                        </Button>
                    </div>
                </Card>

                {/* Form Inputs */}
                <Card className="mb-6">
                    <h3 className="text-sm font-semibold mb-4">Form Inputs</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <Input label="Username" placeholder="Enter username" />
                        <Input label="Email" placeholder="user@example.com" hint="We'll never share your email." />
                        <Input
                            label="Password"
                            type="password"
                            placeholder="••••••••"
                            error="Password must be at least 8 characters"
                        />
                        <Input label="Disabled" placeholder="Cannot edit" disabled />
                        <Select
                            label="Risk Level"
                            placeholder="Select risk level"
                            options={[
                                { label: 'Low', value: 'low' },
                                { label: 'Medium', value: 'medium' },
                                { label: 'High', value: 'high' },
                                { label: 'Critical', value: 'critical' },
                            ]}
                        />
                        <Select label="Disabled Select" options={[{ label: 'Option A', value: 'a' }]} disabled />
                    </div>
                    <div className="mt-4">
                        <Textarea
                            label="Notes"
                            placeholder="Enter investigation notes..."
                            hint="Markdown is supported."
                        />
                    </div>
                </Card>

                {/* Badges */}
                <Card className="mb-6">
                    <h3 className="text-sm font-semibold mb-4">Badges / Status Chips</h3>
                    <div className="flex flex-wrap gap-3">
                        <Badge variant="default">Default</Badge>
                        <Badge variant="success" dot>
                            Approved
                        </Badge>
                        <Badge variant="warning" dot>
                            Pending
                        </Badge>
                        <Badge variant="danger" dot>
                            Rejected
                        </Badge>
                        <Badge variant="info" dot>
                            Assigned
                        </Badge>
                        <Badge variant="muted">Archived</Badge>
                    </div>
                </Card>

                {/* Modal */}
                <Card>
                    <h3 className="text-sm font-semibold mb-4">Modal</h3>
                    <Button variant="secondary" onClick={() => setModalOpen(true)}>
                        Open Modal
                    </Button>
                    <Modal
                        isOpen={modalOpen}
                        onClose={() => setModalOpen(false)}
                        title="Confirm Action"
                        footer={
                            <>
                                <Button variant="ghost" onClick={() => setModalOpen(false)}>
                                    Cancel
                                </Button>
                                <Button variant="danger" onClick={() => setModalOpen(false)}>
                                    Confirm
                                </Button>
                            </>
                        }
                    >
                        <p className="text-base text-text-secondary">
                            Are you sure you want to reject this transaction? This action cannot be undone.
                        </p>
                    </Modal>
                </Card>
            </section>

            {/* ===================== SECTION: Data Display ===================== */}
            <section>
                <SectionHeader title="2. Data Display Components" />

                {/* StatCards */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                    <StatCard
                        label="Total Transactions"
                        value="12,847"
                        change="+12.5%"
                        changeType="positive"
                        accent="purple"
                    />
                    <StatCard label="Flagged Cases" value="234" change="+3.2%" changeType="negative" accent="blue" />
                    <StatCard label="Revenue" value="$1.2M" change="+8.1%" changeType="positive" accent="purple" />
                    <StatCard
                        label="Active Users"
                        value="1,024"
                        change="No change"
                        changeType="neutral"
                        accent="blue"
                    />
                </div>

                {/* Table */}
                <Card noPadding className="mb-6">
                    <TableShell
                        columns={[
                            { key: 'id', label: 'ID', width: '80px' },
                            { key: 'user', label: 'User' },
                            { key: 'amount', label: 'Amount', align: 'right' },
                            { key: 'status', label: 'Status', align: 'center' },
                            { key: 'date', label: 'Date' },
                        ]}
                        data={[
                            {
                                id: 'TXN-001',
                                user: 'Nguyen Van A',
                                amount: '$1,200.00',
                                status: (
                                    <Badge variant="success" dot>
                                        Approved
                                    </Badge>
                                ),
                                date: '2026-04-15',
                            },
                            {
                                id: 'TXN-002',
                                user: 'Tran Thi B',
                                amount: '$450.00',
                                status: (
                                    <Badge variant="warning" dot>
                                        Pending
                                    </Badge>
                                ),
                                date: '2026-04-15',
                            },
                            {
                                id: 'TXN-003',
                                user: 'Le Van C',
                                amount: '$8,900.00',
                                status: (
                                    <Badge variant="danger" dot>
                                        Flagged
                                    </Badge>
                                ),
                                date: '2026-04-14',
                            },
                            {
                                id: 'TXN-004',
                                user: 'Pham Thi D',
                                amount: '$320.00',
                                status: (
                                    <Badge variant="success" dot>
                                        Approved
                                    </Badge>
                                ),
                                date: '2026-04-14',
                            },
                            {
                                id: 'TXN-005',
                                user: 'Hoang Van E',
                                amount: '$15,000.00',
                                status: (
                                    <Badge variant="danger" dot>
                                        Rejected
                                    </Badge>
                                ),
                                date: '2026-04-13',
                            },
                        ]}
                    />
                </Card>

                {/* KeyValueRows */}
                <Card className="mb-6">
                    <SectionHeader title="Transaction Details" />
                    <KeyValueRow label="Transaction ID" value="TXN-2026-04-15-001" />
                    <KeyValueRow label="Sender" value="Nguyen Van A" />
                    <KeyValueRow label="Receiver" value="Company XYZ Ltd." />
                    <KeyValueRow label="Amount" value={<span className="font-semibold">$12,500.00</span>} />
                    <KeyValueRow label="Risk Score" value={<Badge variant="danger">92 / 100</Badge>} />
                    <KeyValueRow
                        label="Status"
                        value={
                            <Badge variant="warning" dot>
                                Under Review
                            </Badge>
                        }
                    />
                </Card>

                {/* Timeline */}
                <Card>
                    <SectionHeader title="Activity Timeline" />
                    <TimelineItem
                        title="Transaction created"
                        description="Transaction TXN-001 submitted by Nguyen Van A."
                        timestamp="Apr 15, 2026 — 09:30 AM"
                        variant="default"
                    />
                    <TimelineItem
                        title="Fraud alert triggered"
                        description="Risk score exceeded threshold (92/100). Auto-flagged by system."
                        timestamp="Apr 15, 2026 — 09:31 AM"
                        variant="warning"
                        icon={<AlertTriangle size={12} />}
                    />
                    <TimelineItem
                        title="Case assigned"
                        description="Assigned to analyst Tran Thi B for manual review."
                        timestamp="Apr 15, 2026 — 10:15 AM"
                        variant="default"
                    />
                    <TimelineItem
                        title="Investigation completed"
                        description="Confirmed legitimate transaction. Case closed."
                        timestamp="Apr 15, 2026 — 02:45 PM"
                        variant="success"
                        icon={<CheckCircle size={12} />}
                    />
                </Card>
            </section>

            {/* ===================== SECTION: Navigation & Filter ===================== */}
            <section>
                <SectionHeader title="3. Navigation & Filter Components" />

                <Card className="mb-6">
                    <FilterBar>
                        <SearchBox
                            value={searchTerm}
                            onChange={setSearchTerm}
                            placeholder="Search transactions..."
                            className="w-full sm:w-64"
                        />
                        <Select
                            label="Status"
                            options={[
                                { label: 'All', value: 'all' },
                                { label: 'Approved', value: 'approved' },
                                { label: 'Pending', value: 'pending' },
                                { label: 'Rejected', value: 'rejected' },
                            ]}
                        />
                        <Select
                            label="Risk Level"
                            options={[
                                { label: 'All', value: 'all' },
                                { label: 'Low', value: 'low' },
                                { label: 'Medium', value: 'medium' },
                                { label: 'High', value: 'high' },
                            ]}
                        />
                        <DateRangeShell />
                        <Button variant="primary" size="sm" icon={<TrendingUp size={12} />}>
                            Apply
                        </Button>
                    </FilterBar>
                </Card>

                <Card>
                    <h3 className="text-sm font-semibold mb-4">Pagination</h3>
                    <Pagination currentPage={currentPage} totalPages={12} onPageChange={setCurrentPage} />
                </Card>
            </section>

            {/* ===================== SECTION: State Components ===================== */}
            <section>
                <SectionHeader title="4. State Components" />

                <h3 className="text-sm font-semibold mb-4">Loading Skeletons</h3>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
                    <div>
                        <p className="text-xs text-text-secondary mb-3">Table variant</p>
                        <LoadingSkeleton variant="table" rows={3} />
                    </div>
                    <div>
                        <p className="text-xs text-text-secondary mb-3">Chart variant</p>
                        <LoadingSkeleton variant="chart" />
                    </div>
                    <div>
                        <p className="text-xs text-text-secondary mb-3">Card variant</p>
                        <LoadingSkeleton variant="card" />
                    </div>
                    <div>
                        <p className="text-xs text-text-secondary mb-3">Form variant</p>
                        <LoadingSkeleton variant="form" rows={3} />
                    </div>
                </div>

                <h3 className="text-sm font-semibold mb-4">Empty States</h3>
                <Card className="mb-6">
                    <EmptyState
                        title="No transactions found"
                        description="There are no transactions matching your filter criteria. Try adjusting your search or clear filters."
                        action={
                            <Button variant="secondary" size="sm">
                                Clear Filters
                            </Button>
                        }
                    />
                </Card>

                <h3 className="text-sm font-semibold mb-4">Error States</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <ErrorState type="network" onRetry={() => alert('Retry clicked')} />
                    <ErrorState type="unauthorized" />
                    <ErrorState type="unknown" onRetry={() => alert('Retry clicked')} />
                </div>
            </section>

            {/* ===================== SECTION: Page Templates ===================== */}
            <section>
                <SectionHeader title="5. Page Template Previews" />

                <div className="space-y-6">
                    <Card>
                        <h3 className="text-sm font-semibold mb-4">Dashboard Template</h3>
                        <div className="border border-dashed border-border-default p-4 rounded-lg">
                            <DashboardTemplate
                                header={<PageHeader title="Dashboard Overview" subtitle="Real-time fraud monitoring" />}
                                kpiRow={
                                    <>
                                        <StatCard
                                            label="Total Txn"
                                            value="12.8K"
                                            change="+12%"
                                            changeType="positive"
                                            accent="purple"
                                        />
                                        <StatCard
                                            label="Flagged"
                                            value="234"
                                            change="+3%"
                                            changeType="negative"
                                            accent="blue"
                                        />
                                        <StatCard
                                            label="Revenue"
                                            value="$1.2M"
                                            change="+8%"
                                            changeType="positive"
                                            accent="purple"
                                        />
                                        <StatCard
                                            label="Users"
                                            value="1,024"
                                            change="0%"
                                            changeType="neutral"
                                            accent="blue"
                                        />
                                    </>
                                }
                                chartRow={
                                    <>
                                        <LoadingSkeleton variant="chart" />
                                        <LoadingSkeleton variant="chart" />
                                    </>
                                }
                            />
                        </div>
                    </Card>

                    <Card>
                        <h3 className="text-sm font-semibold mb-4">List Page Template</h3>
                        <div className="border border-dashed border-border-default p-4 rounded-lg">
                            <ListPageTemplate
                                header={
                                    <PageHeader
                                        title="Transactions"
                                        subtitle="Manage all transactions"
                                        actions={
                                            <Button size="sm" icon={<Plus size={12} />}>
                                                New
                                            </Button>
                                        }
                                    />
                                }
                                filterBar={
                                    <FilterBar>
                                        <SearchBox placeholder="Search..." className="w-48" />
                                        <Select options={[{ label: 'All Status', value: 'all' }]} />
                                    </FilterBar>
                                }
                                table={<LoadingSkeleton variant="table" rows={3} />}
                                pagination={<Pagination currentPage={1} totalPages={5} />}
                            />
                        </div>
                    </Card>
                </div>
            </section>
        </div>
    );
}
