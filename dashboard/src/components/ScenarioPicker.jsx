export default function ScenarioPicker({ scenarios, activeIdx, onChange }) {
  return (
    <div className="flex gap-1 bg-slate-100 rounded-lg p-1 border border-slate-200">
      {scenarios.map((s, i) => (
        <button
          key={s.k}
          onClick={() => onChange(i)}
          className={`px-3 py-1.5 rounded-md text-xs font-semibold transition-all ${
            i === activeIdx
              ? 'bg-blue-600 text-white shadow-sm'
              : 'text-slate-500 hover:text-slate-800 hover:bg-white'
          }`}
        >
          {s.k}-WH
        </button>
      ))}
    </div>
  );
}
