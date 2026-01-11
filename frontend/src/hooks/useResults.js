import { useQuery } from '@tanstack/react-query';
import { monitorsAPI } from '../api/monitors';

// Fetch results for a monitor
export function useResults(monitorId, limit = 10) {
  return useQuery({
    queryKey: ['results', monitorId, limit],
    queryFn: () => monitorsAPI.getResults(monitorId, limit),
    enabled: !!monitorId,
    refetchInterval: 30000, // Refetch every 30 seconds
  });
}

// Fetch single result
export function useResult(monitorId, resultId) {
  return useQuery({
    queryKey: ['results', monitorId, resultId],
    queryFn: () => monitorsAPI.getResult(monitorId, resultId),
    enabled: !!(monitorId && resultId),
  });
}
