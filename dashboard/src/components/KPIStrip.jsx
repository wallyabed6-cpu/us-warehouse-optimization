const fmt = (n) => n.toLocaleString('en-US', { maximumFractionDigits: 1 });

function KPI({ label, value, sub, highlight }) {
  return (
    <div className="flex-1 bg-white rounded-xl border border-slate-200 shadow-sm px-5 py-4">
      <div className="text-[10px] uppercase tracking-widest text-slate-400 mb-1">{label}</div>
      <div className={`text-2xl font-bold ${highlight ? 'text-blue-600' : 'text-slate-900'}`}>{value}</div>
      {sub && <div className="text-xs text-slate-400 mt-0.5">{sub}</div>}
    </div>
  );
}

export default function KPIStrip({ scenario, baseline }) {
  const savings = ((1 - scenario.avg_distance_per_capita_mi / baseline.avg_distance_per_capita_mi) * 100).toFixed(1);
  const totalPop = (scenario.total_demand_population / 1e6).toFixed(1);
  const costIndex = (scenario.avg_distance_per_capita_mi / baseline.avg_distance_per_capita_mi * 100).toFixed(0);

  return (
    <div className="flex gap-3">
      <KPI
        label="Warehouses"
        value={scenario.k}
        sub={scenario.scenario}
      />
      <KPI
        label="Avg Distance / Capita"
        value={`${fmt(scenario.avg_distance_per_capita_mi)} mi`}
        sub="population-weighted"
        highlight
      />
      <KPI
        label="Demand Population"
        value={`${totalPop}M`}
        sub="top-75 US cities"
      />
      <KPI
        label="Cost vs 3-WH Baseline"
        value={scenario.k === 3 ? '—' : `-${savings}%`}
        sub={`index: ${costIndex} (base=100)`}
        highlight={scenario.k !== 3}
      />
    </div>
  );
}
