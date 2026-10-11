"""Export the React dashboard's validated data snapshot from analysis Parquet files."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "osm_20260727"
OUTPUTS = ROOT / "outputs"
DEFAULT_OUTPUT = ROOT / "frontend" / "public" / "data" / "dashboard-snapshot.json"

SOURCE_PATHS = {
    "baseline_accessibility": DATA / "baseline_accessibility.parquet",
    "network_disruption_results": DATA / "network_disruption_results.parquet",
    "potentially_affected_roads": DATA / "potentially_affected_roads.parquet",
    "potentially_affected_bridges": DATA / "potentially_affected_bridges.parquet",
    "buildings_drainage_corridor_exposed": OUTPUTS / "buildings_drainage_corridor_exposed.parquet",
}

REQUIRED_COLUMNS = {
    "baseline_accessibility": {"baseline_accessible"},
    "network_disruption_results": {
        "name",
        "status",
        "baseline_distance_km",
        "post_distance_km",
        "route_increase_km",
        "route_increase_percent",
    },
    "potentially_affected_roads": {
        "osm_id",
        "highway",
        "road_length_m",
        "affected_length_m",
        "affected_fraction",
    },
    "potentially_affected_bridges": {"osm_id", "highway", "ref", "road_length_m", "affected_length_m"},
    "buildings_drainage_corridor_exposed": {"osm_type", "osm_id", "tags", "geom_type", "clipped"},
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_source(name: str) -> pd.DataFrame:
    path = SOURCE_PATHS[name]
    if not path.exists():
        raise FileNotFoundError(f"Missing source file: {path}")
    frame = pd.read_parquet(path)
    missing = REQUIRED_COLUMNS[name] - set(frame.columns)
    if missing:
        missing_list = ", ".join(sorted(missing))
        raise ValueError(f"{name} is missing required columns: {missing_list}")
    return frame


def rounded(value: Any, digits: int) -> float:
    number = float(value)
    if pd.isna(number):
        return 0.0
    return round(number, digits)


def tag_summary(value: Any) -> str:
    """Flatten the source OSM tag array into a compact, readable summary."""
    if hasattr(value, "tolist"):
        value = value.tolist()
    if not isinstance(value, (list, tuple)):
        return str(value) if value not in (None, "") else "No OSM tags"

    pairs: list[str] = []
    for item in value:
        if hasattr(item, "tolist"):
            item = item.tolist()
        if isinstance(item, (list, tuple)) and len(item) == 2:
            pairs.append(f"{item[0]}={item[1]}")
    return ", ".join(pairs) if pairs else "OSM tags available"

def export_snapshot(output: Path) -> dict[str, Any]:
    frames = {name: load_source(name) for name in SOURCE_PATHS}
    baseline = frames["baseline_accessibility"]
    disruption = frames["network_disruption_results"]
    affected_roads = frames["potentially_affected_roads"]
    affected_bridges = frames["potentially_affected_bridges"]
    buildings = frames["buildings_drainage_corridor_exposed"]

    baseline_accessible = int(baseline["baseline_accessible"].fillna(False).sum())
    baseline_unreachable = int((~baseline["baseline_accessible"].fillna(False)).sum())
    cut_off = int((disruption["status"] == "CUT_OFF").sum())
    longer_routes = int((disruption["status"] == "LONGER_ROUTE").sum())

    roads = affected_roads[
        [
            "osm_id",
            "highway",
            "road_length_m",
            "affected_length_m",
            "affected_fraction",
        ]
    ].copy()
    roads["road_length_km"] = (roads["road_length_m"] / 1000).round(2)
    roads["affected_length_m"] = roads["affected_length_m"].round(1)
    roads["affected_fraction_pct"] = (roads["affected_fraction"] * 100).round(2)
    roads = roads.sort_values("affected_fraction_pct", ascending=False)

    road_records = [
        {
            "id": str(row.osm_id),
            "roadClass": str(row.highway),
            "total": f"{rounded(row.road_length_km, 2):.2f} km",
            "overlap": f"{rounded(row.affected_length_m, 1):.1f} m",
            "percent": f"{rounded(row.affected_fraction_pct, 2):.2f}%",
        }
        for row in roads.itertuples(index=False)
    ]

    building_records = [
        {
            "id": str(row.osm_id),
            "osmType": str(row.osm_type),
            "geometryType": str(row.geom_type),
            "attributes": tag_summary(row.tags),
            "clippedToCorridor": bool(row.clipped),
            "classification": "DRAINAGE_CORRIDOR_EXPOSED",
        }
        for row in buildings[["osm_type", "osm_id", "tags", "geom_type", "clipped"]].itertuples(index=False)
    ]

    bridge_records = [
        {
            "id": str(row.osm_id),
            "bridgeClass": str(row.highway),
            "reference": str(row.ref) if not pd.isna(row.ref) else "",
            "mappedLength": f"{rounded(row.road_length_m, 1):.1f} m",
            "evidenceOverlap": f"{rounded(row.affected_length_m, 1):.1f} m",
            "classification": "POTENTIALLY_AFFECTED_BRIDGE",
        }
        for row in affected_bridges[["osm_id", "highway", "ref", "road_length_m", "affected_length_m"]].itertuples(index=False)
    ]
    settlement_records = [
        {
            "settlement": str(row.name),
            "status": str(row.status),
            "baseline": f"{rounded(row.baseline_distance_km, 2):.2f} km",
            "scenario": f"{rounded(row.post_distance_km, 2):.2f} km",
            "delta": f"{rounded(row.route_increase_km, 2):.2f} km",
        }
        for row in disruption[
            [
                "name",
                "status",
                "baseline_distance_km",
                "post_distance_km",
                "route_increase_km",
                "route_increase_percent",
            ]
        ].itertuples(index=False)
    ]

    source_metadata = {}
    for name, path in SOURCE_PATHS.items():
        frame = frames[name]
        source_metadata[name] = {
            "path": path.relative_to(ROOT).as_posix(),
            "sha256": sha256(path),
            "rows": int(len(frame)),
            "columns": list(frame.columns),
        }

    snapshot = {
        "schema_version": "1.1",
        "snapshot_version": "rasuwa-0826-dashboard-v2",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "analysis": {
            "name": "Flood Intelligence | Rasuwa",
            "event_date": "2026-08-28",
            "radar_pair": ["2026-08-16", "2026-08-28"],
            "osm_snapshot": "2026-07-27",
            "analysis_version": "rasuwa-0826",
        },
        "sources": source_metadata,
        "metrics": {
            "settlementsAnalysed": int(len(disruption)),
            "potentiallyAffectedRoads": int(len(affected_roads)),
            "buildingsInDrainageCorridor": int(len(buildings)),
            "potentiallyAffectedBridges": int(len(affected_bridges)),
            "baselineReachable": baseline_accessible,
            "baselineUnreachable": baseline_unreachable,
            "potentiallyCutOff": cut_off,
            "longerRoute": longer_routes,
        },
        "roadSegments": road_records,
        "settlementConnectivity": settlement_records,
        "buildingRecords": building_records,
        "bridgeRecords": bridge_records,
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return snapshot


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    snapshot = export_snapshot(args.output.resolve())
    print(json.dumps({"output": str(args.output.resolve()), "metrics": snapshot["metrics"], "roads": len(snapshot["roadSegments"]), "settlements": len(snapshot["settlementConnectivity"]), "buildings": len(snapshot["buildingRecords"]), "bridges": len(snapshot["bridgeRecords"])}, indent=2))


if __name__ == "__main__":
    main()
