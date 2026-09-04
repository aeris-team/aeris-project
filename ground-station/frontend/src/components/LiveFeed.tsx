import { useAppStore } from '../stores/appStore';
import { Icon } from './Icon';

export function LiveFeed() {
  const { link, setActiveTab } = useAppStore();

  return (
    <div className="lg:col-span-4 panel-card p-0 overflow-hidden relative group min-h-[300px] lg:min-h-0">
      <div className="absolute top-4 left-4 right-4 flex justify-between items-start z-10">
        <h2 className="text-sm font-bold text-white drop-shadow-md">LIVE FEED (RGB)</h2>
        <div className="flex items-center gap-2 bg-black/50 backdrop-blur-sm px-2 py-1 rounded text-xs text-white">
          <span className="w-1.5 h-1.5 rounded-full bg-green-400 pulse-indicator" />
          <span>LIVE</span>
        </div>
      </div>

      <div className="absolute inset-0 bg-[#0d1b2a]">
        <img
          src="https://images.unsplash.com/photo-1623869661448-f62291dc7685?q=80&w=800&auto=format&fit=crop"
          className="w-full h-full object-cover opacity-60"
          alt="Aerial Forest View"
          onError={(e) => {
            (e.target as HTMLImageElement).style.display = 'none';
          }}
        />
        <div
          className="absolute inset-0 pointer-events-none"
          style={{
            background: `linear-gradient(135deg, #0d1b2a 0%, #1b3a5c 40%, #1b3a5c 60%, #0d1b2a 100%)`,
          }}
        />
        <div
          className="absolute inset-0 video-overlay pointer-events-none"
        />

        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 opacity-60 pointer-events-none">
          <Icon name="crosshair" className="text-5xl text-white" weight="bold" />
        </div>

        <div className="absolute bottom-4 left-4 right-4 flex justify-between items-end z-10 text-white/90 text-xs">
          <div>
            <div className="bg-black/40 backdrop-blur px-2 py-1 rounded inline-block mb-1">1080p • 30fps</div>
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
    </div>
  );
}
