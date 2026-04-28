import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import type { ReactElement } from 'react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { DemoPage } from '~/pages/DemoPage/DemoPage';
import { adminUser, demoStatusRunning, demoStatusStopped } from '~/test/fixtures';
import { setAuthUser } from '~/test/testUtils';
import type { DemoStatus } from '~/services/demoService';

const demoServiceMocks = vi.hoisted(() => ({
    getStatus: vi.fn(),
    start: vi.fn(),
    stop: vi.fn(),
}));

vi.mock('~/services/demoService', () => ({
    demoService: demoServiceMocks,
}));

function renderWithQueryClient(ui: ReactElement) {
    const queryClient = new QueryClient({
        defaultOptions: {
            queries: {
                retry: false,
            },
            mutations: {
                retry: false,
            },
        },
    });

    return render(<QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>);
}

describe('demo page', () => {
    let currentStatus: DemoStatus;

    beforeEach(() => {
        currentStatus = demoStatusStopped;
        demoServiceMocks.getStatus.mockImplementation(async () => currentStatus);
        demoServiceMocks.start.mockImplementation(async () => {
            currentStatus = demoStatusRunning;
            return currentStatus;
        });
        demoServiceMocks.stop.mockImplementation(async () => {
            currentStatus = demoStatusStopped;
            return currentStatus;
        });
        setAuthUser(adminUser);
    });

    it('starts and stops the demo runner', async () => {
        const user = userEvent.setup();

        renderWithQueryClient(<DemoPage />);

        await screen.findByRole('button', { name: 'Start Demo' });
        expect(screen.getByRole('heading', { name: 'Demo Runner' })).toBeInTheDocument();
        expect(screen.getByText('Configuration')).toBeInTheDocument();
        expect(screen.getByText('No events yet. Start the demo to generate data.')).toBeInTheDocument();

        await user.click(screen.getByRole('button', { name: 'Start Demo' }));
        await waitFor(() => expect(screen.getByRole('button', { name: 'Stop Demo' })).toBeInTheDocument());
        expect(screen.getByText(/Live/)).toBeInTheDocument();
        expect(demoServiceMocks.start).toHaveBeenCalledWith({ rate: 1, count: null, loan_pct: 20 });

        await user.click(screen.getByRole('button', { name: 'Stop Demo' }));
        await waitFor(() => expect(screen.getByRole('button', { name: 'Start Demo' })).toBeInTheDocument());
        expect(demoServiceMocks.stop).toHaveBeenCalledTimes(1);
    });
});
