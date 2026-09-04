import { useAppStore } from '../stores/appStore';
import { Icon } from '../components/Icon';

export function LiveFeedPage() {
  const { link } = useAppStore();

  return (
    <div className="h-full flex flex-col">
      <div className="panel-card flex-1 p-0 flex flex-col overflow-hidden bg-slate-900 border-none rounded-xl shadow-lg relative">
        <div className="p-4 flex flex-col sm:flex-row justify-between sm:items-center gap-4 bg-black/50 absolute top-0 left-0 right-0 z-10 text-white backdrop-blur">
          <div className="flex items-center gap-4">
            <h2 className="text-base sm:text-lg font-bold">5GHz Video Surveillance</h2>
            <span className="bg-green-500 text-white text-[10px] px-2 py-0.5 rounded font-bold uppercase tracking-wider animate-pulse">
              Live
            </span>
          </div>
          <div className="flex items-center gap-4 sm:gap-6 text-xs text-slate-300 overflow-x-auto pb-1 sm:pb-0">
            <div className="whitespace-nowrap">Res: <span className="text-white">1080p</span></div>
            <div className="whitespace-nowrap">FPS: <span className="text-white">30</span></div>
            <div className="whitespace-nowrap">Latency: <span className="text-green-400 font-mono">{Math.round(link.wifi.latency)}ms</span></div>
            <div className="whitespace-nowrap">RSSI: <span className="text-white font-mono">{Math.round(link.wifi.rssi)}dBm</span></div>
            <button onClick={() => alert('Fullscreen mode engaged.')} className="hover:text-white rounded">
              <Icon name="corners-out" className="text-xl" />
            </button>
          </div>
        </div>

        <div className="absolute inset-0 bg-[#0d1b2a]">
          <img
            src="https://images.unsplash.com/photo-1623869661448-f62291dc7685?q=80&w=1200&auto=format&fit=crop"
            className="w-full h-full object-cover opacity-60"
            alt="Full screen video"
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
          <div className="absolute inset-0 flex items-center justify-center opacity-30 pointer-events-none">
            <Icon name="crosshair" className="text-[150px] text-white" weight="bold" />
          </div>
        </div>
      </div>
    </div>
  );
}
