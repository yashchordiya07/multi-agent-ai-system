export default function BulletList({ items = [], dotClass = "bg-slate-500", empty = "None" }) {
  if (!items.length) return <p className="text-sm text-slate-600 italic">{empty}</p>;
  return (
    <ul className="space-y-2">
      {items.map((item, i) => (
        <li key={i} className="flex items-start gap-2.5 text-sm text-slate-300 leading-relaxed">
          <span className={`dot ${dotClass}`} />
          <span>{item}</span>
        </li>
      ))}
    </ul>
  );
}
