import { useEffect, useRef, useState } from 'react';
import { useAppStore } from '../stores/appStore';
import { API_BASE } from '../hooks/useVideoStream';
import { Icon } from './Icon';

type LocalCamStatus = 'connecting' | 'live' | 'denied' | 'error';

interface LiveVideoPaneProps {
  crosshairClassName?: string;
  crosshairOpacity?: string;
}

export function LiveVideoPane({
  crosshairClassName = 'text-5xl text-white',
  crosshairOpacity = 'opacity-60',
}: LiveVideoPaneProps) {
  const { setVideoStatus } = useAppStore();
  const [localStatus, setLocalStatus] = useState<LocalCamStatus>('connecting');
  const [droneOnline, setDroneOnline] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    let cancelled = false;
    let mediaStream: MediaStream | null = null;
    let videoEl: HTMLVideoElement | null = null;
    let retryTimer: number | undefined;
    let attempt = 0;

    const stopCamera = () => {
      mediaStream?.getTracks().forEach((t) => t.stop());
      mediaStream = null;
      if (videoEl) {
        videoEl.srcObject = null;
        videoEl = null;
      }
    };

    const startCamera = async () => {
      try {
        if (!navigator.mediaDevices?.getUserMedia) {
          throw new DOMException('Camera unsupported', 'NotSupportedError');
        }
        const stream = await navigator.mediaDevices.getUserMedia({
          video: true,
          audio: false,
        });
        if (cancelled) {
          stream.getTracks().forEach((t) => t.stop());
          return;
        }
        mediaStream = stream;
        videoEl = videoRef.current;
        if (videoEl) {
          videoEl.srcObject = stream;
          await videoEl.play().catch(() => {});
        }
        setLocalStatus('live');
      } catch (err) {
        if (cancelled) return;
        const name = (err as DOMException)?.name;
        if (name === 'NotAllowedError' || name === 'SecurityError') {
          setLocalStatus('denied');
          return;
        }
        attempt += 1;
        if (attempt <= 5) {
          // camera may be briefly busy (StrictMode remount / OS) — retry
          retryTimer = window.setTimeout(() => {
            if (!cancelled) void startCamera();
          }, 350 * attempt);
        } else {
          setLocalStatus('error');
        }
      }
    };

    void startCamera();

    return () => {
      cancelled = true;
      if (retryTimer) window.clearTimeout(retryTimer);
      stopCamera();
    };
  }, []);

  useEffect(() => {
    let cancelled = false;

    const tick = async () => {
      try {
        const [videoRes, droneRes] = await Promise.all([
          fetch(`${API_BASE}/video/status`, { cache: 'no-store' }).catch(() => null),
          fetch(`${API_BASE}/api/drone/status`, { cache: 'no-store' }).catch(() => null),
        ]);
        let online = false;
        if (videoRes?.ok) {
          const v = await videoRes.json();
          if (v.online) online = true;
        }
        if (!online && droneRes?.ok) {
          const d = await droneRes.json();
          if (d.connected) online = true;
        }
        if (!cancelled) setDroneOnline(online);
      } catch {
        if (!cancelled) setDroneOnline(false);
      }
    };

    void tick();
    const id = window.setInterval(() => void tick(), 3000);
    return () => {
      cancelled = true;
      window.clearInterval(id);
    };
  }, []);

  const paneStatus: 'connecting' | 'live' | 'offline' | 'denied' =
    localStatus === 'live'
      ? 'live'
      : localStatus === 'denied'
        ? 'denied'
        : localStatus === 'error'
          ? 'offline'
          : 'connecting';

  useEffect(() => {
    setVideoStatus(paneStatus);
  }, [paneStatus, setVideoStatus]);

  const isLive = paneStatus === 'live';

  const centerHint =
    paneStatus === 'live'
      ? null
      : paneStatus === 'connecting'
        ? 'Starting camera…'
        : paneStatus === 'denied'
          ? 'Camera permission required'
          : 'Camera unavailable';

  return (
    <div className="absolute inset-0 bg-[#0d1b2a]">
      <video
        ref={videoRef}
        className="absolute inset-0 w-full h-full object-cover -scale-x-100"
        playsInline
        muted
        autoPlay
      />

      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          background: `linear-gradient(135deg, #0d1b2a 0%, #1b3a5c 40%, #1b3a5c 60%, #0d1b2a 100%)`,
          opacity: isLive ? 0.25 : 1,
        }}
      />
      <div className="absolute inset-0 video-overlay pointer-events-none" />

      {!isLive && (
        <div
          className={`absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 pointer-events-none ${crosshairOpacity}`}
        >
          <Icon name="crosshair" className={crosshairClassName} weight="bold" />
        </div>
      )}

      {centerHint && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none z-[5]">
          <span className="bg-black/50 backdrop-blur px-4 py-2 rounded text-xs sm:text-sm text-white/70">
            {centerHint}
          </span>
        </div>
      )}

      <div
        className={`absolute bottom-0 left-0 right-0 z-10 px-3 py-1.5 flex items-center gap-2 text-[10px] font-bold uppercase tracking-wider text-white ${
          droneOnline ? 'bg-green-600/90' : 'bg-red-600/90'
        }`}
      >
        <span
          className={`w-1.5 h-1.5 rounded-full bg-white ${
            droneOnline ? '' : 'animate-pulse'
          }`}
        />
        {droneOnline ? 'Drone connected' : 'No drone connected'}
      </div>
    </div>
  );
}
