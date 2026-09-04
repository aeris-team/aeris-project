import { useAppStore } from '../stores/appStore';
import { Icon } from './Icon';

export function CommLinkHealth() {
  const { link } = useAppStore();

  return (
    <div className="lg:col-span-3 flex flex-col gap-4 overflow-y-auto">
      <div className="panel-card flex-1 p-4">
        <h2 className="text-xs font-bold text-slate-500 mb-3 uppercase tracking-wider flex items-center justify-between">
          Comm Links
          <Icon name="broadcast" className="text-lg" />
        </h2>

        <div className="bg-slate-50 rounded-lg p-3 border border-slate-200 mb-3">
          <div className="flex justify-between items-center mb-2">
            <div className="font-semibold text-xs text-slate-700">5 GHz Wi-Fi</div>
            <span className="flex items-center gap-1 text-[10px] font-bold text-aeris">
              <span className="w-1.5 h-1.5 rounded-full bg-aeris pulse-indicator" /> Good
            </span>
          </div>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div>
              <span className="text-slate-400 block text-[9px] uppercase">Latency</span>
              <span className="font-mono text-slate-800">{Math.round(link.wifi.latency)} ms</span>
            </div>
            <div>
              <span className="text-slate-400 block text-[9px] uppercase">RSSI</span>
              <span className="font-mono text-slate-800">{Math.round(link.wifi.rssi)} dBm</span>
            </div>
            <div>
              <span className="text-slate-400 block text-[9px] uppercase">Bitrate</span>
              <span className="font-mono text-slate-800">5.4 Mbps</span>
            </div>
          </div>
        </div>

        <div className="bg-slate-50 rounded-lg p-3 border border-slate-200">
          <div className="flex justify-between items-center mb-2">
            <div className="font-semibold text-xs text-slate-700">915 MHz LoRa</div>
            <span className="flex items-center gap-1 text-[10px] font-bold text-aeris">
              <span className="w-1.5 h-1.5 rounded-full bg-aeris pulse-indicator" /> Good
            </span>
          </div>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div>
              <span className="text-slate-400 block text-[9px] uppercase">Latency</span>
              <span className="font-mono text-slate-800">{Math.round(link.lora.latency)} ms</span>
            </div>
            <div>
              <span className="text-slate-400 block text-[9px] uppercase">RSSI</span>
              <span className="font-mono text-slate-800">{Math.round(link.lora.rssi)} dBm</span>
            </div>
            <div>
              <span className="text-slate-400 block text-[9px] uppercase">PLR</span>
              <span className="font-mono text-slate-800">0.8%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
