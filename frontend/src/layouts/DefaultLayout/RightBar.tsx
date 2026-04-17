import { Bug, User, Radio } from 'lucide-react';
import { cn } from '~/utils/cn';

/* ---- Data ---- */

const notifications = [
    {
        icon: <Bug size={16} />,
        iconBg: 'bg-[var(--color-bg-accent-purple)]',
        text: 'You fixed a bug.',
        time: 'Just now',
    },
    {
        icon: <User size={16} />,
        iconBg: 'bg-[var(--color-bg-accent-blue)]',
        text: 'New user registered.',
        time: '59 minutes ago',
    },
    {
        icon: <Bug size={16} />,
        iconBg: 'bg-[var(--color-bg-accent-purple)]',
        text: 'You fixed a bug.',
        time: '12 hours ago',
    },
    {
        icon: <Radio size={16} />,
        iconBg: 'bg-[var(--color-bg-accent-blue)]',
        text: 'Andi Lane subscribed to you.',
        time: 'Today, 11:59 AM',
    },
];

const activities = [
    { avatar: 'AV', name: 'You', action: 'changed invoice status', time: 'Just now' },
    { avatar: 'AL', name: 'Andi Lane', action: 'replied to comment', time: '5 min ago' },
    { avatar: 'JM', name: 'John Miller', action: 'added new transaction', time: '1 hour ago' },
    { avatar: 'LS', name: 'Lisa Smith', action: 'approved a request', time: '2 hours ago' },
    { avatar: 'RK', name: 'Robert Kim', action: 'uploaded a document', time: 'Yesterday' },
];

const contacts = [
    { avatar: 'NP', name: 'Natali Petrov' },
    { avatar: 'DW', name: 'Drew Warren' },
    { avatar: 'OF', name: 'Orlane Fisher' },
    { avatar: 'AJ', name: 'Andi Johnson' },
    { avatar: 'KC', name: 'Kate Chen' },
    { avatar: 'RA', name: 'Rose Adams' },
];

export function RightBar() {
    return (
        <aside
            className={cn(
                'hidden lg:flex flex-col shrink-0',
                'bg-[var(--color-bg-primary)]',
                'border-l border-[var(--color-border-default)]',
                'overflow-y-auto',
            )}
            style={{ width: 'var(--right-bar-width)', padding: 16, gap: 16 }}
        >
            {/* NOTIFICATIONS */}
            <section>
                <div className="flex items-center justify-between px-2 py-2 mb-1">
                    <span className="text-xs font-normal text-[var(--color-text-secondary)] uppercase tracking-wider">
                        Notifications
                    </span>
                </div>
                <ul className="flex flex-col">
                    {notifications.map((item, idx) => (
                        <li key={idx} className="flex items-start gap-2 px-2 py-2">
                            <div
                                className={cn(
                                    'flex size-6 shrink-0 items-center justify-center rounded-xs',
                                    item.iconBg,
                                )}
                            >
                                <span className="text-[var(--color-text-on-accent)]">{item.icon}</span>
                            </div>
                            <div className="flex flex-col min-w-0">
                                <span className="text-sm text-[var(--color-text-primary)] leading-5 truncate">
                                    {item.text}
                                </span>
                                <span className="text-xs text-[var(--color-text-secondary)] leading-4">
                                    {item.time}
                                </span>
                            </div>
                        </li>
                    ))}
                </ul>
            </section>

            {/* ACTIVITIES */}
            <section>
                <div className="flex items-center justify-between px-2 py-2 mb-1">
                    <span className="text-xs font-normal text-[var(--color-text-secondary)] uppercase tracking-wider">
                        Activities
                    </span>
                </div>
                <ul className="flex flex-col">
                    {activities.map((item, idx) => (
                        <li key={idx} className="flex items-start gap-2 px-2 py-2 relative">
                            {/* Timeline line */}
                            {idx < activities.length - 1 && (
                                <div className="absolute left-[23px] top-10 bottom-0 w-px bg-[var(--color-border-default)]" />
                            )}
                            {/* Avatar */}
                            <div className="flex size-6 shrink-0 items-center justify-center rounded-full bg-[var(--color-bg-secondary)] relative z-10">
                                <span className="text-[9px] font-semibold text-[var(--color-text-secondary)]">
                                    {item.avatar}
                                </span>
                            </div>
                            <div className="flex flex-col min-w-0">
                                <span className="text-sm text-[var(--color-text-primary)] leading-5">
                                    <span className="font-semibold">{item.name}</span> {item.action}
                                </span>
                                <span className="text-xs text-[var(--color-text-secondary)] leading-4">
                                    {item.time}
                                </span>
                            </div>
                        </li>
                    ))}
                </ul>
            </section>

            {/* CONTACTS */}
            <section>
                <div className="flex items-center justify-between px-2 py-2 mb-1">
                    <span className="text-xs font-normal text-[var(--color-text-secondary)] uppercase tracking-wider">
                        Contacts
                    </span>
                </div>
                <ul className="flex flex-col">
                    {contacts.map((item) => (
                        <li
                            key={item.name}
                            className="flex items-center gap-2 px-2 py-2 cursor-pointer hover:bg-[var(--color-bg-subtle)] rounded-sm transition-colors"
                        >
                            <div className="flex size-6 shrink-0 items-center justify-center rounded-full bg-[var(--color-bg-accent-purple)]">
                                <span className="text-[9px] font-semibold text-[var(--color-text-on-accent)]">
                                    {item.avatar}
                                </span>
                            </div>
                            <span className="text-sm text-[var(--color-text-primary)]">{item.name}</span>
                        </li>
                    ))}
                </ul>
            </section>
        </aside>
    );
}
