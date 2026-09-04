import { DetectionsTable } from '../components/DetectionsTable';

export function DetectionsPage() {
  return (
    <div className="h-full">
      <div className="panel-card min-h-full flex flex-col">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6 border-b border-slate-100 pb-4">
          <div>
            <h2 className="text-xl font-bold text-slate-800 uppercase">Detections</h2>
            <p className="text-xs text-slate-500 mt-1">List of all detections.</p>
          </div>
        </div>
        <DetectionsTable />
      </div>
    </div>
  );
}
