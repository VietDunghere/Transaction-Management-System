import { useQuery } from '@tanstack/react-query';
import { demoService } from '~/services/demoService';

/**
 * Lightweight check: is the demo runner active?
 * Polls every 5s to detect start/stop. List pages use this to enable
 * their own 1s data refresh when demo is running.
 */
export function useDemoRunning() {
    const { data } = useQuery({
        queryKey: ['demo', 'running'],
        queryFn: () => demoService.getStatus(),
        refetchInterval: 5000,
        select: (d) => d.running,
    });
    return data ?? false;
}
