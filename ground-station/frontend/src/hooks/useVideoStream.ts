import { useCallback, useEffect, useRef, useState } from 'react';

export const API_BASE = 'http://localhost:8000';

export type VideoStatus = 'connecting' | 'live' | 'offline';

async function probeOnline(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/video/status`, { cache: 'no-store' });
    if (!res.ok) return false;
    const data = await res.json();
    return Boolean(data.online);
  } catch {
    return false;
  }
}

export function useVideoStream(pollMs = 3000) {
  const [status, setStatus] = useState<VideoStatus>('connecting');
  const [attempt, setAttempt] = useState(0);
  const statusRef = useRef<VideoStatus>('connecting');

  useEffect(() => {
    statusRef.current = status;
  }, [status]);

  const streamUrl = `${API_BASE}/video/stream?cb=${attempt}`;

  const retry = useCallback(() => {
    setStatus('connecting');
    setAttempt((a) => a + 1);
  }, []);

  const handleLoad = useCallback(() => {
    setStatus('live');
  }, []);

  const handleError = useCallback(() => {
    setStatus('offline');
  }, []);

  useEffect(() => {
    const id = window.setInterval(() => {
      const current = statusRef.current;
      if (current === 'connecting') return;

      void probeOnline().then((online) => {
        const now = statusRef.current;
        if (!online && now !== 'offline') {
          setStatus('offline');
        } else if (online && now === 'offline') {
          setStatus('connecting');
          setAttempt((a) => a + 1);
        }
      });
    }, pollMs);
    return () => window.clearInterval(id);
  }, [pollMs]);

  return { status, streamUrl, attempt, retry, handleLoad, handleError };
}
