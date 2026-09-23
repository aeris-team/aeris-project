import { useAppStore } from '../stores/appStore';
import { LiveVideoPane } from './LiveVideoPane';
import { Icon } from './Icon';

export function LiveFeed() {
  const { link, setActiveTab, videoStatus } = useAppStore();

  const badge =
    videoStatus === 'live'
      ? { text: 'LIVE', dot: 'bg-green-400 pulse-indicator' }
      : videoStatus === 'connecting'
        ? { text: 'CONNECTING', dot: 'bg-yellow-400 pulse-indicator' }
        : { text: 'OFFLINE', dot: 'bg-red-500' };

  const statusText =
    videoStatus === 'live'
      ? '1080p • 30fps'
      : videoStatus === 'connecting'
        ? 'Starting camera…'
        : videoStatus === 'denied'
          ? 'Camera permission required'
          : 'Camera unavailable';

  return (
    <div className="lg:col-span-4 panel-card p-0 overflow-hidden relative group min-h-[300px] lg:min-h-0">
      <div className="absolute top-4 left-4 right-4 flex justify-between items-start z-10">
        <h2 className="text-sm font-bold text-white drop-shadow-md">LIVE FEED (RGB)</h2>
        <div className="flex items-center gap-2 bg-black/50 backdrop-blur-sm px-2 py-1 rounded text-xs text-white">
          <span className={`w-1.5 h-1.5 rounded-full ${badge.dot}`} />
          <span>{badge.text}</span>
        </div>
      </div>

      <LiveVideoPane crosshairClassName="text-5xl text-white" crosshairOpacity="opacity-60" />

      <div className="absolute bottom-8 left-4 right-4 flex justify-between items-end z-10 text-white/90 text-xs">
        <div>
          <div className="bg-black/40 backdrop-blur px-2 py-1 rounded inline-block mb-1">{statusText}</div>
          <div className="bg-black/40 backdrop-blur px-2 py-1 rounded block font-mono">
            Lat: {Math.round(link.wifi.latency)}ms
          </div>
        </div>
        <button
          onClick={() => setActiveTab('livefeed')}
          className="bg-black/40 hover:bg-black/60 backdrop-blur p-2 rounded transition-colors"
        >
          <Icon name="corners-out" className="text-lg" />
        </button>
      </div>
    </div>
  );
}
