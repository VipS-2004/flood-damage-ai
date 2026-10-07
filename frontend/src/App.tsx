import { useState } from "react";
import SegmentedEvidenceSwitcher from "./components/SegmentedEvidenceSwitcher";
import MetricCard from "./components/MetricCard";
import EvidenceLedgerTable from "./components/EvidenceLedgerTable";
import {
  Crosshair,
  ArrowUpRight,
  Layers3,
  Minus,
  Navigation,
  Plus,
  RotateCcw,
} from "lucide-react";


type MapMode =
  | "impact"
  | "sar"
  | "drainage"
  | "beforeAfter";


const mapImages: Record<MapMode, string> = {
  impact: "/evidence/final_impact_map.png",
  sar: "/evidence/gamma0terrain_change.png",
  drainage: "/evidence/drainage_corridor_100m.png",
  beforeAfter: "/evidence/event_s1_before_after.png",
};


const mapLabels: Record<MapMode, string> = {
  impact: "Impact Map",
  sar: "SAR Change",
  drainage: "Drainage Network",
  beforeAfter: "Before / After",
};


const roadData = [
  {
    id: "248708067",
    roadClass: "path",
    total: "0.45 km",
    overlap: "82.9 m",
    percent: "18.44%",
  },
  {
    id: "937405879",
    roadClass: "unclassified",
    total: "1.69 km",
    overlap: "202.1 m",
    percent: "11.97%",
  },
  {
    id: "1523551262",
    roadClass: "path",
    total: "0.31 km",
    overlap: "27.0 m",
    percent: "8.85%",
  },
  {
    id: "904894051",
    roadClass: "trunk",
    total: "0.62 km",
    overlap: "26.5 m",
    percent: "4.31%",
  },
  {
    id: "248705796",
    roadClass: "primary",
    total: "3.83 km",
    overlap: "79.5 m",
    percent: "2.08%",
  },
];


const settlementData = [
  {
    settlement: "Dhunche",
    status: "NO_CHANGE",
    baseline: "0.36 km",
    scenario: "0.36 km",
    delta: "0.00 km",
  },
  {
    settlement: "Brabal",
    status: "NO_CHANGE",
    baseline: "0.49 km",
    scenario: "0.49 km",
    delta: "0.00 km",
  },
  {
    settlement: "Gosaikunda",
    status: "NO_CHANGE",
    baseline: "0.52 km",
    scenario: "0.52 km",
    delta: "0.00 km",
  },
  {
    settlement: "Sano Bharkhu",
    status: "NO_CHANGE",
    baseline: "3.21 km",
    scenario: "3.21 km",
    delta: "0.00 km",
  },
  {
    settlement: "Thulo SyÄbru",
    status: "NO_CHANGE",
    baseline: "3.86 km",
    scenario: "3.86 km",
    delta: "0.00 km",
  },
  {
    settlement: "Dursagang",
    status: "NO_CHANGE",
    baseline: "5.40 km",
    scenario: "5.40 km",
    delta: "0.00 km",
  },
  {
    settlement: "Syabru Bensi",
    status: "NO_CHANGE",
    baseline: "7.38 km",
    scenario: "7.38 km",
    delta: "0.00 km",
  },
];


function SectionHeader({
  number,
  title,
  description,
}: {
  number: string;
  title: string;
  description: string;
}) {
  return (
    <div className="flex flex-col gap-4 border-b border-[#d8d5cc] pb-3 md:flex-row md:items-end md:justify-between">
      <div>
        <div className="font-mono text-[10px] font-semibold uppercase tracking-[0.14em] text-[#2c5282]">
          {number}
        </div>

        <h2 className="mt-1 font-newsreader text-3xl leading-none text-[#1a1a1a] md:text-[34px]">
          {title}
        </h2>
      </div>

      <p className="max-w-xl text-right text-xs leading-5 text-[#717171]">
        {description}
      </p>
    </div>
  );
}


function StatusPill({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <span className="inline-flex items-center gap-1.5 border border-[#d8d5cc] bg-[#f4f2ec] px-2 py-1 font-mono text-[9px] uppercase tracking-[0.05em] text-[#4a4a4a]">
      <span className="h-1.5 w-1.5 bg-[#385e42]" />
      {children}
    </span>
  );
}


