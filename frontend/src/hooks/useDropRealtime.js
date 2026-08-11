import { useEffect, useRef } from 'react';
import { useQueryClient } from '@tanstack/react-query';

export const useDropRealtime = (dropId = 0) => {
  const queryClient = useQueryClient();
  const wsRef = useRef(null);

  useEffect(() => {
    // Determine WebSocket URL dynamically based on environment
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    let wsHost = window.location.host;
    
    // In Vite dev mode (port 5173), target backend at localhost:8000
    if (wsHost.includes('5173')) {
      wsHost = 'localhost:8000';
    }
    
    const wsUrl = `${protocol}//${wsHost}/api/ws/drops/${dropId}`;

    let socket;
    try {
      socket = new WebSocket(wsUrl);
      wsRef.current = socket;

      socket.onopen = () => {
        console.log(`[WebSocket] Connected to live updates for drop_id=${dropId}`);
      };

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('[WebSocket] Live event received:', data);

          if (data.event === 'entry_updated' || data.event === 'drop_status_updated') {
            // Automatically invalidate TanStack Query caches to re-fetch live data
            queryClient.invalidateQueries({ queryKey: ['drops'] });
            queryClient.invalidateQueries({ queryKey: ['public-drops'] });
            queryClient.invalidateQueries({ queryKey: ['my-entries'] });
          }
        } catch (e) {
          console.error('[WebSocket] Failed to parse message:', e);
        }
      };

      socket.onerror = (err) => {
        console.warn('[WebSocket] Connection error:', err);
      };

      socket.onclose = () => {
        console.log(`[WebSocket] Disconnected from drop_id=${dropId}`);
      };
    } catch (err) {
      console.warn('[WebSocket] Instantiation error:', err);
    }

    // SSE Fallback for serverless environments (e.g. Vercel)
    const sseUrl = `/api/drops/${dropId}/stream`;
    let eventSource;
    if (typeof EventSource !== 'undefined' && dropId > 0) {
      try {
        eventSource = new EventSource(sseUrl);
        eventSource.onmessage = (e) => {
          try {
            const data = JSON.parse(e.data);
            if (data.event === 'entry_updated' || data.event === 'drop_status_updated') {
              queryClient.invalidateQueries({ queryKey: ['drops'] });
              queryClient.invalidateQueries({ queryKey: ['public-drops'] });
            }
          } catch (err) {
            // ignore
          }
        };
      } catch (err) {
        // ignore
      }
    }

    return () => {
      if (socket && socket.readyState === WebSocket.OPEN) {
        socket.close();
      }
      if (eventSource) {
        eventSource.close();
      }
    };
  }, [dropId, queryClient]);
};
