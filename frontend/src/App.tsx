import { useEffect, useState } from "react";
import SegmentedEvidenceSwitcher from "./components/ui/SegmentedEvidenceSwitcher";
import MetricCard from "./components/ui/MetricCard";
import EvidenceLedgerTable from "./components/ui/EvidenceLedgerTable";
import GlobeScrollDemo from "./components/ui/landing-page";
import {
  Crosshair,
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


const evidenceMetadata: Record<
  MapMode,
  {
    title: string;
    explanation: string;
    source: string;
    date: string;
    classification: string;
  }
> = {
  impact: {
    title: "Composite impact / evidence view",
    explanation:
      "Composite visualization of the analytical evidence and contextual layers used in this report; it is not a confirmed damage map.",
    source: "Sentinel-1 + Copernicus DEM + pre-event OSM",
    date: "EVENT 28 AUG 2026 · OSM 27 JUL 2026",
    classification: "Analytical evidence + contextual layers",
  },
  sar: {
    title: "Terrain-corrected SAR change",
    explanation:
      "Terrain-corrected Sentinel-1 surface-change visualization used as potential flood-related evidence.",
    source: "Copernicus Sentinel-1 / gamma0terrain",
    date: "16 AUG → 28 AUG 2026",
    classification: "Analytical evidence",
  },
  drainage: {
    title: "DEM-derived drainage corridor",
    explanation:
      "Terrain-derived drainage structure used to contextualise where water may move and where assets are exposed.",
    source: "Copernicus DEM GLO-30",
    date: "100 M HYDROLOGIC CORRIDOR",
    classification: "Contextual terrain layer",
  },
  beforeAfter: {
    title: "Sentinel-1 before / after comparison",
    explanation:
      "Before-and-after Sentinel-1 comparison for the two acquisition dates; visual change is not a confirmed flood boundary.",
    source: "Copernicus Sentinel-1",
    date: "16 AUG 2026 → 28 AUG 2026",
    classification: "Analytical evidence",
  },
};



type DashboardMetrics = {
  settlementsAnalysed: number;
  potentiallyAffectedRoads: number;
  buildingsInDrainageCorridor: number;
  potentiallyAffectedBridges: number;
  baselineReachable: number;
  baselineUnreachable: number;
  potentiallyCutOff: number;
  longerRoute: number;
};

type DashboardRoadRecord = { id: string; roadClass: string; total: string; overlap: string; percent: string };
type DashboardSettlementRecord = { settlement: string; status: string; baseline: string; scenario: string; delta: string };
type DashboardBuildingRecord = { id: string; osmType: string; geometryType: string; attributes: string; clippedToCorridor: boolean; classification: string };
type DashboardBridgeRecord = { id: string; bridgeClass: string; reference: string; mappedLength: string; evidenceOverlap: string; classification: string };
type DashboardSnapshot = {
  schema_version: string;
  snapshot_version: string;
  generated_at: string;
  analysis: { name: string; event_date: string; radar_pair: string[]; osm_snapshot: string; analysis_version: string };
  metrics: DashboardMetrics;
  roadSegments: DashboardRoadRecord[];
  settlementConnectivity: DashboardSettlementRecord[];
  buildingRecords: DashboardBuildingRecord[];
  bridgeRecords: DashboardBridgeRecord[];
};

function isDashboardSnapshot(value: unknown): value is DashboardSnapshot {
  if (!value || typeof value !== "object") return false;
  const snapshot = value as Partial<DashboardSnapshot>;
  const metrics = snapshot.metrics;
  const analysis = snapshot.analysis;
  if (!metrics || typeof metrics !== "object" || !analysis || typeof analysis !== "object") return false;

  const metricKeys: (keyof DashboardMetrics)[] = [
    "settlementsAnalysed", "potentiallyAffectedRoads", "buildingsInDrainageCorridor",
    "potentiallyAffectedBridges", "baselineReachable", "baselineUnreachable",
    "potentiallyCutOff", "longerRoute",
  ];
  const roadFields: (keyof DashboardRoadRecord)[] = ["id", "roadClass", "total", "overlap", "percent"];
  const settlementFields: (keyof DashboardSettlementRecord)[] = ["settlement", "status", "baseline", "scenario", "delta"];
  const buildingFields: (keyof DashboardBuildingRecord)[] = ["id", "osmType", "geometryType", "attributes", "classification"];
  const bridgeFields: (keyof DashboardBridgeRecord)[] = ["id", "bridgeClass", "reference", "mappedLength", "evidenceOverlap", "classification"];
  const hasFields = (record: object, fields: string[]) => fields.every((field) => typeof record[field as keyof typeof record] === "string");

  return snapshot.schema_version === "1.1" &&
    typeof snapshot.snapshot_version === "string" &&
    typeof snapshot.generated_at === "string" &&
    typeof analysis.name === "string" &&
    typeof analysis.event_date === "string" &&
    Array.isArray(analysis.radar_pair) &&
    Array.isArray(snapshot.roadSegments) &&
    snapshot.roadSegments.every((record) => record && typeof record === "object" && hasFields(record, roadFields)) &&
    Array.isArray(snapshot.settlementConnectivity) &&
    snapshot.settlementConnectivity.every((record) => record && typeof record === "object" && hasFields(record, settlementFields)) &&
    Array.isArray(snapshot.buildingRecords) &&
    snapshot.buildingRecords.every((record) => record && typeof record === "object" && hasFields(record, buildingFields) && typeof record.clippedToCorridor === "boolean") &&
    Array.isArray(snapshot.bridgeRecords) &&
    snapshot.bridgeRecords.every((record) => record && typeof record === "object" && hasFields(record, bridgeFields)) &&
    metricKeys.every((key) => typeof metrics[key] === "number" && Number.isFinite(metrics[key]));
}

const settlementStatusDescriptions: Record<string, string> = {
  BASELINE_UNREACHABLE: "No baseline route was found; this is not a flood-induced cut-off.",
  CUT_OFF: "A baseline route existed, but none remained under the simulated road-removal scenario.",
  LONGER_ROUTE: "A route remains, but its distance increased under the simulated scenario.",
  NO_CHANGE: "No meaningful accessibility change was found in the simulated scenario.",
};function SectionHeader({
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



function DashboardDataState({ message }: { message: string }) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-[#fdf9f0] px-5 text-[#1a1a1a]">
      <div className="w-full max-w-xl border border-[#d8d5cc] bg-[#f7f3ea] p-6 md:p-8">
        <div className="font-mono text-[10px] font-semibold uppercase tracking-[0.14em] text-[#c05621]">Dashboard data unavailable</div>
        <h1 className="mt-3 font-newsreader text-4xl leading-none">Flood intelligence is waiting for a valid snapshot.</h1>
        <p className="mt-4 text-sm leading-6 text-[#717171]">{message}</p>
      </div>
    </div>
  );
}

function Dashboard() {
  const [dashboardData, setDashboardData] = useState<DashboardSnapshot | null>(null);
  const [dataError, setDataError] = useState<string | null>(null);
  const [mapMode, setMapMode] = useState<MapMode>("impact");
  const [selectedRoadId, setSelectedRoadId] = useState<string | null>(null);
  const [selectedSettlementIndex, setSelectedSettlementIndex] = useState<number | null>(null);
  const [selectedBuildingIndex, setSelectedBuildingIndex] = useState<number | null>(null);
  const [selectedBridgeIndex, setSelectedBridgeIndex] = useState<number | null>(null);
  const [zoom, setZoom] = useState(1);


  const changeZoom = (value: number) => {
    setZoom((current) =>
      Math.min(1.35, Math.max(0.8, current + value))
    );
  };


  const resetZoom = () => {
    setZoom(1);
  };



  useEffect(() => {
    let active = true;
    fetch("/data/dashboard-snapshot.json", { cache: "no-store" })
      .then(async (response) => {
        if (!response.ok) throw new Error(`Snapshot request failed (${response.status}).`);
        const payload: unknown = await response.json();
        if (!isDashboardSnapshot(payload)) throw new Error("Snapshot schema validation failed.");
        return payload;
      })
      .then((payload) => { if (active) setDashboardData(payload); })
      .catch((error: unknown) => {
        if (active) setDataError(error instanceof Error ? error.message : "Unknown snapshot error.");
      });
  return () => { active = false; };
  }, []);

  if (dataError) return <DashboardDataState message={dataError} />;
  if (!dashboardData) return <DashboardDataState message="Loading the versioned analysis snapshot…" />;

    const infrastructureSummary = [
    { label: "BUILDINGS", value: dashboardData.metrics.buildingsInDrainageCorridor, detail: "hydrological-corridor exposure records", tone: "bg-[#385e42]" },
    { label: "ROADS", value: dashboardData.metrics.potentiallyAffectedRoads, detail: "potentially affected road records", tone: "bg-[#c05621]" },
    { label: "BRIDGES", value: dashboardData.metrics.potentiallyAffectedBridges, detail: "potentially affected bridge records", tone: "bg-[#2c5282]" },
  ];
  const infrastructureMax = Math.max(...infrastructureSummary.map((item) => item.value), 1);
  const settlementStatusOrder = ["BASELINE_UNREACHABLE", "CUT_OFF", "LONGER_ROUTE", "NO_CHANGE"];
  const settlementSummary = settlementStatusOrder.map((status) => ({
    status,
    value: dashboardData.settlementConnectivity.filter((record) => record.status === status).length,
  }));
  const settlementMax = Math.max(...settlementSummary.map((item) => item.value), 1);
  const roadOverlapSummary = dashboardData.roadSegments.map((road) => ({
    ...road,
    overlapValue: Number.parseFloat(road.percent) || 0,
  }));
  const roadOverlapMax = Math.max(...roadOverlapSummary.map((road) => road.overlapValue), 1);
  const selectedRoad = dashboardData.roadSegments.find((road) => road.id === selectedRoadId) ?? null;
  const selectedSettlement = selectedSettlementIndex === null
    ? null
    : dashboardData.settlementConnectivity[selectedSettlementIndex] ?? null;
  const selectedBuilding = selectedBuildingIndex === null
    ? null
    : dashboardData.buildingRecords[selectedBuildingIndex] ?? null;
  const selectedBridge = selectedBridgeIndex === null
    ? null
    : dashboardData.bridgeRecords[selectedBridgeIndex] ?? null;
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
                LAT 28°10′N · LON 85°22′E
                <span className="mx-3 text-[#c4c7c7]">|</span>
                ANALYTICAL PROTOTYPE
              </div>
            </div>


            <div className="relative overflow-hidden border border-[#d8d5cc] bg-[#f1eee4]">
              <div aria-label="Static reference coordinate" className="absolute left-3 top-2 z-20 border border-[#d8d5cc]/70 bg-[#fdf9f0]/90 px-1 py-0.5 font-mono text-[8px] tracking-widest text-[#717171]">
                REF / N28°15′00″ — E85°10′00″
              </div>

              <div aria-label="Static reference coordinate" className="absolute right-3 top-2 z-20 border border-[#d8d5cc]/70 bg-[#fdf9f0]/90 px-1 py-0.5 font-mono text-[8px] tracking-widest text-[#717171]">
                REF / N28°15′00″ — E85°30′00″
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
                        16 → 28 AUG 2026
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
                      STATIC REFERENCE / METRIC SCALE
                    </div>
                    <div className="mt-1 flex items-center gap-2">
                      <div className="flex h-2 w-24 border-x border-b border-[#1a1a1a]">
                        <div className="w-1/3 bg-[#1a1a1a]" />
                        <div className="w-1/3 border-r border-[#1a1a1a]" />
                        <div className="w-1/3 bg-[#1a1a1a]" />
                      </div>

                      <span>0 — 5 — 15 km</span>
                    </div>
                  </div>

                  <div className="h-6 w-px bg-[#d8d5cc]" />

                  <div className="flex items-center gap-2">
                    <Crosshair size={16} />
                    <div>
                      <div>TRUE N</div>
                      <div className="text-[#717171]">
                        DECL +0.2°
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
                note={`${dashboardData.metrics.baselineReachable} reachable in baseline network`}
                unit="LOCI"
                value={String(dashboardData.metrics.settlementsAnalysed)}
              />
              <MetricCard
                accent="rust"
                label="Potentially Affected Roads"
                note="SAR evidence intersection"
                unit="SEGS"
                value={String(dashboardData.metrics.potentiallyAffectedRoads)}
              />
              <MetricCard
                accent="green"
                label="Buildings in Drainage Corridor"
                note="100 m hydrologic corridor"
                unit="BLDG"
                value={String(dashboardData.metrics.buildingsInDrainageCorridor)}
              />
              <MetricCard
                accent="blue"
                label="Potentially Affected Bridges"
                note="No bridge intersected current SAR evidence"
                unit="SEV"
                value={String(dashboardData.metrics.potentiallyAffectedBridges)}
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
                    IMAGE SCALE {Math.round(zoom * 100)}%
                  </span>

                  <button
                    aria-label="Zoom in"
                    onClick={() => changeZoom(0.1)}
                    type="button" className="flex h-7 w-7 items-center justify-center border border-[#d8d5cc] bg-[#fdf9f0]"
                  >
                    <Plus size={14} />
                  </button>

                  <button
                    aria-label="Zoom out"
                    onClick={() => changeZoom(-0.1)}
                    type="button" className="flex h-7 w-7 items-center justify-center border border-[#d8d5cc] bg-[#fdf9f0]"
                  >
                    <Minus size={14} />
                  </button>

                  <button
                    aria-label="Reset zoom"
                    onClick={resetZoom}
                    type="button" className="flex h-7 items-center gap-1 border border-[#d8d5cc] bg-[#fdf9f0] px-2"
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
                      STATIC REFERENCE · ANALYSIS CENTRE
                    </div>
                  </div>
                </div>


                <div className="absolute bottom-4 left-4 max-w-[min(25rem,calc(100%-2rem))] border border-[#1a1a1a] bg-[#fdf9f0]/95 p-3 font-mono text-[9px]">
                  <div className="mb-2 border-b border-[#d8d5cc] pb-1 font-semibold uppercase tracking-wider">
                    {evidenceMetadata[mapMode].title}
                  </div>

                  <p className="max-w-md leading-4 text-[#4a4a4a]">
                    {evidenceMetadata[mapMode].explanation}
                  </p>

                  <div className="mt-2 grid gap-1 border-t border-[#d8d5cc] pt-2 uppercase tracking-[0.04em] text-[#717171]">
                    <span>SOURCE / {evidenceMetadata[mapMode].source}</span>
                    <span>DATE / {evidenceMetadata[mapMode].date}</span>
                    <span>CLASS / {evidenceMetadata[mapMode].classification}</span>
                  </div>
                </div>
                <div className="absolute right-4 top-4 border border-[#1a1a1a] bg-[#fdf9f0]/95 p-3">
                  <div className="flex items-center gap-2 font-mono text-[9px] uppercase">
                    <Layers3 size={13} />
                    <span>{evidenceMetadata[mapMode].title}</span>
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
                  String(dashboardData.metrics.buildingsInDrainageCorridor),
                  "Buildings inside the 100 m drainage corridor.",
                ],
                [
                  "ROADS",
                  String(dashboardData.metrics.potentiallyAffectedRoads),
                  "Road features intersecting SAR evidence.",
                ],
                [
                  "BRIDGES",
                  String(dashboardData.metrics.potentiallyAffectedBridges),
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


            <section aria-labelledby="summary-visualizations" className="flex flex-col gap-4 border-y border-[#d8d5cc] py-4">
              <div className="flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
                <div>
                  <div className="font-mono text-[10px] font-semibold uppercase tracking-[0.14em] text-[#2c5282]">03 / SUMMARY VISUALIZATIONS</div>
                  <h3 id="summary-visualizations" className="mt-1 font-newsreader text-3xl leading-none">Exposure and access at a glance</h3>
                </div>
                <p className="max-w-xl text-xs leading-5 text-[#717171]">Snapshot-backed summaries of potential infrastructure exposure and network-disruption scenario classifications. These are not confirmed physical damage or real-world isolation findings.</p>
              </div>

              <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
                <div className="border border-[#d8d5cc] bg-[#f7f3ea] p-4">
                  <div className="flex items-baseline justify-between border-b border-[#d8d5cc] pb-2">
                    <h4 className="font-mono text-[10px] font-semibold uppercase tracking-[0.08em]">Infrastructure exposure</h4>
                    <span className="font-mono text-[9px] uppercase text-[#717171]">records</span>
                  </div>
                  <div className="mt-4 space-y-4" role="list" aria-label="Infrastructure exposure summary">
                    {infrastructureSummary.map((item) => (
                      <div key={item.label} role="listitem">
                        <div className="flex items-baseline justify-between gap-3 font-mono text-[10px]">
                          <span className="font-semibold">{item.label}</span>
                          <span>{item.value}</span>
                        </div>
                        <div className="mt-1 h-2 bg-[#e2dfd7]" role="progressbar" aria-label={`${item.label} ${item.detail}`} aria-valuemin={0} aria-valuemax={infrastructureMax} aria-valuenow={item.value}>
                          <div className={`h-full ${item.tone}`} style={{ width: `${(item.value / infrastructureMax) * 100}%` }} />
                        </div>
                        <div className="mt-1 text-[10px] text-[#717171]">{item.detail}</div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="border border-[#d8d5cc] bg-[#f7f3ea] p-4">
                  <div className="flex items-baseline justify-between border-b border-[#d8d5cc] pb-2">
                    <h4 className="font-mono text-[10px] font-semibold uppercase tracking-[0.08em]">Settlement accessibility</h4>
                    <span className="font-mono text-[9px] uppercase text-[#717171]">scenario records</span>
                  </div>
                  <div className="mt-4 space-y-4" role="list" aria-label="Settlement accessibility scenario classifications">
                    {settlementSummary.map((item) => (
                      <div key={item.status} role="listitem">
                        <div className="flex items-baseline justify-between gap-3 font-mono text-[10px]">
                          <span className="font-semibold">{item.status}</span>
                          <span>{item.value}</span>
                        </div>
                        <div className="mt-1 h-2 bg-[#e2dfd7]" role="progressbar" aria-label={`${item.status} settlement count`} aria-valuemin={0} aria-valuemax={settlementMax} aria-valuenow={item.value}>
                          <div className={`h-full ${item.status === "CUT_OFF" ? "bg-[#c05621]" : item.status === "LONGER_ROUTE" ? "bg-[#2c5282]" : item.status === "BASELINE_UNREACHABLE" ? "bg-[#717171]" : "bg-[#385e42]"}`} style={{ width: `${(item.value / settlementMax) * 100}%` }} />
                        </div>
                        <div className="mt-1 text-[10px] text-[#717171]">{settlementStatusDescriptions[item.status]}</div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div className="border border-[#d8d5cc] bg-[#f7f3ea] p-4">
                <div className="flex flex-col gap-2 border-b border-[#d8d5cc] pb-2 sm:flex-row sm:items-baseline sm:justify-between">
                  <h4 className="font-mono text-[10px] font-semibold uppercase tracking-[0.08em]">Road evidence overlap</h4>
                  <span className="font-mono text-[9px] uppercase text-[#717171]">Select a bar to inspect the table record</span>
                </div>
                {roadOverlapSummary.length === 0 ? (
                  <div className="py-5 text-xs text-[#717171]">No road records are available in the generated snapshot.</div>
                ) : (
                  <div className="mt-4 grid grid-cols-1 gap-x-6 gap-y-2 md:grid-cols-2" role="list" aria-label="Road evidence overlap percentages">
                    {roadOverlapSummary.map((road) => (
                      <button
                        key={road.id}
                        type="button"
                        role="listitem"
                        aria-label={`Select road ${road.id}, ${road.overlapValue.toFixed(2)} percent evidence overlap`}
                        aria-pressed={selectedRoadId === road.id}
                        onClick={() => setSelectedRoadId(road.id)}
                        className={`group min-w-0 text-left outline-none focus-visible:ring-2 focus-visible:ring-[#2c5282] ${selectedRoadId === road.id ? "bg-[#e3eaf2]" : ""}`}
                      >
                        <div className="flex items-baseline justify-between gap-2 font-mono text-[9px]">
                          <span className="truncate font-semibold">OSM {road.id} · {road.roadClass}</span>
                          <span className="shrink-0 text-[#2c5282]">{road.percent}</span>
                        </div>
                        <div className="mt-1 h-2 bg-[#e2dfd7]">
                          <div className="h-full bg-[#c05621] transition-[width] duration-300 group-hover:bg-[#2c5282]" style={{ width: `${(road.overlapValue / roadOverlapMax) * 100}%` }} />
                        </div>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </section>
            <div className="overflow-x-auto border border-[#d8d5cc] bg-[#f7f3ea]">
              <div className="flex items-center justify-between border-b border-[#d8d5cc] bg-[#ebe8df] px-4 py-3 font-mono text-[9px] uppercase">
                <span className="font-semibold">
                  Potentially affected road segments
                </span>

                <span className="text-[#717171]">
                  Evidence overlap ledger
                </span>
              </div>

              <EvidenceLedgerTable
                roads={dashboardData.roadSegments}
                selectedRoadId={selectedRoadId}
                onSelectRoad={setSelectedRoadId}
              />

              {selectedRoad ? (
                <aside
                  aria-label="Selected potential road exposure"
                  className="border-t border-[#d8d5cc] bg-[#fdf9f0] px-4 py-4"
                  role="region"
                >
                  <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                    <div>
                      <div className="font-mono text-[9px] font-semibold uppercase tracking-[0.12em] text-[#c05621]">
                        Potential road exposure · selected record
                      </div>
                      <h3 className="mt-1 font-newsreader text-2xl leading-none">
                        OSM {selectedRoad.id}
                      </h3>
                      <p className="mt-2 max-w-2xl text-xs leading-5 text-[#717171]">
                        This record indicates potential exposure where the analysis evidence overlaps a mapped road. It does not confirm physical road damage, and the static PNG map is not highlighted by this selection.
                      </p>
                    </div>
                    <button
                      type="button"
                      onClick={() => setSelectedRoadId(null)}
                      className="shrink-0 border border-[#1a1a1a] bg-[#f7f3ea] px-3 py-2 font-mono text-[9px] uppercase tracking-[0.08em] transition-colors hover:bg-[#ebe8df] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#2c5282]"
                    >
                      Clear selection
                    </button>
                  </div>

                  <dl className="mt-4 grid grid-cols-2 gap-3 border-t border-[#d8d5cc] pt-3 sm:grid-cols-5">
                    <div>
                      <dt className="font-mono text-[9px] uppercase text-[#717171]">OSM ID</dt>
                      <dd className="mt-1 font-mono text-xs">{selectedRoad.id}</dd>
                    </div>
                    <div>
                      <dt className="font-mono text-[9px] uppercase text-[#717171]">Road class</dt>
                      <dd className="mt-1 font-mono text-xs uppercase">{selectedRoad.roadClass}</dd>
                    </div>
                    <div>
                      <dt className="font-mono text-[9px] uppercase text-[#717171]">Mapped length</dt>
                      <dd className="mt-1 font-mono text-xs">{selectedRoad.total}</dd>
                    </div>
                    <div>
                      <dt className="font-mono text-[9px] uppercase text-[#717171]">Evidence overlap</dt>
                      <dd className="mt-1 font-mono text-xs text-[#c05621]">{selectedRoad.overlap}</dd>
                    </div>
                    <div>
                      <dt className="font-mono text-[9px] uppercase text-[#717171]">Overlap</dt>
                      <dd className="mt-1 font-mono text-xs text-[#2c5282]">{selectedRoad.percent}</dd>
                    </div>
                  </dl>
                </aside>
              ) : (
                <div className="border-t border-[#d8d5cc] bg-[#fdf9f0] px-4 py-3 font-mono text-[9px] uppercase tracking-[0.06em] text-[#717171]">
                  Select a road row with a mouse, Enter, or Space to inspect potential exposure details.
                </div>
              )}
            </div>
          </section>


          <section className="flex flex-col gap-4">
            <SectionHeader
              number="03A / BUILDINGS"
              title="Inspect corridor exposure"
              description="Building records intersecting the DEM-derived drainage corridor are shown as hydrological-corridor exposure, not confirmed building damage."
            />

            <div className="overflow-x-auto border border-[#d8d5cc] bg-[#f7f3ea]">
              <div className="flex items-center justify-between border-b border-[#d8d5cc] bg-[#ebe8df] px-4 py-3 font-mono text-[9px] uppercase">
                <span className="font-semibold">Buildings in drainage corridor</span>
                <span className="text-[#717171]">Hydrological exposure ledger</span>
              </div>

              {dashboardData.buildingRecords.length === 0 ? (
                <div className="px-4 py-6 text-xs leading-5 text-[#717171]">
                  No building exposure records are available in the generated snapshot.
                </div>
              ) : (
                <>
                  <table className="w-full min-w-[760px] border-collapse text-left font-mono text-[10px]">
                    <caption className="sr-only">Buildings exposed within the drainage corridor. Select a row to inspect the source-backed record.</caption>
                    <thead className="border-b border-[#1a1a1a] bg-[#efece4] text-[#717171]">
                      <tr>
                        <th className="px-4 py-3 font-semibold">OSM ID</th>
                        <th className="px-4 py-3 font-semibold">OSM TYPE</th>
                        <th className="px-4 py-3 font-semibold">GEOMETRY</th>
                        <th className="px-4 py-3 font-semibold">ATTRIBUTES</th>
                        <th className="px-4 py-3 font-semibold">CLASSIFICATION</th>
                      </tr>
                    </thead>
                    <tbody>
                      {dashboardData.buildingRecords.map((building, index) => (
                        <tr
                          key={`${building.id}-${index}`}
                          aria-label={`Select building corridor exposure ${building.id}`}
                          aria-selected={selectedBuildingIndex === index}
                          role="button"
                          tabIndex={0}
                          onClick={() => setSelectedBuildingIndex(index)}
                          onKeyDown={(event) => {
                            if (event.key === "Enter" || event.key === " ") {
                              event.preventDefault();
                              setSelectedBuildingIndex(index);
                            }
                          }}
                          className={`cursor-pointer border-b border-[#e2dfd7] outline-none transition-colors focus-visible:bg-[#e3eaf2] focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-[#2c5282] ${selectedBuildingIndex === index ? "bg-[#e3eaf2]" : "hover:bg-[#f4f2ec]"}`}
                        >
                          <td className="whitespace-nowrap px-4 py-3 text-[#4a4a4a]">{building.id}</td>
                          <td className="px-4 py-3 uppercase">{building.osmType}</td>
                          <td className="px-4 py-3">{building.geometryType}</td>
                          <td className="max-w-[16rem] truncate px-4 py-3 text-[#717171]">{building.attributes}</td>
                          <td className="px-4 py-3 uppercase text-[#385e42]">{building.classification}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>

                  {selectedBuilding ? (
                    <aside aria-label="Selected building corridor exposure" className="border-t border-[#d8d5cc] bg-[#fdf9f0] px-4 py-4" role="region">
                      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                        <div>
                          <div className="font-mono text-[9px] font-semibold uppercase tracking-[0.12em] text-[#385e42]">Hydrological-corridor exposure · selected record</div>
                          <h3 className="mt-1 font-newsreader text-2xl leading-none">OSM {selectedBuilding.id}</h3>
                          <p className="mt-2 max-w-3xl text-xs leading-5 text-[#717171]">This source record is inside the DEM-derived drainage corridor. It does not confirm building damage, and the static PNG map is not highlighted by this selection.</p>
                        </div>
                        <button type="button" onClick={() => setSelectedBuildingIndex(null)} className="shrink-0 border border-[#1a1a1a] bg-[#f7f3ea] px-3 py-2 font-mono text-[9px] uppercase tracking-[0.08em] transition-colors hover:bg-[#ebe8df] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#2c5282]">Clear selection</button>
                      </div>
                      <dl className="mt-4 grid grid-cols-2 gap-3 border-t border-[#d8d5cc] pt-3 sm:grid-cols-5">
                        <div><dt className="font-mono text-[9px] uppercase text-[#717171]">OSM ID</dt><dd className="mt-1 font-mono text-xs">{selectedBuilding.id}</dd></div>
                        <div><dt className="font-mono text-[9px] uppercase text-[#717171]">OSM type</dt><dd className="mt-1 font-mono text-xs uppercase">{selectedBuilding.osmType}</dd></div>
                        <div><dt className="font-mono text-[9px] uppercase text-[#717171]">Geometry</dt><dd className="mt-1 font-mono text-xs">{selectedBuilding.geometryType}</dd></div>
                        <div><dt className="font-mono text-[9px] uppercase text-[#717171]">Attributes</dt><dd className="mt-1 font-mono text-xs">{selectedBuilding.attributes}</dd></div>
                        <div><dt className="font-mono text-[9px] uppercase text-[#717171]">Exposure class</dt><dd className="mt-1 font-mono text-xs uppercase text-[#385e42]">{selectedBuilding.classification}</dd></div>
                      </dl>
                    </aside>
                  ) : (
                    <div className="border-t border-[#d8d5cc] bg-[#fdf9f0] px-4 py-3 font-mono text-[9px] uppercase tracking-[0.06em] text-[#717171]">Select a building row with a mouse, Enter, or Space to inspect corridor exposure details.</div>
                  )}
                </>
              )}
            </div>
          </section>

          <section className="flex flex-col gap-4">
            <SectionHeader
              number="03B / BRIDGES"
              title="Bridge exposure records"
              description="Potentially affected bridge records from the analysis source are reported separately from buildings and roads."
            />

            <div className="border border-[#d8d5cc] bg-[#f7f3ea]">
              <div className="flex items-center justify-between border-b border-[#d8d5cc] bg-[#ebe8df] px-4 py-3 font-mono text-[9px] uppercase">
                <span className="font-semibold">Potentially affected bridges</span>
                <span className="text-[#717171]">Source-backed records only</span>
              </div>

              {dashboardData.bridgeRecords.length === 0 ? (
                <div className="px-4 py-6 text-xs leading-5 text-[#717171]">
                  <strong className="font-mono text-[10px] uppercase text-[#1a1a1a]">0 potentially affected bridge records.</strong>{" "}
                  The source contains no records under the current analysis criteria. This does not prove that no bridges were damaged; it only reports the available analysis result.
                </div>
              ) : (
                <>
                  <div className="overflow-x-auto">
                    <table className="w-full min-w-[720px] border-collapse text-left font-mono text-[10px]">
                      <caption className="sr-only">Potentially affected bridge records. Select a row to inspect the source-backed record.</caption>
                      <thead className="border-b border-[#1a1a1a] bg-[#efece4] text-[#717171]"><tr><th className="px-4 py-3 font-semibold">OSM ID</th><th className="px-4 py-3 font-semibold">CLASS</th><th className="px-4 py-3 font-semibold">REFERENCE</th><th className="px-4 py-3 font-semibold">MAPPED LENGTH</th><th className="px-4 py-3 font-semibold">EVIDENCE OVERLAP</th></tr></thead>
                      <tbody>
                        {dashboardData.bridgeRecords.map((bridge, index) => (
                          <tr key={`${bridge.id}-${index}`} aria-label={`Select bridge exposure ${bridge.id}`} aria-selected={selectedBridgeIndex === index} role="button" tabIndex={0} onClick={() => setSelectedBridgeIndex(index)} onKeyDown={(event) => { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); setSelectedBridgeIndex(index); } }} className={`cursor-pointer border-b border-[#e2dfd7] outline-none transition-colors focus-visible:bg-[#e3eaf2] focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-[#2c5282] ${selectedBridgeIndex === index ? "bg-[#e3eaf2]" : "hover:bg-[#f4f2ec]"}`}>
                            <td className="whitespace-nowrap px-4 py-3">{bridge.id}</td><td className="px-4 py-3 uppercase">{bridge.bridgeClass}</td><td className="px-4 py-3">{bridge.reference || "—"}</td><td className="px-4 py-3">{bridge.mappedLength}</td><td className="px-4 py-3 text-[#c05621]">{bridge.evidenceOverlap}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  {selectedBridge ? (
                    <aside aria-label="Selected bridge exposure" className="border-t border-[#d8d5cc] bg-[#fdf9f0] px-4 py-4" role="region"><div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between"><div><div className="font-mono text-[9px] font-semibold uppercase tracking-[0.12em] text-[#2c5282]">Potential bridge exposure · selected record</div><h3 className="mt-1 font-newsreader text-2xl leading-none">OSM {selectedBridge.id}</h3><p className="mt-2 text-xs leading-5 text-[#717171]">This is a potential exposure record from the analysis source, not a confirmation of bridge damage. The static PNG map is not highlighted by this selection.</p></div><button type="button" onClick={() => setSelectedBridgeIndex(null)} className="shrink-0 border border-[#1a1a1a] bg-[#f7f3ea] px-3 py-2 font-mono text-[9px] uppercase tracking-[0.08em] transition-colors hover:bg-[#ebe8df] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#2c5282]">Clear selection</button></div><dl className="mt-4 grid grid-cols-2 gap-3 border-t border-[#d8d5cc] pt-3 sm:grid-cols-5"><div><dt className="font-mono text-[9px] uppercase text-[#717171]">OSM ID</dt><dd className="mt-1 font-mono text-xs">{selectedBridge.id}</dd></div><div><dt className="font-mono text-[9px] uppercase text-[#717171]">Class</dt><dd className="mt-1 font-mono text-xs uppercase">{selectedBridge.bridgeClass}</dd></div><div><dt className="font-mono text-[9px] uppercase text-[#717171]">Reference</dt><dd className="mt-1 font-mono text-xs">{selectedBridge.reference || "—"}</dd></div><div><dt className="font-mono text-[9px] uppercase text-[#717171]">Mapped length</dt><dd className="mt-1 font-mono text-xs">{selectedBridge.mappedLength}</dd></div><div><dt className="font-mono text-[9px] uppercase text-[#717171]">Evidence overlap</dt><dd className="mt-1 font-mono text-xs text-[#c05621]">{selectedBridge.evidenceOverlap}</dd></div></dl></aside>
                  ) : null}
                </>
              )}
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
                  String(dashboardData.metrics.baselineReachable),
                  "Normal network access",
                ],
                [
                  "BASELINE UNREACHABLE",
                  String(dashboardData.metrics.baselineUnreachable),
                  "Already disconnected",
                ],
                [
                  "POTENTIALLY CUT OFF",
                  String(dashboardData.metrics.potentiallyCutOff),
                  "No route after scenario",
                ],
                [
                  "LONGER ROUTE",
                  String(dashboardData.metrics.longerRoute),
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
                  {dashboardData.settlementConnectivity.map((row, index) => (
                    <tr
                      key={`${row.settlement}-${index}`}
                      aria-label={`Select settlement accessibility record ${row.settlement}`}
                      aria-selected={selectedSettlementIndex === index}
                      role="button"
                      tabIndex={0}
                      onClick={() => setSelectedSettlementIndex(index)}
                      onKeyDown={(event) => {
                        if (event.key === "Enter" || event.key === " ") {
                          event.preventDefault();
                          setSelectedSettlementIndex(index);
                        }
                      }}
                      className={`cursor-pointer border-b border-[#e2dfd7] outline-none transition-colors focus-visible:bg-[#e3eaf2] focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-[#2c5282] ${selectedSettlementIndex === index ? "bg-[#e3eaf2]" : "hover:bg-[#f4f2ec]"}`}
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


              {selectedSettlement ? (
                <aside
                  aria-label="Selected settlement accessibility record"
                  className="border-t border-[#d8d5cc] bg-[#fdf9f0] px-4 py-4"
                  role="region"
                >
                  <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                    <div>
                      <div className="font-mono text-[9px] font-semibold uppercase tracking-[0.12em] text-[#2c5282]">
                        Network-disruption scenario · selected record
                      </div>
                      <h3 className="mt-1 font-newsreader text-2xl leading-none">
                        {selectedSettlement.settlement}
                      </h3>
                      <p className="mt-2 max-w-3xl text-xs leading-5 text-[#717171]">
                        {settlementStatusDescriptions[selectedSettlement.status] ?? "Classification supplied by the analysis snapshot."} Results describe a simulated network-disruption scenario, not confirmed real-world isolation.
                      </p>
                    </div>
                    <button
                      type="button"
                      onClick={() => setSelectedSettlementIndex(null)}
                      className="shrink-0 border border-[#1a1a1a] bg-[#f7f3ea] px-3 py-2 font-mono text-[9px] uppercase tracking-[0.08em] transition-colors hover:bg-[#ebe8df] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#2c5282]"
                    >
                      Clear selection
                    </button>
                  </div>

                  <dl className="mt-4 grid grid-cols-2 gap-3 border-t border-[#d8d5cc] pt-3 sm:grid-cols-5">
                    <div>
                      <dt className="font-mono text-[9px] uppercase text-[#717171]">Baseline status</dt>
                      <dd className="mt-1 font-mono text-xs uppercase">
                        {selectedSettlement.status === "BASELINE_UNREACHABLE" ? "BASELINE_UNREACHABLE" : "BASELINE ROUTE FOUND"}
                      </dd>
                    </div>
                    <div>
                      <dt className="font-mono text-[9px] uppercase text-[#717171]">Baseline route</dt>
                      <dd className="mt-1 font-mono text-xs">{selectedSettlement.baseline}</dd>
                    </div>
                    <div>
                      <dt className="font-mono text-[9px] uppercase text-[#717171]">Scenario status</dt>
                      <dd className="mt-1 font-mono text-xs uppercase">
                        {selectedSettlement.status === "BASELINE_UNREACHABLE" ? "NOT ASSESSED" : selectedSettlement.status}
                      </dd>
                    </div>
                    <div>
                      <dt className="font-mono text-[9px] uppercase text-[#717171]">Scenario route</dt>
                      <dd className="mt-1 font-mono text-xs">{selectedSettlement.scenario}</dd>
                    </div>
                    <div>
                      <dt className="font-mono text-[9px] uppercase text-[#717171]">Route change</dt>
                      <dd className="mt-1 font-mono text-xs text-[#2c5282]">{selectedSettlement.delta}</dd>
                    </div>
                  </dl>
                </aside>
              ) : (
                <div className="border-t border-[#d8d5cc] bg-[#fdf9f0] px-4 py-3 font-mono text-[9px] uppercase tracking-[0.06em] text-[#717171]">
                  Select a settlement row with a mouse, Enter, or Space to inspect accessibility details.
                </div>
              )}
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
              © OpenStreetMap contributors.
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


function App() {
  return window.location.pathname === "/dashboard" ? <Dashboard /> : <GlobeScrollDemo />;
}

export default App;

