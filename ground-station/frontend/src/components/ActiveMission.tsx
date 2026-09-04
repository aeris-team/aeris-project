import { useAppStore } from '../stores/appStore';
import { Icon } from './Icon';

export function ActiveMission() {
  const { mission, endMission, startMission } = useAppStore();

  const isActive = mission.status === 'active';

  return (
    <div className="lg:col-span-3 panel-card bg-white border-aeris border-t-4 overflow-y-auto">
      <div className="flex items-center justify-between mb-1">
        <div className="text-[10px] font-bold text-aeris uppercase tracking-wider">
          {isActive ? 'Active Mission' : 'Mission Ended'}
        </div>
        <div className={`flex items-center gap-1 text-[10px] font-bold ${isActive ? 'text-aeris' : 'text-slate-400'}`}>
          <span className={`w-1.5 h-1.5 rounded-full ${isActive ? 'bg-aeris pulse-indicator' : 'bg-slate-400'}`} />
          {isActive ? 'ACTIVE' : 'ENDED'}
        </div>
      </div>
      <h2 className="text-lg font-bold text-slate-800 mb-4">{mission.name}</h2>

      <div className="space-y-4 text-xs">
        <div className="flex justify-between items-center border-b border-slate-100 pb-2">
          <span className="text-slate-500">Started</span>
          <span className="font-medium text-slate-800">{mission.startedAt}</span>
        </div>

        {mission.endedAt && (
          <div className="flex justify-between items-center border-b border-slate-100 pb-2">
            <span className="text-slate-500">Ended</span>
            <span className="font-medium text-slate-800">{mission.endedAt}</span>
          </div>
        )}

        <div className="flex justify-between items-center">
          <span className="text-slate-500">Mission ID</span>
          <span className="font-mono text-[10px] text-slate-800">{mission.id}</span>
        </div>

        <div className="mt-4 pt-4 border-t border-slate-100">
          {isActive ? (
            <button
              onClick={() => {
                if (confirm(`End mission "${mission.name}"?`)) {
                  endMission();
                }
              }}
              className="w-full py-2 bg-danger hover:bg-red-700 text-white font-bold rounded shadow-sm transition-colors flex items-center justify-center gap-2"
            >
              <Icon name="warning-circle" />
              End Mission
            </button>
          ) : (
            <button
              onClick={() => {
                startMission('Maragondon, Cavite Search');
              }}
              className="w-full py-2 bg-aeris hover:bg-aeris-dark text-white font-bold rounded shadow-sm transition-colors flex items-center justify-center gap-2"
            >
              <Icon name="check" />
              Start New Mission
            </button>
          )}
        </div>

        {!isActive && mission.endedAt && (
          <div className="text-[10px] text-slate-500 italic mt-2 text-center">
            Mission ended at {mission.endedAt}
          </div>
        )}
      </div>
    </div>
  );
}
