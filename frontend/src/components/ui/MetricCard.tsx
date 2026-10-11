type MetricAccent = "charcoal" | "blue" | "green" | "rust";

type MetricCardProps = {
  value: string;
  unit: string;
  label: string;
  note: string;
  accent?: MetricAccent;
};

const accentClasses: Record<MetricAccent, string> = {
  charcoal: "border-t-[#1a1a1a]",
  blue: "border-t-[#2c5282]",
  green: "border-t-[#385e42]",
  rust: "border-t-[#c05621]",
};

export default function MetricCard({
  value,
  unit,
  label,
  note,
  accent = "charcoal",
}: MetricCardProps) {
  return (
    <article
      aria-label={`${value} ${label}`}
      className={`border-t-2 px-4 py-4 outline-none transition-colors hover:bg-[#fdf9f0] lg:py-3 ${accentClasses[accent]}`}
    >
      <div className="flex items-baseline gap-2">
        <span className="font-newsreader text-5xl leading-none text-[#1a1a1a]">
          {value}
        </span>
        <span className="font-mono text-[9px] uppercase text-[#717171]">
          {unit}
        </span>
      </div>
      <div className="mt-2 font-mono text-[10px] font-semibold uppercase tracking-wider text-[#1a1a1a]">
        {label}
      </div>
      <div className="mt-1 text-[10px] leading-4 text-[#717171]">
        {note}
      </div>
    </article>
  );
}


