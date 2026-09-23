import { useEffect, useRef, useState } from 'react';
import { useAppStore } from '../stores/appStore';
import { LiveVideoPane } from '../components/LiveVideoPane';
import { Icon } from '../components/Icon';

export function LiveFeedPage() {
  const { link, videoStatus } = useAppStore();
  const panelRef = useRef<HTMLDivElement>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);

  useEffect(() => {
    const onChange = () => setIsFullscreen(Boolean(document.fullscreenElement));
    document.addEventListener('fullscreenchange', onChange);
    return () => document.removeEventListener('fullscreenchange', onChange);
  }, []);

  const toggleFullscreen = async () => {
    try {
      if (document.fullscreenElement) {
        await document.exitFullscreen();
      } else {
        await panelRef.current?.requestFullscreen();
      }
    } catch {
      // browser may block fullscreen (e.g. iframe without allow)
    }
  };

  const badge =
    videoStatus === 'live'
      ? { text: 'Live', cls: 'bg-green-500' }
      : videoStatus === 'connecting'
        ? { text: 'Connecting', cls: 'bg-yellow-500' }
        : { text: 'Offline', cls: 'bg-red-500' };

  return (
    <div className="h-full flex flex-col">
      <div
        ref={panelRef}
        className="panel-card flex-1 p-0 flex flex-col overflow-hidden bg-slate-900 border-none rounded-xl shadow-lg relative"
      >
        <div className="p-4 flex flex-col sm:flex-row justify-between sm:items-center gap-4 bg-black/50 absolute top-0 left-0 right-0 z-10 text-white backdrop-blur">
          <div className="flex items-center gap-4">
            <h2 className="text-base sm:text-lg font-bold">5GHz Video Surveillance</h2>
            <span
              className={`${badge.cls} text-white text-[10px] px-2 py-0.5 rounded font-bold uppercase tracking-wider animate-pulse`}
            >
              {badge.text}
            </span>
          </div>
          <div className="flex items-center gap-4 sm:gap-6 text-xs text-slate-300 overflow-x-auto pb-1 sm:pb-0">
            <div className="whitespace-nowrap">Res: <span className="text-white">1080p</span></div>
            <div className="whitespace-nowrap">FPS: <span className="text-white">30</span></div>
            <div className="whitespace-nowrap">
              Latency: <span className="text-green-400 font-mono">{Math.round(link.wifi.latency)}ms</span>
            </div>
            <div className="whitespace-nowrap">RSSI: <span className="text-white font-mono">{Math.round(link.wifi.rssi)}dBm</span></div>
            <button
              onClick={toggleFullscreen}
              className="hover:text-white rounded"
              title={isFullscreen ? 'Exit fullscreen' : 'Fullscreen'}
            >
              <Icon name="corners-out" className="text-xl" />
            </button>
          </div>
        </div>

        <LiveVideoPane
          crosshairClassName="text-[150px] text-white"
          crosshairOpacity="opacity-30"
        />
      </div>
    </div>
  );
}
