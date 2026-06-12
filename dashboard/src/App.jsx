import { useState } from 'react';
import { scenarios } from './data';
import ScenarioPicker from './components/ScenarioPicker';
import KPIStrip from './components/KPIStrip';
import MapView from './components/MapView';
import CostCurve from './components/CostCurve';
import ClusterPanel from './components/ClusterPanel';

export default function App() {
  const [activeIdx, setActiveIdx] = useState(2); // k=5 default (elbow)
  const scenario = scenarios[activeIdx];
  const baseline = scenarios[0]; // k=3

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">

      {/* Header */}
      <header className="border-b border-slate-200 bg-white px-6 py-4">
        <div className="max-w-screen-xl mx-auto flex flex-col sm:flex-row sm:items-center gap-3">
          <div className="flex-1">
            <h1 className="text-lg font-bold tracking-tight text-slate-900">
              US Warehouse Network Optimizer
            </h1>
            <p className="text-xs text-slate-500 mt-0.5">
              P-Median facility-location model · 75 demand nodes · population-weighted distance
            </p>
          </div>
          <ScenarioPicker
            scenarios={scenarios}
            activeIdx={activeIdx}
            onChange={setActiveIdx}
          />
        </div>
      </header>

      <main className="max-w-screen-xl mx-auto px-6 py-5 space-y-5">

        {/* KPIs */}
        <KPIStrip scenario={scenario} baseline={baseline} />

        {/* Map + Cluster panel */}
        <div className="flex gap-4 h-[500px]">
          <div className="flex-1 rounded-xl overflow-hidden border border-slate-200 shadow-sm">
            <MapView scenario={scenario} />
          </div>
          <div className="w-72 flex-shrink-0">
            <ClusterPanel scenario={scenario} />
          </div>
        </div>

        {/* Cost curve */}
        <div className="rounded-xl border border-slate-200 bg-white shadow-sm p-5">
          <h2 className="text-sm font-semibold text-slate-600 mb-4 uppercase tracking-wider">
            Cost vs. Network Size
          </h2>
          <CostCurve
            scenarios={scenarios}
            activeIdx={activeIdx}
            onSelect={setActiveIdx}
          />
        </div>

        {/* Footer */}
        <p className="text-center text-[10px] text-slate-400 pb-4">
          DATA: SIMPLEMAPS USCITIES v1.93 · MODEL: P-MEDIAN GREEDY + LOCAL SEARCH · NOT FOR OPERATIONAL USE
        </p>
      </main>
    </div>
  );
}
