import {
  Chart as ChartJS,
  CategoryScale, LinearScale, BarElement,
  PointElement, LineElement,
  Tooltip, Legend, Filler,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale, LinearScale, BarElement,
  PointElement, LineElement,
  Tooltip, Legend, Filler
);

const ACTIVE_COLOR = '#2563eb';
const MUTED_COLOR  = '#cbd5e1';

export default function CostCurve({ scenarios, activeIdx, onSelect }) {
  const labels = scenarios.map(s => `${s.k}-WH`);
  const values = scenarios.map(s => s.avg_distance_per_capita_mi);

  // % savings vs previous k
  const savings = scenarios.map((s, i) =>
    i === 0 ? null
    : (((scenarios[i - 1].avg_distance_per_capita_mi - s.avg_distance_per_capita_mi)
        / scenarios[i - 1].avg_distance_per_capita_mi) * 100).toFixed(1)
  );

  const data = {
    labels,
    datasets: [
      {
        label: 'Avg Distance / Capita (mi)',
        data: values,
        backgroundColor: scenarios.map((_, i) =>
          i === activeIdx ? ACTIVE_COLOR : MUTED_COLOR
        ),
        borderRadius: 6,
        borderSkipped: false,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    onClick: (_, elements) => {
      if (elements.length) onSelect(elements[0].index);
    },
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: (ctx) => {
            const i = ctx.dataIndex;
            const base = ` Avg ${ctx.parsed.y.toFixed(1)} mi/capita`;
            return savings[i] ? [base, ` -${savings[i]}% vs ${scenarios[i-1].k}-WH`] : [base];
          },
        },
        backgroundColor: '#ffffff',
        borderColor: '#e2e8f0',
        borderWidth: 1,
        titleColor: '#0f172a',
        bodyColor: '#475569',
      },
    },
    scales: {
      x: {
        ticks: { color: '#64748b', font: { size: 11 } },
        grid: { display: false },
        border: { color: '#cbd5e1' },
      },
      y: {
        ticks: {
          color: '#64748b',
          font: { size: 11 },
          callback: (v) => `${v} mi`,
        },
        grid: { color: '#f1f5f9' },
        border: { color: '#cbd5e1' },
        title: {
          display: true,
          text: 'Avg Distance / Capita (miles)',
          color: '#94a3b8',
          font: { size: 11 },
        },
      },
    },
  };

  return (
    <div>
      {/* Savings annotation row */}
      <div className="flex mb-3">
        <div className="w-10" />
        {scenarios.map((s, i) => (
          <div key={s.k} className="flex-1 text-center">
            {savings[i] ? (
              <span className="text-[10px] font-semibold text-emerald-600">
                -{savings[i]}%
              </span>
            ) : (
              <span className="text-[10px] text-slate-400">base</span>
            )}
          </div>
        ))}
      </div>

      <div style={{ height: 220 }}>
        <Bar data={data} options={options} />
      </div>

      <p className="text-[10px] text-slate-400 text-center mt-2">
        Click a bar to switch scenario · Elbow at k=5 (~24% marginal savings, then diminishing returns)
      </p>
    </div>
  );
}
