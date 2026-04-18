import { StatCard } from '~/components/ui';

/* ---- Content Block wrapper matching Figma ---- */
function ContentBlock({
    title,
    tabs,
    children,
    className,
}: {
    title: string;
    tabs?: React.ReactNode;
    children: React.ReactNode;
    className?: string;
}) {
    return (
        <div
            className={`bg-surface-card rounded-xl flex flex-col gap-4 ${className ?? ''}`}
            style={{ padding: 24 }}
        >
            <div className="flex items-center justify-between">
                <span className="text-sm font-semibold text-text-primary">{title}</span>
                {tabs}
            </div>
            {children}
        </div>
    );
}

function ChartPlaceholder({ height = 200 }: { height?: number }) {
    return (
        <div
            className="w-full rounded-lg bg-subtle flex items-end justify-center gap-1.5 px-4 pb-4"
            style={{ height }}
        >
            {Array.from({ length: 12 }).map((_, i) => (
                <div
                    key={i}
                    className="flex-1 rounded-t-sm bg-accent-indigo opacity-20"
                    style={{ height: `${20 + Math.sin(i * 0.8) * 30 + Math.random() * 20}%` }}
                />
            ))}
        </div>
    );
}

function TabSelector() {
    return (
        <div className="flex items-center gap-1">
            <button className="px-3 py-1 text-xs rounded-md bg-text-primary text-bg-primary cursor-pointer">
                This year
            </button>
            <button className="px-3 py-1 text-xs rounded-md text-text-secondary hover:bg-subtle cursor-pointer transition-colors">
                Last year
            </button>
        </div>
    );
}

/* ---- Traffic source item ---- */
function TrafficSource({ name, percent, color }: { name: string; percent: number; color: string }) {
    return (
        <div className="flex items-center justify-between py-1.5">
            <div className="flex items-center gap-2">
                <div className="size-2 rounded-full" style={{ backgroundColor: color }} />
                <span className="text-sm text-text-primary">{name}</span>
            </div>
            <span className="text-sm text-text-secondary">{percent}%</span>
        </div>
    );
}

export function PublicHomePage() {
    return (
        <div className="flex flex-col gap-7">
            {/* Stat Cards Row */}
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
                <StatCard label="Views" value="7,265" change="+11.01%" changeType="positive" accent="purple" />
                <StatCard label="Visits" value="3,671" change="-0.03%" changeType="negative" accent="blue" />
                <StatCard label="New Users" value="156" change="+15.03%" changeType="positive" accent="purple" />
                <StatCard label="Active Users" value="2,318" change="+6.08%" changeType="positive" accent="blue" />
            </div>

            {/* Revenue + Traffic by Website row */}
            <div className="grid grid-cols-1 gap-4 lg:grid-cols-4">
                {/* Revenue — takes 3 cols */}
                <ContentBlock title="Revenue" tabs={<TabSelector />} className="lg:col-span-3">
                    <ChartPlaceholder height={240} />
                </ContentBlock>

                {/* Traffic by Website — takes 1 col */}
                <ContentBlock title="Traffic by Website" className="lg:col-span-1">
                    {/* Donut placeholder */}
                    <div className="flex justify-center py-2">
                        <div className="size-25 rounded-full border-[0.75rem] border-accent-indigo border-t-status-info border-r-status-success opacity-60" />
                    </div>
                    <div className="flex flex-col">
                        <TrafficSource name="Google" percent={42} color="#4F507F" />
                        <TrafficSource name="YouTube" percent={25} color="#3b82f6" />
                        <TrafficSource name="Instagram" percent={14} color="#22c55e" />
                        <TrafficSource name="Pinterest" percent={10} color="#f59e0b" />
                        <TrafficSource name="Facebook" percent={6} color="#8b5cf6" />
                        <TrafficSource name="Twitter" percent={3} color="#ef4444" />
                    </div>
                </ContentBlock>
            </div>

            {/* Traffic by Device + Traffic by Location row */}
            <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
                <ContentBlock title="Traffic by Device">
                    <ChartPlaceholder height={220} />
                </ContentBlock>
                <ContentBlock title="Traffic by Location">
                    {/* Map placeholder */}
                    <div
                        className="w-full rounded-lg bg-subtle flex items-center justify-center"
                        style={{ height: 220 }}
                    >
                        <span className="text-xs text-text-tertiary">Map visualization</span>
                    </div>
                </ContentBlock>
            </div>

            {/* Marketing & SEO — full width */}
            <ContentBlock title="Marketing & SEO">
                <ChartPlaceholder height={220} />
            </ContentBlock>
        </div>
    );
}