function Dashboard() {
  const [mapMode, setMapMode] = useState<MapMode>("impact");
  const [zoom, setZoom] = useState(1);


  const changeZoom = (value: number) => {
    setZoom((current) =>
      Math.min(1.35, Math.max(0.8, current + value))
    );
  };


  const resetZoom = () => {
    setZoom(1);
  };


  return (
    <div className="min-h-screen bg-[#fdf9f0] text-[#1a1a1a]">
      <header className="sticky top-0 z-50 border-b border-[#c4c7c7]/70 bg-[#fdf9f0]">
        <div className="mx-auto flex h-16 max-w-[1440px] items-center justify-between gap-6 px-5 md:px-10">
          <div className="flex items-center gap-4">
            <div className="flex items-baseline font-mono text-sm font-bold uppercase tracking-[0.08em]">
              <span>FLOOD</span>
              <span className="mx-1 text-[#717171]">/</span>
              <span className="font-newsreader text-base italic font-normal">
                INTELLIGENCE
              </span>
            </div>

            <div className="hidden h-5 w-px bg-[#d8d5cc] lg:block" />

            <div className="hidden items-center gap-3 font-mono text-[9px] uppercase tracking-[0.08em] text-[#717171] xl:flex">
              <StatusPill>Analysis Ready</StatusPill>

              <span>Rasuwa Corridor</span>
              <span>|</span>
              <span>26.08.2026</span>
              <span>|</span>

              <span className="text-[#2c5282]">
                Copernicus Sentinel-1 + DEM
              </span>
            </div>
          </div>

          <nav className="hidden items-center gap-4 font-mono text-[9px] uppercase tracking-[0.06em] text-[#717171] lg:flex">
            <a
              href="#overview"
              className="border-b border-[#1a1a1a] py-1 text-[#1a1a1a]"
            >
              01 Overview
            </a>

            <a
              href="#observe"
              className="py-1 hover:text-[#1a1a1a]"
            >
              02 Read Landscape
            </a>

            <a
              href="#chain"
              className="py-1 hover:text-[#1a1a1a]"
            >
              03 Analytical Chain
            </a>

            <a
              href="#exposure"
              className="py-1 hover:text-[#1a1a1a]"
            >
              04 Exposure
            </a>

            <a
              href="#accessibility"
              className="py-1 hover:text-[#1a1a1a]"
            >
              05 Accessibility
            </a>
          </nav>

          <div className="flex h-7 w-7 items-center justify-center bg-[#1a1a1a]">
            <Navigation size={14} className="text-[#fdf9f0]" />
          </div>
        </div>
      </header>


      <main>
        <div className="mx-auto flex max-w-[1440px] flex-col gap-10 px-5 pb-24 pt-5 md:px-10">
          <section
            id="overview"
            className="flex flex-col gap-4"
          >
            <div className="flex flex-col gap-2 border-b border-[#d8d5cc] pb-3 md:flex-row md:items-center md:justify-between">
              <div className="font-mono text-[9px] uppercase tracking-[0.08em] text-[#717171]">
                <span className="font-semibold text-[#1a1a1a]">
                  GEO-RAPID REPORT // RASUWA-0826
                </span>
                <span className="mx-2">/</span>
                LANGTANG HIMALAYAN SECTOR
                <span className="mx-2">/</span>
                UTM ZONE 45N
              </div>

              <div className="font-mono text-[9px] uppercase tracking-[0.08em] text-[#717171]">
                LAT 28Â°10â€²N Â· LON 85Â°22â€²E
                <span className="mx-3 text-[#c4c7c7]">|</span>
                ANALYTICAL PROTOTYPE
              </div>
            </div>


            <div className="relative overflow-hidden border border-[#d8d5cc] bg-[#f1eee4]">
              <div className="absolute left-3 top-2 z-20 border border-[#d8d5cc]/70 bg-[#fdf9f0]/90 px-1 py-0.5 font-mono text-[8px] tracking-widest text-[#717171]">
                N28Â°15'00" â€” E85Â°10'00"
              </div>

              <div className="absolute right-3 top-2 z-20 border border-[#d8d5cc]/70 bg-[#fdf9f0]/90 px-1 py-0.5 font-mono text-[8px] tracking-widest text-[#717171]">
                N28Â°15'00" â€” E85Â°30'00"
              </div>


              <div className="relative h-[430px] overflow-hidden md:h-[580px]">
                <img
                  src="/evidence/final_impact_map.png"
                  alt="Flood impact evidence map"
                  className="h-full w-full object-cover"
                />

                <div className="pointer-events-none absolute inset-0 bg-gradient-to-r from-[#f4f1e9]/90 via-[#f4f1e9]/15 to-transparent" />


                <div className="absolute left-5 top-5 z-20 max-w-md border border-[#747878]/50 bg-[#fdf9f0]/95 p-4 md:left-6 md:top-6">
                  <div className="mb-2 flex items-center justify-between border-b border-[#d8d5cc] pb-2 font-mono text-[9px] uppercase tracking-widest text-[#717171]">
                    <span>Satellite Damage Intelligence</span>

                    <span className="text-[#2c5282]">
                      Evidence View
                    </span>
                  </div>

                  <h1 className="font-newsreader text-[38px] leading-[0.98] text-[#1a1a1a] md:text-[50px]">
                    Flood from space.
                    <br />
                    <span className="italic">
                      Impact on the ground.
                    </span>
                  </h1>

                  <p className="mt-3 max-w-lg text-sm leading-6 text-[#4a4a4a]">
                    A satellite-driven analysis of flood-related
                    change, terrain pathways, infrastructure
                    exposure and settlement accessibility across
                    the Rasuwa corridor.
                  </p>

                  <div className="mt-4 grid grid-cols-2 gap-x-4 gap-y-2 border-t border-[#d8d5cc] pt-3 font-mono text-[9px] text-[#717171]">
                    <div>
                      <span>EVENT:</span>{" "}
                      <span className="font-semibold text-[#1a1a1a]">
                        26 AUG 2026
                      </span>
                    </div>

                    <div>
                      <span>OSM:</span>{" "}
                      <span className="font-semibold text-[#1a1a1a]">
                        27 JUL 2026
                      </span>
                    </div>

                    <div className="col-span-2">
                      <span>RADAR PAIR:</span>{" "}
                      <span className="font-semibold text-[#1a1a1a]">
                        16 â†’ 28 AUG 2026
                      </span>
                    </div>

                    <div className="col-span-2">
                      <span>ELEVATION:</span>{" "}
                      <span className="font-semibold text-[#1a1a1a]">
                        Copernicus DEM GLO-30
                      </span>
                    </div>
                  </div>
                </div>


                <div className="absolute bottom-5 right-5 z-20 hidden items-center gap-4 border border-[#747878]/50 bg-[#fdf9f0]/95 px-4 py-3 font-mono text-[9px] md:flex">
                  <div>
                    <div className="uppercase tracking-wider text-[#717171]">
                      METRIC SCALE
                    </div>
                    <div className="mt-1 flex items-center gap-2">
                      <div className="flex h-2 w-24 border-x border-b border-[#1a1a1a]">
                        <div className="w-1/3 bg-[#1a1a1a]" />
                        <div className="w-1/3 border-r border-[#1a1a1a]" />
                        <div className="w-1/3 bg-[#1a1a1a]" />
                      </div>

                      <span>0 â€” 5 â€” 15 km</span>
                    </div>
                  </div>

                  <div className="h-6 w-px bg-[#d8d5cc]" />

                  <div className="flex items-center gap-2">
                    <Crosshair size={16} />
                    <div>
                      <div>TRUE N</div>
                      <div className="text-[#717171]">
                        DECL +0.2Â°
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>


          <section className="border-y border-[#d8d5cc] bg-[#f7f3ea]/40 py-4">
            <div className="grid grid-cols-1 divide-y divide-[#d8d5cc] md:grid-cols-2 md:divide-y-0 lg:grid-cols-4 lg:divide-x">
              <MetricCard
                accent="charcoal"
                label="Settlements Analysed"
                note="49 reachable in baseline network"
                unit="LOCI"
                value="57"
              />
              <MetricCard
                accent="rust"
                label="Potentially Affected Roads"
                note="SAR evidence intersection"
                unit="SEGS"
                value="16"
              />
              <MetricCard
                accent="green"
                label="Buildings in Drainage Corridor"
                note="100 m hydrologic corridor"
                unit="BLDG"
                value="529"
              />
              <MetricCard
                accent="blue"
                label="Potentially Affected Bridges"
                note="No bridge intersected current SAR evidence"
                unit="SEV"
                value="0"
              />
            </div>
          </section>


          <section
            id="observe"
            className="flex flex-col gap-4"
          >
            <SectionHeader
              number="01 / OBSERVE"
              title="Read the landscape"
              description="Inspection of terrain-corrected Sentinel-1 radar change alongside the drainage structure used to contextualise potential impact."
            />


            <div className="border border-[#d8d5cc] bg-[#f7f3ea]">
              <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[#d8d5cc] bg-[#ebe8df] px-3 py-2">
                <SegmentedEvidenceSwitcher
                  value={mapMode}
                  onChange={setMapMode}
                  options={[
                    { value: "impact", label: "Impact Map" },
                    { value: "sar", label: "SAR Change" },
                    { value: "drainage", label: "Drainage Network" },
                    { value: "beforeAfter", label: "Before / After" },
                  ]}
                />


                <div className="flex items-center gap-1 font-mono text-[9px] uppercase text-[#717171]">
                  <span className="mr-1">
                    VIEWPORT {Math.round(zoom * 100)}%
                  </span>

                  <button
                    aria-label="Zoom in"
                    onClick={() => changeZoom(0.1)}
                    className="flex h-7 w-7 items-center justify-center border border-[#d8d5cc] bg-[#fdf9f0]"
                  >
                    <Plus size={14} />
                  </button>

                  <button
                    aria-label="Zoom out"
                    onClick={() => changeZoom(-0.1)}
                    className="flex h-7 w-7 items-center justify-center border border-[#d8d5cc] bg-[#fdf9f0]"
                  >
                    <Minus size={14} />
                  </button>

                  <button
                    aria-label="Reset zoom"
                    onClick={resetZoom}
                    className="flex h-7 items-center gap-1 border border-[#d8d5cc] bg-[#fdf9f0] px-2"
                  >
                    <RotateCcw size={12} />
                    Reset
                  </button>
                </div>
              </div>


              <div className="relative h-[420px] overflow-hidden bg-[#e5e2d9] md:h-[560px]">
                <img
                  src={mapImages[mapMode]}
                  alt={mapLabels[mapMode]}
                  className="h-full w-full object-cover transition-transform duration-300"
                  style={{
                    transform: `scale(${zoom})`,
                  }}
                />


                <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
                  <div className="relative flex h-16 w-16 items-center justify-center border border-dashed border-[#1a1a1a]/40">
                    <div className="h-2 w-2 bg-[#c05621]" />

                    <div className="absolute -top-6 whitespace-nowrap bg-[#1a1a1a] px-1.5 py-1 font-mono text-[9px] tracking-widest text-white">
                      ANALYSIS CENTRE
                    </div>
                  </div>
                </div>


                <div className="absolute bottom-4 left-4 border border-[#1a1a1a] bg-[#fdf9f0]/95 p-3 font-mono text-[9px]">
                  <div className="mb-2 border-b border-[#d8d5cc] pb-1 font-semibold uppercase tracking-wider">
                    Cartographic overlays
                  </div>

                  <div className="flex items-center gap-2 py-0.5">
                    <span className="h-3 w-3 bg-[#c05621]" />
                    <span>
                      SAR evidence
                    </span>
                  </div>

                  <div className="flex items-center gap-2 py-0.5">
                    <span className="h-1 w-3 bg-[#2c5282]" />
                    <span>
                      Main drainage
                    </span>
                  </div>

                  <div className="flex items-center gap-2 py-0.5">
                    <span className="h-3 w-3 border border-[#385e42]" />
                    <span>
                      Hydrologic corridor
                    </span>
                  </div>
                </div>


                <div className="absolute right-4 top-4 border border-[#1a1a1a] bg-[#fdf9f0]/95 p-3">
                  <div className="flex items-center gap-2 font-mono text-[9px] uppercase">
                    <Layers3 size={13} />
                    <span>{mapLabels[mapMode]}</span>
                  </div>
                </div>
              </div>
            </div>


            <div className="border-l-2 border-[#c05621] bg-[#f0ddd5] px-4 py-3 text-xs leading-5 text-[#694236]">
              <strong>Reading the evidence:</strong>{" "}
              Sentinel-1 radar change is treated as potential
              flood-related surface change. The signal is interpreted
              alongside terrain-derived drainage structure rather than
              as a confirmed operational flood boundary.
            </div>
          </section>


          <section id="chain" className="flex flex-col gap-4">
            <SectionHeader
              number="02 / TRACE"
              title="From terrain to impact"
              description="The workflow connects satellite observations with terrain structure and pre-event infrastructure to move from signal toward consequence."
            />


            <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
              {[
                [
                  "01",
                  "OBSERVE",
                  "Sentinel-1",
                  "Compare before and after radar observations for potential surface change.",
                ],
                [
                  "02",
                  "TRACE",
                  "Copernicus DEM",
                  "Use flow accumulation and terrain structure to trace the main drainage pathways.",
                ],
                [
                  "03",
                  "OVERLAY",
                  "Pre-event OSM",
                  "Intersect the analytical evidence with buildings, roads and bridges from the 27 July 2026 snapshot.",
                ],
              ].map(([number, title, input, text]) => (
                <div
                  key={number}
                  className="border border-[#d8d5cc] bg-[#f7f3ea] p-4"
                >
                  <div className="flex items-center justify-between border-b border-[#d8d5cc] pb-2 font-mono text-[9px]">
                    <span className="font-semibold">
                      STEP {number}
                    </span>

                    <span className="text-[#717171]">
                      INPUT: {input}
                    </span>
                  </div>

                  <h3 className="mt-4 font-newsreader text-xl">
                    {title}
                  </h3>

                  <p className="mt-2 text-xs leading-5 text-[#717171]">
                    {text}
                  </p>
                </div>
              ))}
            </div>
          </section>


          <section id="exposure" className="flex flex-col gap-4">
            <SectionHeader
              number="03 / IMPACT"
              title="What could be affected?"
              description="Infrastructure intersecting the analytical evidence is classified as potentially affected, not confirmed damaged."
            />


            <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
              {[
                [
                  "BUILDINGS",
                  "529",
                  "Buildings inside the 100 m drainage corridor.",
                ],
                [
                  "ROADS",
                  "16",
                  "Road features intersecting SAR evidence.",
                ],
                [
                  "BRIDGES",
                  "0",
                  "No bridge feature intersected current joint SAR evidence.",
                ],
              ].map(([label, value, description]) => (
                <div
                  key={label}
                  className="border border-[#d8d5cc] bg-[#f7f3ea] p-4"
                >
                  <div className="font-mono text-[9px] uppercase tracking-wider text-[#717171]">
                    {label}
                  </div>

                  <div className="mt-2 font-newsreader text-5xl leading-none">
                    {value}
                  </div>

                  <div className="mt-3 border-t border-[#d8d5cc] pt-3 text-xs leading-5 text-[#717171]">
                    {description}
                  </div>
                </div>
              ))}
            </div>


            <div className="overflow-x-auto border border-[#d8d5cc] bg-[#f7f3ea]">
              <div className="flex items-center justify-between border-b border-[#d8d5cc] bg-[#ebe8df] px-4 py-3 font-mono text-[9px] uppercase">
                <span className="font-semibold">
                  Potentially affected road segments
                </span>

                <span className="text-[#717171]">
                  Evidence overlap ledger
                </span>
              </div>

              <EvidenceLedgerTable roads={roadData} />
            </div>
          </section>


          <section
            id="accessibility"
            className="flex flex-col gap-4"
          >
            <SectionHeader
              number="04 / ACCESSIBILITY"
              title="Who could lose access?"
              description="The pre-event road graph is compared with a disruption scenario in which potentially affected road segments are removed."
            />


            <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
              {[
                [
                  "BASELINE REACHABLE",
                  "49",
                  "Normal network access",
                ],
                [
                  "BASELINE UNREACHABLE",
                  "8",
                  "Already disconnected",
                ],
                [
                  "POTENTIALLY CUT OFF",
                  "0",
                  "No route after scenario",
                ],
                [
                  "LONGER ROUTE",
                  "0",
                  "Reachable with detour",
                ],
              ].map(([label, value, note]) => (
                <div
                  key={label}
                  className="border border-[#d8d5cc] bg-[#fdf9f0] p-3"
                >
                  <div className="font-mono text-[9px] uppercase text-[#717171]">
                    {label}
                  </div>

                  <div className="mt-1 font-newsreader text-4xl">
                    {value}
                  </div>

                  <div className="mt-1 text-[10px] text-[#717171]">
                    {note}
                  </div>
                </div>
              ))}
            </div>


            <div className="overflow-x-auto border border-[#d8d5cc] bg-[#f7f3ea]">
              <div className="flex items-center justify-between border-b border-[#d8d5cc] bg-[#ebe8df] px-4 py-3 font-mono text-[9px] uppercase">
                <span className="font-semibold">
                  Settlement connectivity matrix
                </span>

                <span className="text-[#717171]">
                  Hospital accessibility
                </span>
              </div>

              <table className="w-full border-collapse text-left font-mono text-[10px]">
                <thead className="border-b border-[#1a1a1a] bg-[#efece4] text-[#717171]">
                  <tr>
                    <th className="px-4 py-3 font-semibold">
                      SETTLEMENT
                    </th>

                    <th className="px-4 py-3 font-semibold">
                      STATUS
                    </th>

                    <th className="px-4 py-3 font-semibold">
                      BASELINE
                    </th>

                    <th className="px-4 py-3 font-semibold">
                      SCENARIO
                    </th>

                    <th className="px-4 py-3 text-right font-semibold">
                      DELTA
                    </th>
                  </tr>
                </thead>

                <tbody>
                  {settlementData.map((row) => (
                    <tr
                      key={row.settlement}
                      className="border-b border-[#e2dfd7] hover:bg-[#f4f2ec]"
                    >
                      <td className="px-4 py-3 font-medium">
                        {row.settlement}
                      </td>

                      <td className="px-4 py-3">
                        <StatusPill>
                          {row.status}
                        </StatusPill>
                      </td>

                      <td className="px-4 py-3">
                        {row.baseline}
                      </td>

                      <td className="px-4 py-3">
                        {row.scenario}
                      </td>

                      <td className="px-4 py-3 text-right">
                        {row.delta}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>


            <div className="border-l-2 border-[#c05621] bg-[#f0ddd5] px-4 py-3 text-xs leading-5 text-[#694236]">
              <strong>Scenario interpretation:</strong>{" "}
              BASELINE_UNREACHABLE settlements were already disconnected
              in the pre-event network. CUT_OFF is reserved for
              settlements that had a baseline route but lose it under
              the simulated road-disruption scenario.
            </div>
          </section>


          <section
            id="methodology"
            className="flex flex-col gap-4"
          >
            <SectionHeader
              number="05 / METHODOLOGY"
              title="How the analysis works"
              description="A reproducible chain from satellite observation to spatial exposure and network-level consequence."
            />


            <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
              {[
                [
                  "01",
                  "OBSERVE",
                  "Sentinel-1",
                  "Before/after radar comparison.",
                ],
                [
                  "02",
                  "TRACE",
                  "Copernicus DEM",
                  "Drainage and terrain structure.",
                ],
                [
                  "03",
                  "OVERLAY",
                  "OpenStreetMap",
                  "Pre-event infrastructure context.",
                ],
                [
                  "04",
                  "ASSESS",
                  "Road graph",
                  "Hospital accessibility scenario.",
                ],
              ].map(([number, title, input, description]) => (
                <div
                  key={number}
                  className="border-t border-[#d8d5cc] pt-4"
                >
                  <div className="font-mono text-[9px] text-[#2c5282]">
                    {number}
                  </div>

                  <div className="mt-3 font-newsreader text-xl">
                    {title}
                  </div>

                  <div className="mt-1 font-mono text-[9px] uppercase text-[#717171]">
                    {input}
                  </div>

                  <p className="mt-2 text-xs leading-5 text-[#717171]">
                    {description}
                  </p>
                </div>
              ))}
            </div>
          </section>


          <section className="border-t border-[#d8d5cc] pt-5">
            <div className="border border-[#c05621] bg-[#f0ddd5] p-4">
              <div className="flex items-center gap-2 font-mono text-[10px] font-semibold uppercase tracking-wider text-[#694236]">
                <span className="h-2 w-2 bg-[#c05621]" />
                Scientific limitations
              </div>

              <div className="mt-4 grid grid-cols-1 gap-4 text-xs leading-5 text-[#694236] md:grid-cols-3">
                <div>
                  <strong>01 / Remote sensing</strong>
                  <p className="mt-1">
                    SAR evidence represents potential flood-related
                    surface change and is not a confirmed operational
                    flood boundary.
                  </p>
                </div>

                <div>
                  <strong>02 / Asset classification</strong>
                  <p className="mt-1">
                    Infrastructure intersecting the evidence is
                    classified as potentially affected, not confirmed
                    damaged.
                  </p>
                </div>

                <div>
                  <strong>03 / Network scenario</strong>
                  <p className="mt-1">
                    Accessibility disruption is a scenario based on
                    removing potentially affected road segments.
                  </p>
                </div>
              </div>
            </div>
          </section>


          <footer className="flex flex-col justify-between gap-4 border-t border-[#d8d5cc] pt-4 font-mono text-[9px] uppercase tracking-[0.05em] text-[#717171] md:flex-row">
            <div>
              Contains modified Copernicus Sentinel data 2026.
              <br />
              Â© OpenStreetMap contributors.
            </div>

            <div className="text-left md:text-right">
              Educational disaster-response prototype.
              <br />
              Analytical evidence is not a confirmed operational
              damage map.
            </div>
          </footer>
        </div>
      </main>
    </div>
  );
}


function LandingPage() {
  const signals = [["57", "settlements analysed", "text-[#1a1a1a]"], ["16", "potentially affected roads", "text-[#c05621]"], ["529", "buildings in drainage corridor", "text-[#385e42]"], ["0", "potentially affected bridges", "text-[#2c5282]"]];
  const chain = [["01", "Observe", "Sentinel-1", "Radar evidence of flood-related surface change."], ["02", "Trace", "Copernicus DEM", "Terrain pathways that help read how water may move."], ["03", "Overlay", "Pre-event OSM", "Infrastructure and settlement context before the event."], ["04", "Assess", "Road accessibility scenario", "A scenario for how potentially affected segments may alter access."]];
  return <div className="min-h-screen bg-[#fdf9f0] text-[#1a1a1a]">
    <header className="border-b border-[#d8d5cc]"><div className="mx-auto flex max-w-[1440px] items-center justify-between px-5 py-5 md:px-10"><a href="/" className="flex items-baseline font-mono text-sm font-bold uppercase tracking-[0.08em]">FLOOD<span className="mx-1 text-[#717171]">/</span><span className="font-newsreader text-base italic font-normal">INTELLIGENCE</span></a><div className="flex items-center gap-5 font-mono text-[9px] uppercase tracking-[0.09em] text-[#717171]"><span className="hidden md:inline">RASUWA CORRIDOR / 2026</span><a href="/dashboard" className="border-b border-[#1a1a1a] py-1 text-[#1a1a1a]">Open dashboard ↗</a></div></div></header>
    <main>
      <section className="mx-auto grid max-w-[1440px] gap-10 px-5 pb-20 pt-16 md:grid-cols-[1.02fr_0.98fr] md:px-10 md:pb-28 md:pt-24"><div className="flex flex-col justify-center"><div className="mb-7 flex items-center gap-3 font-mono text-[10px] uppercase tracking-[0.16em] text-[#2c5282]"><span className="h-2 w-2 bg-[#2c5282]" /> GEO-RAPID REPORT / RASUWA-0826</div><h1 className="max-w-3xl font-newsreader text-[clamp(4rem,9vw,8.6rem)] leading-[0.82] tracking-[-0.055em]">Flood from space.<br /><span className="italic text-[#2c5282]">Impact on the ground.</span></h1><p className="mt-9 max-w-xl text-base leading-7 text-[#4a4a4a] md:text-lg">A satellite-driven analysis of flood-related change, terrain pathways, infrastructure exposure and settlement accessibility across the Rasuwa corridor.</p><div className="mt-10 flex flex-wrap items-center gap-5"><a href="/dashboard" className="inline-flex items-center gap-3 bg-[#1a1a1a] px-5 py-3 font-mono text-[10px] uppercase tracking-[0.12em] text-[#fdf9f0] hover:bg-[#2c5282]">Explore the analysis <ArrowUpRight size={15} /></a><span className="font-mono text-[9px] uppercase tracking-[0.08em] text-[#717171]">Sentinel-1 + DEM + OSM</span></div></div><figure className="relative min-h-[430px] overflow-hidden border border-[#d8d5cc] bg-[#efece4] md:min-h-[600px]"><img src="/evidence/final_impact_map.png" alt="Final impact evidence map for the Rasuwa corridor" className="h-full w-full object-cover" /><div className="pointer-events-none absolute inset-0 bg-gradient-to-t from-[#1a1a1a]/45 via-transparent to-transparent" /><figcaption className="absolute bottom-0 left-0 right-0 flex justify-between p-4 font-mono text-[9px] uppercase tracking-[0.08em] text-[#fdf9f0]"><span>Evidence view / final impact map</span><span>28 AUG 2026</span></figcaption></figure></section>
      <section className="border-y border-[#d8d5cc] bg-[#f7f3ea]/55"><div className="mx-auto max-w-[1440px] px-5 py-12 md:px-10 md:py-16"><div className="mb-8 border-b border-[#d8d5cc] pb-3"><h2 className="font-mono text-[10px] font-semibold uppercase tracking-[0.15em] text-[#2c5282]">Signal / At a glance</h2></div><div className="grid grid-cols-2 gap-y-8 md:grid-cols-4 md:divide-x md:divide-[#d8d5cc]">{signals.map(([value, label, tone]) => <div key={label} className="md:px-6 first:md:pl-0"><div className={`font-newsreader text-6xl leading-none ${tone}`}>{value}</div><div className="mt-3 max-w-[150px] font-mono text-[10px] font-semibold uppercase leading-4 tracking-[0.06em]">{label}</div></div>)}</div></div></section>
      <section className="mx-auto max-w-[1440px] px-5 py-20 md:px-10 md:py-28"><div className="grid gap-12 md:grid-cols-[0.75fr_1.25fr]"><div><div className="font-mono text-[10px] font-semibold uppercase tracking-[0.15em] text-[#2c5282]">From signal to consequence</div><h2 className="mt-4 max-w-sm font-newsreader text-5xl leading-[0.95] md:text-6xl">A chain of evidence, not a single answer.</h2></div><div className="border-t border-[#d8d5cc]">{chain.map(([number, title, source, description]) => <div key={number} className="grid gap-3 border-b border-[#d8d5cc] py-5 md:grid-cols-[52px_1fr_1.4fr] md:items-baseline md:gap-5"><span className="font-mono text-[10px] text-[#c05621]">{number}</span><div className="font-newsreader text-3xl">{title} <span className="text-[#717171]">—</span></div><div><div className="font-mono text-[10px] uppercase tracking-[0.08em] text-[#2c5282]">{source}</div><p className="mt-2 text-sm leading-6 text-[#717171]">{description}</p></div></div>)}</div></div></section>
      <section className="border-y border-[#d8d5cc] bg-[#efece4]"><div className="mx-auto grid max-w-[1440px] gap-10 px-5 py-20 md:grid-cols-2 md:px-10 md:py-24"><div><div className="font-mono text-[10px] font-semibold uppercase tracking-[0.15em] text-[#385e42]">Why this matters</div><h2 className="mt-4 font-newsreader text-5xl leading-[0.95] md:text-6xl">From satellite evidence to decisions on the ground.</h2></div><p className="max-w-lg self-end text-base leading-7 text-[#4a4a4a]">The system connects observed surface change with terrain, infrastructure exposure and settlement accessibility. It makes the analytical chain visible so that each consequence can be read against the evidence that led to it.</p></div></section>
      <section className="mx-auto max-w-[1440px] px-5 py-20 md:px-10 md:py-28"><div className="border-l-2 border-[#c05621] pl-6 md:pl-10"><div className="font-mono text-[10px] font-semibold uppercase tracking-[0.15em] text-[#c05621]">Scientific restraint</div><div className="mt-5 grid gap-8 md:grid-cols-2"><p className="max-w-xl font-newsreader text-3xl leading-tight">SAR evidence represents potential flood-related surface change, not a confirmed operational flood boundary.</p><p className="max-w-xl text-sm leading-6 text-[#717171]">Infrastructure intersecting the evidence is classified as potentially affected, not confirmed damaged. Network disruption is a scenario based on potentially affected road segments.</p></div></div></section>
      <section className="border-t border-[#d8d5cc] bg-[#1a1a1a] text-[#fdf9f0]"><div className="mx-auto flex max-w-[1440px] flex-col gap-8 px-5 py-14 md:flex-row md:items-end md:justify-between md:px-10 md:py-20"><div><div className="font-mono text-[10px] uppercase tracking-[0.15em] text-[#9db8d7]">Next / evidence in context</div><h2 className="mt-4 max-w-xl font-newsreader text-5xl leading-[0.9] md:text-7xl">Read the full flood intelligence.</h2></div><a href="/dashboard" className="inline-flex shrink-0 items-center gap-3 border border-[#fdf9f0]/60 px-5 py-3 font-mono text-[10px] uppercase tracking-[0.12em] hover:bg-[#fdf9f0] hover:text-[#1a1a1a]">Open flood intelligence dashboard <ArrowUpRight size={15} /></a></div></section>
    </main>
  </div>;
}

function App() {
  return window.location.pathname === "/dashboard" ? <Dashboard /> : <LandingPage />;
}

export default App;







