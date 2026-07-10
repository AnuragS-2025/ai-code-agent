export default function StatCard({
  title = "Metric",
  value = "-",
  color = "text-slate-400",
  icon,
}) {
  return (
    <div className="bg-slate-900 rounded-xl p-6 shadow-md border border-slate-800 hover:border-slate-700 transition-all duration-300 group cursor-default">
      <div className="flex justify-between items-center">
        <div className="space-y-1">
          <p className="text-slate-500 text-[11px] font-bold uppercase tracking-wider font-mono">
            {title}
          </p>

          <h2 className={`text-3xl font-bold font-mono ${color}`}>
            {value}
          </h2>
        </div>

        <div className={`text-3xl p-3 bg-slate-950 rounded-xl border border-slate-800/60 ${color} opacity-80 group-hover:scale-110 group-hover:opacity-100 transition-all duration-300 shadow-inner`}>
          {icon}
        </div>
      </div>
    </div>
  );
}