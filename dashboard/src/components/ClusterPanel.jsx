import { CLUSTER_COLORS } from '../data';

export default function ClusterPanel({ scenario }) {
  return (
    <div className="h-full flex flex-col bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
      <div className="px-4 py-3 border-b border-slate-200">
        <h2 className="text-xs font-semibold uppercase tracking-widest text-slate-500">
          Warehouse Clusters
        </h2>
      </div>
      <div className="overflow-y-auto flex-1 p-3 space-y-2">
        {scenario.warehouses.map((cluster, ci) => {
          const color = CLUSTER_COLORS[ci % CLUSTER_COLORS.length];
          const fac = cluster.facility;
          const pop = (cluster.served_population / 1e6).toFixed(1);
          return (
            <div
              key={ci}
              className="rounded-lg bg-slate-50 border border-slate-200 p-3"
              style={{ borderLeftColor: color, borderLeftWidth: 3 }}
            >
              <div className="flex items-center gap-2 mb-2">
                <span
                  className="w-2.5 h-2.5 rounded-full flex-shrink-0"
                  style={{ background: color }}
                />
                <span className="text-sm font-semibold text-slate-900">
                  {fac.city}, {fac.state_id}
                </span>
              </div>
              <div className="grid grid-cols-3 gap-1 text-center">
                <Stat label="Cities" value={cluster.served_cities} />
                <Stat label="Population" value={`${pop}M`} />
                <Stat label="Avg Dist" value={`${cluster.avg_weighted_distance_mi} mi`} />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function Stat({ label, value }) {
  return (
    <div className="bg-white border border-slate-200 rounded px-1 py-1.5">
      <div className="text-[9px] uppercase tracking-wider text-slate-400">{label}</div>
      <div className="text-xs font-semibold text-slate-700 mt-0.5">{value}</div>
    </div>
  );
}
