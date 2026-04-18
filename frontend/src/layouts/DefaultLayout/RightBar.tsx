import { cn } from '~/utils/cn';
import { formatActivityTime, useActivityStore } from '~/stores/useActivityStore';

/* ---- Data ---- */

const notifications: Array<{
    icon: React.ReactNode;
    iconBg: string;
    text: string;
    time: string;
}> = [];

const contacts = [
    { avatar: 'VH', name: 'Vũ Hoàng Anh' },
    { avatar: 'NB', name: 'Nguyễn Bá Hùng' },
    { avatar: 'PN', name: 'Phan Nguyễn Việt Dũng' },
    { avatar: 'LD', name: 'Lê Duy Anh' },
    { avatar: 'NT', name: 'Nguyễn Trung Nam' },
];

export function RightBar() {
    const activities = useActivityStore((s) => s.activities);

    return (
        <aside
            className={cn(
                'hidden lg:flex flex-col shrink-0',
                'bg-primary',
                'border-l border-border-default',
                'overflow-y-auto',
            )}
            style={{ width: 'var(--right-bar-width)', padding: 16, gap: 16 }}
        >
            {/* NOTIFICATIONS */}
            <section>
                <div className="flex items-center justify-between px-2 py-2 mb-1">
                    <span className="text-xs font-normal text-text-secondary uppercase tracking-wider">
                        Notifications
                    </span>
                </div>
                <ul className="flex flex-col">
                    {notifications.length === 0 ? (
                        <li className="px-2 py-2 text-sm text-text-secondary">No notifications yet.</li>
                    ) : (
                        notifications.map((item, idx) => (
                            <li key={idx} className="flex items-start gap-2 px-2 py-2">
                                <div
                                    className={cn(
                                        'flex size-6 shrink-0 items-center justify-center rounded-xs',
                                        item.iconBg,
                                    )}
                                >
                                    <span className="text-text-on-accent">{item.icon}</span>
                                </div>
                                <div className="flex flex-col min-w-0">
                                    <span className="text-sm text-text-primary leading-5 truncate">{item.text}</span>
                                    <span className="text-xs text-text-secondary leading-4">{item.time}</span>
                                </div>
                            </li>
                        ))
                    )}
                </ul>
            </section>

            {/* ACTIVITIES */}
            <section>
                <div className="flex items-center justify-between px-2 py-2 mb-1">
                    <span className="text-xs font-normal text-text-secondary uppercase tracking-wider">Activities</span>
                </div>
                <ul className="flex flex-col">
                    {activities.length === 0 ? (
                        <li className="px-2 py-2 text-sm text-text-secondary">No activities yet.</li>
                    ) : (
                        activities.map((item, idx) => (
                            <li key={idx} className="flex items-start gap-2 px-2 py-2 relative">
                                {/* Timeline line */}
                                {idx < activities.length - 1 && (
                                    <div className="absolute left-6 top-10 bottom-0 w-px bg-border-default" />
                                )}
                                {/* Avatar */}
                                <div className="flex size-6 shrink-0 items-center justify-center rounded-full bg-secondary relative z-10">
                                    <span className="text-[0.5625rem] font-semibold text-text-secondary">
                                        {item.avatar}
                                    </span>
                                </div>
                                <div className="flex flex-col min-w-0">
                                    <span className="text-sm text-text-primary leading-5">
                                        <span className="font-semibold">{item.name}</span> {item.action}
                                    </span>
                                    <span className="text-xs text-text-secondary leading-4">
                                        {formatActivityTime(item.timestamp)}
                                    </span>
                                </div>
                            </li>
                        ))
                    )}
                </ul>
            </section>

            {/* CONTACTS */}
            <section>
                <div className="flex items-center justify-between px-2 py-2 mb-1">
                    <span className="text-xs font-normal text-text-secondary uppercase tracking-wider">Contacts</span>
                </div>
                <ul className="flex flex-col">
                    {contacts.map((item) => (
                        <li
                            key={item.name}
                            className="flex items-center gap-2 px-2 py-2 cursor-pointer hover:bg-subtle rounded-sm transition-colors"
                        >
                            <div className="flex size-6 shrink-0 items-center justify-center rounded-full bg-accent-purple">
                                <span className="text-[0.5625rem] font-semibold text-text-on-accent">
                                    {item.avatar}
                                </span>
                            </div>
                            <span className="text-sm text-text-primary">{item.name}</span>
                        </li>
                    ))}
                </ul>
            </section>
        </aside>
    );
}
