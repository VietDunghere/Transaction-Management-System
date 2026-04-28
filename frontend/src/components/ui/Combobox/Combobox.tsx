import { useState, useRef, useEffect, useCallback } from 'react';
import { cn } from '~/utils/cn';

export interface ComboboxOption {
    value: string;
    label: string;
    sublabel?: string;
}

interface ComboboxProps {
    label?: string;
    placeholder?: string;
    error?: string;
    value: string;
    displayValue: string;
    options: ComboboxOption[];
    onSearch: (q: string) => void;
    onSelect: (value: string, label: string) => void;
    loading?: boolean;
}

export function Combobox({
    label,
    placeholder,
    error,
    value,
    displayValue,
    options,
    onSearch,
    onSelect,
    loading,
}: ComboboxProps) {
    const [inputText, setInputText] = useState(displayValue);
    const [isOpen, setIsOpen] = useState(false);
    const [activeIndex, setActiveIndex] = useState(-1);
    const debounceRef = useRef<ReturnType<typeof setTimeout>>(null);
    const containerRef = useRef<HTMLDivElement>(null);
    const listRef = useRef<HTMLUListElement>(null);
    const inputId = label?.toLowerCase().replace(/\s+/g, '-');

    // Sync displayValue from parent when selection changes externally
    useEffect(() => {
        if (!isOpen) {
            setInputText(displayValue);
        }
    }, [displayValue, isOpen]);

    // Close on outside click
    useEffect(() => {
        function handleClickOutside(e: MouseEvent) {
            if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
                setIsOpen(false);
                // Reset input to the display value if nothing new was selected
                setInputText(displayValue);
            }
        }
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, [displayValue]);

    // Scroll active item into view
    useEffect(() => {
        if (activeIndex >= 0 && listRef.current) {
            const item = listRef.current.children[activeIndex] as HTMLElement | undefined;
            item?.scrollIntoView({ block: 'nearest' });
        }
    }, [activeIndex]);

    const debouncedSearch = useCallback(
        (q: string) => {
            if (debounceRef.current) clearTimeout(debounceRef.current);
            debounceRef.current = setTimeout(() => {
                onSearch(q);
            }, 300);
        },
        [onSearch],
    );

    function handleInputChange(e: React.ChangeEvent<HTMLInputElement>) {
        const q = e.target.value;
        setInputText(q);
        setActiveIndex(-1);
        setIsOpen(true);
        debouncedSearch(q);
    }

    function handleInputFocus() {
        // If a value is already selected, clear to re-search
        if (value) {
            setInputText('');
            onSearch('');
        }
        setIsOpen(true);
        setActiveIndex(-1);
    }

    function handleSelect(opt: ComboboxOption) {
        onSelect(opt.value, opt.label);
        setInputText(opt.label);
        setIsOpen(false);
        setActiveIndex(-1);
    }

    function handleKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
        if (!isOpen) {
            if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
                setIsOpen(true);
            }
            return;
        }

        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                setActiveIndex((prev) => (prev < options.length - 1 ? prev + 1 : 0));
                break;
            case 'ArrowUp':
                e.preventDefault();
                setActiveIndex((prev) => (prev > 0 ? prev - 1 : options.length - 1));
                break;
            case 'Enter':
                e.preventDefault();
                if (activeIndex >= 0 && activeIndex < options.length) {
                    handleSelect(options[activeIndex]);
                }
                break;
            case 'Escape':
                setIsOpen(false);
                setInputText(displayValue);
                break;
        }
    }

    return (
        <div className="flex flex-col gap-1.5" ref={containerRef}>
            {label && (
                <label htmlFor={inputId} className="text-sm font-semibold text-text-primary">
                    {label}
                </label>
            )}
            <div className="relative">
                <input
                    id={inputId}
                    type="text"
                    role="combobox"
                    aria-expanded={isOpen}
                    aria-autocomplete="list"
                    aria-activedescendant={activeIndex >= 0 ? `cb-opt-${activeIndex}` : undefined}
                    autoComplete="off"
                    value={inputText}
                    placeholder={placeholder}
                    onChange={handleInputChange}
                    onFocus={handleInputFocus}
                    onKeyDown={handleKeyDown}
                    className={cn(
                        'w-full',
                        'px-4 py-2.5 text-sm',
                        'bg-primary',
                        'border border-border-default',
                        'rounded-lg',
                        'outline-none transition-all duration-150',
                        'focus:border-accent-indigo focus:ring-1 focus:ring-accent-indigo',
                        'placeholder:text-text-tertiary',
                        error && 'border-status-danger focus:ring-status-danger',
                    )}
                />
                {loading && (
                    <div className="absolute right-3 top-1/2 -translate-y-1/2">
                        <div className="h-4 w-4 animate-spin rounded-full border-2 border-border-default border-t-accent-indigo" />
                    </div>
                )}
                {isOpen && (
                    <ul
                        ref={listRef}
                        role="listbox"
                        className={cn(
                            'absolute z-50 mt-1 w-full max-h-60 overflow-auto',
                            'rounded-lg border border-border-default',
                            'bg-primary shadow-lg',
                        )}
                    >
                        {options.length === 0 && !loading && inputText.length >= 2 && (
                            <li className="px-4 py-2.5 text-sm text-text-tertiary">No results found</li>
                        )}
                        {options.length === 0 && !loading && inputText.length < 2 && (
                            <li className="px-4 py-2.5 text-sm text-text-tertiary">
                                Type at least 2 characters to search
                            </li>
                        )}
                        {options.map((opt, idx) => (
                            <li
                                key={opt.value}
                                id={`cb-opt-${idx}`}
                                role="option"
                                aria-selected={idx === activeIndex}
                                onMouseDown={(e) => {
                                    e.preventDefault();
                                    handleSelect(opt);
                                }}
                                onMouseEnter={() => setActiveIndex(idx)}
                                className={cn(
                                    'cursor-pointer px-4 py-2.5 text-sm',
                                    'transition-colors duration-100',
                                    idx === activeIndex
                                        ? 'bg-surface-card text-text-primary'
                                        : 'text-text-primary hover:bg-surface-card',
                                    opt.value === value && 'font-semibold',
                                )}
                            >
                                <span>{opt.label}</span>
                                {opt.sublabel && (
                                    <span className="ml-2 text-xs text-text-secondary">{opt.sublabel}</span>
                                )}
                            </li>
                        ))}
                    </ul>
                )}
            </div>
            {error && <p className="text-sm text-status-danger font-semibold">{error}</p>}
        </div>
    );
}
