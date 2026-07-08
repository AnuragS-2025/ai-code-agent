export default function StatCard({
  title,
  value,
  color,
  icon,
}) {
  return (
    <div className="bg-slate-900 rounded-xl p-6 shadow-md border border-slate-800 hover:border-cyan-500 transition">
      <div className="flex justify-between items-center">
        <div>
          <p className="text-slate-400 text-sm">
            {title}
          </p>

          <h2 className={`text-3xl font-bold mt-2 ${color}`}>
            {value}
          </h2>
        </div>

        <div className="text-4xl">
          {icon}
        </div>
      </div>
    </div>
  );
}