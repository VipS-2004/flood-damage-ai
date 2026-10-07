type RoadRecord = {
  id: string;
  roadClass: string;
  total: string;
  overlap: string;
  percent: string;
};

type EvidenceLedgerTableProps = {
  roads: RoadRecord[];
};

const roadClassStyles: Record<string, string> = {
  path: "border-[#c05621]/40 bg-[#f0ddd5] text-[#694236]",
  unclassified: "border-[#d8d5cc] bg-[#efece4] text-[#4a4a4a]",
  trunk: "border-[#2c5282]/40 bg-[#e3eaf2] text-[#2c5282]",
  primary: "border-[#385e42]/40 bg-[#e4ebe4] text-[#385e42]",
};

export default function EvidenceLedgerTable({
  roads,
}: EvidenceLedgerTableProps) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[640px] border-collapse text-left font-mono text-[10px]">
        <caption className="sr-only">
          Potentially affected road segments and evidence overlap ledger
        </caption>
        <thead className="border-b border-[#1a1a1a] bg-[#efece4] text-[#717171]">
          <tr>
            <th className="px-4 py-3 font-semibold tracking-[0.04em]">OSM ID</th>
            <th className="px-4 py-3 font-semibold tracking-[0.04em]">ROAD CLASS</th>
            <th className="px-4 py-3 text-right font-semibold tracking-[0.04em]">TOTAL</th>
            <th className="px-4 py-3 text-right font-semibold tracking-[0.04em] text-[#c05621]">OVERLAP</th>
            <th className="px-4 py-3 text-right font-semibold tracking-[0.04em] text-[#2c5282]">OVERLAP %</th>
          </tr>
        </thead>
        <tbody>
          {roads.map((road) => (
            <tr
              key={road.id}
              className="border-b border-[#e2dfd7] outline-none transition-colors hover:bg-[#f4f2ec]"
            >
              <td className="whitespace-nowrap px-4 py-3 text-[#4a4a4a]">{road.id}</td>
              <td className="px-4 py-3 uppercase">
                <span className={`inline-flex border px-2 py-1 text-[9px] tracking-[0.04em] ${roadClassStyles[road.roadClass] ?? "border-[#d8d5cc] bg-[#efece4] text-[#4a4a4a]"}`}>
                  {road.roadClass}
                </span>
              </td>
              <td className="whitespace-nowrap px-4 py-3 text-right text-[#4a4a4a]">{road.total}</td>
              <td className="whitespace-nowrap px-4 py-3 text-right font-semibold text-[#c05621]">{road.overlap}</td>
              <td className="whitespace-nowrap px-4 py-3 text-right font-semibold text-[#2c5282]">{road.percent}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}


