import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { monitorsAPI } from '../api/monitors';

// Fetch all monitors
export function useMonitors() {
  return useQuery({
    queryKey: ['monitors'],
    queryFn: monitorsAPI.getAll,
    refetchInterval: 60000, // Refetch every minute
  });
}

// Fetch single monitor
export function useMonitor(monitorId) {
  return useQuery({
    queryKey: ['monitors', monitorId],
    queryFn: () => monitorsAPI.getById(monitorId),
    enabled: !!monitorId,
  });
}

// Create monitor
export function useCreateMonitor() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: monitorsAPI.create,
    onSuccess: () => {
      queryClient.invalidateQueries(['monitors']);
    },
  });
}

// Update monitor
export function useUpdateMonitor() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ monitorId, data }) => monitorsAPI.update(monitorId, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries(['monitors']);
      queryClient.invalidateQueries(['monitors', variables.monitorId]);
    },
  });
}

// Delete monitor
export function useDeleteMonitor() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: monitorsAPI.delete,
    onSuccess: () => {
      queryClient.invalidateQueries(['monitors']);
    },
  });
}

// Trigger manual run
export function useTriggerRun() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: monitorsAPI.triggerRun,
    onSuccess: (_, monitorId) => {
      // Invalidate results to see new run
      queryClient.invalidateQueries(['results', monitorId]);
      // Invalidate monitor to see updated last_run_at
      queryClient.invalidateQueries(['monitors', monitorId]);
    },
  });
}
