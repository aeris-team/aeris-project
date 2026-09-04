import { LiveFeed } from '../components/LiveFeed';
import { MissionMap } from '../components/MissionMap';
import { CommLinkHealth } from '../components/CommLinkHealth';
import { DetectionsTable } from '../components/DetectionsTable';
import { ActiveMission } from '../components/ActiveMission';

export function Dashboard() {
  return (
    <div className="h-full flex flex-col gap-4 lg:gap-6 max-w-[1600px] mx-auto">
      {/* Top Row: Video, Map, Link/Telemetry */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 lg:gap-6 lg:h-[55%] shrink-0">
        <LiveFeed />
        <MissionMap />
        <CommLinkHealth />
      </div>

      {/* Bottom Row: Detections Table & Mission Info */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 lg:gap-6 flex-1 min-h-[400px] lg:min-h-0 overflow-hidden">
        <DetectionsTable />
        <ActiveMission />
      </div>
    </div>
  );
}
