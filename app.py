from pathlib import Path
from textwrap import dedent
import base64

import pandas as pd
import streamlit as st
from PIL import Image


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "processed" / "osm_20260727"
OUTPUTS = ROOT / "outputs"


st.set_page_config(
    page_title="Flood Intelligence | Rasuwa",
    page_icon="◌",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def render_html(content: str) -> None:
    st.markdown(
        dedent(content),
        unsafe_allow_html=True,
    )


@st.cache_data
def load_data():
    baseline = pd.read_parquet(
        DATA / "baseline_accessibility.parquet"
    )

    disruption = pd.read_parquet(
        DATA / "network_disruption_results.parquet"
    )

    affected_roads = pd.read_parquet(
        DATA / "potentially_affected_roads.parquet"
    )

    affected_bridges = pd.read_parquet(
        DATA / "potentially_affected_bridges.parquet"
    )

    buildings = pd.read_parquet(
        OUTPUTS / "buildings_drainage_corridor_exposed.parquet"
    )

    roads_exposed = pd.read_parquet(
        OUTPUTS / "roads_drainage_corridor_exposed.parquet"
    )

    bridges_exposed = pd.read_parquet(
        OUTPUTS / "bridges_drainage_corridor_exposed.parquet"
    )

    return (
        baseline,
        disruption,
        affected_roads,
        affected_bridges,
        buildings,
        roads_exposed,
        bridges_exposed,
    )


def show_image(path: Path, caption: str | None = None) -> None:
    if path.exists():
        image = Image.open(path)

        st.image(
            image,
            width="stretch",
            caption=caption,
        )
    else:
        st.warning(f"Visualization not found: {path}")


def metric_html(
    label: str,
    value: str,
    note: str,
) -> str:
    return f"""
    <div class="metric">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-note">{note}</div>
    </div>
    """


render_html(
    """
    <style>
    :root {
        --paper: #f4f1e9;
        --paper-soft: #ebe7dc;
        --ink: #171817;
        --muted: #6d706d;
        --line: #d6d2c8;
        --blue: #356c82;
        --blue-soft: #dbe7eb;
        --green: #68795d;
        --green-soft: #dfe6da;
        --rust: #a65b45;
        --rust-soft: #f0ddd5;
        --white: #fbfaf6;
    }

    .stApp {
        background: var(--paper);
        color: var(--ink);
    }

    .block-container {
        max-width: 1440px;
        padding-top: 1.2rem;
        padding-bottom: 4rem;
    }

    header[data-testid="stHeader"] {
        background: transparent;
    }

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    [data-testid="stSidebar"] {
        background: var(--paper);
    }

    .masthead {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.3rem 0 1rem 0;
        border-bottom: 1px solid var(--line);
        margin-bottom: 1.8rem;
    }

    .brand {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        font-size: 0.76rem;
        font-weight: 800;
        letter-spacing: 0.12em;
        text-transform: uppercase;
    }

    .brand-mark {
        width: 11px;
        height: 11px;
        border: 1.5px solid var(--ink);
        border-radius: 50%;
        position: relative;
    }

    .brand-mark::after {
        content: "";
        position: absolute;
        width: 4px;
        height: 4px;
        background: var(--blue);
        border-radius: 50%;
        top: 2px;
        left: 2px;
    }

    .mast-right {
        display: flex;
        align-items: center;
        gap: 1.35rem;
        color: var(--muted);
        font-size: 0.68rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    .status-dot {
        display: inline-block;
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: var(--green);
        margin-right: 0.32rem;
    }

    .hero-wrap {
        position: relative;
        overflow: hidden;
        border: 1px solid var(--line);
        background: var(--white);
        min-height: 560px;
        margin-bottom: 1.5rem;
    }

    .hero-image {
        width: 100%;
        height: 560px;
        object-fit: cover;
        display: block;
        filter: saturate(0.78) contrast(0.97);
    }

    .hero-overlay {
        position: absolute;
        inset: 0;
        background:
            linear-gradient(
                90deg,
                rgba(244, 241, 233, 0.98) 0%,
                rgba(244, 241, 233, 0.92) 24%,
                rgba(244, 241, 233, 0.65) 42%,
                rgba(244, 241, 233, 0.17) 66%,
                rgba(244, 241, 233, 0.00) 83%
            );
        pointer-events: none;
    }

    .hero-copy {
        position: absolute;
        left: 3.2rem;
        top: 3rem;
        width: 43%;
        z-index: 2;
    }

    .eyebrow {
        font-size: 0.66rem;
        font-weight: 800;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: var(--blue);
        margin-bottom: 1rem;
    }

    .hero-title {
        font-size: clamp(3.2rem, 5.7vw, 6.2rem);
        line-height: 0.9;
        letter-spacing: -0.06em;
        font-weight: 700;
        margin: 0;
        color: var(--ink);
    }

    .hero-title span {
        color: var(--blue);
    }

    .hero-description {
        margin-top: 1.45rem;
        max-width: 470px;
        font-size: 1rem;
        line-height: 1.65;
        color: #4f524f;
    }

    .hero-meta {
        margin-top: 2.1rem;
        display: flex;
        gap: 1.7rem;
        flex-wrap: wrap;
    }

    .meta-block {
        border-left: 2px solid var(--line);
        padding-left: 0.7rem;
    }

    .meta-label {
        font-size: 0.6rem;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: var(--muted);
    }

    .meta-value {
        font-size: 0.82rem;
        font-weight: 750;
        margin-top: 0.22rem;
    }

    .section-kicker {
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
        gap: 2rem;
        border-bottom: 1px solid var(--line);
        padding-bottom: 0.6rem;
        margin-top: 3.5rem;
        margin-bottom: 1.4rem;
    }

    .section-number {
        font-family: monospace;
        font-size: 0.68rem;
        color: var(--muted);
        margin-bottom: 0.45rem;
    }

    .section-title {
        font-size: clamp(2rem, 3.2vw, 3.1rem);
        line-height: 0.95;
        letter-spacing: -0.05em;
        font-weight: 700;
        margin: 0;
    }

    .section-copy {
        color: var(--muted);
        font-size: 0.78rem;
        max-width: 430px;
        text-align: right;
        line-height: 1.5;
    }

    .metric {
        background: var(--white);
        border: 1px solid var(--line);
        padding: 1.2rem 1.25rem 1.25rem 1.25rem;
        min-height: 155px;
        box-sizing: border-box;
    }

    .metric-label {
        color: var(--muted);
        font-size: 0.61rem;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        font-weight: 750;
    }

    .metric-value {
        font-size: 2.65rem;
        line-height: 0.95;
        letter-spacing: -0.055em;
        font-weight: 700;
        margin-top: 1rem;
        color: var(--ink);
    }

    .metric-note {
        color: var(--muted);
        font-size: 0.68rem;
        line-height: 1.42;
        margin-top: 0.72rem;
    }

    .evidence-card {
        background: var(--white);
        border: 1px solid var(--line);
        padding: 1.25rem;
        min-height: 180px;
        box-sizing: border-box;
    }

    .evidence-index {
        font-family: monospace;
        color: var(--blue);
        font-size: 0.65rem;
        margin-bottom: 1rem;
    }

    .evidence-title {
        font-size: 1.3rem;
        letter-spacing: -0.03em;
        font-weight: 700;
        margin-bottom: 0.45rem;
    }

    .evidence-text {
        color: var(--muted);
        font-size: 0.76rem;
        line-height: 1.58;
    }

    .scenario {
        border: 1px solid var(--line);
        background: var(--white);
        padding: 1.5rem;
        min-height: 215px;
        box-sizing: border-box;
    }

    .scenario-title {
        font-size: 0.65rem;
        font-weight: 800;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: var(--blue);
        margin-bottom: 1.15rem;
    }

    .scenario-big {
        font-size: 4.4rem;
        line-height: 0.86;
        letter-spacing: -0.065em;
        font-weight: 700;
    }

    .scenario-small {
        color: var(--muted);
        margin-top: 0.9rem;
        font-size: 0.75rem;
        line-height: 1.5;
        max-width: 260px;
    }

    .status-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.45rem;
        margin: 1rem 0 1.2rem 0;
    }

    .status-pill {
        display: inline-block;
        padding: 0.34rem 0.58rem;
        border: 1px solid var(--line);
        font-family: monospace;
        font-size: 0.63rem;
        background: var(--paper);
    }

    .note-box {
        border-left: 3px solid var(--rust);
        background: var(--rust-soft);
        padding: 1rem 1.15rem;
        color: #694236;
        font-size: 0.75rem;
        line-height: 1.58;
        margin-top: 1.3rem;
    }

    .method-step {
        border-top: 1px solid var(--line);
        padding-top: 1.15rem;
        min-height: 185px;
    }

    .method-num {
        font-family: monospace;
        font-size: 0.66rem;
        color: var(--blue);
        margin-bottom: 1rem;
    }

    .method-title {
        font-size: 1.18rem;
        font-weight: 700;
        letter-spacing: -0.025em;
        margin-bottom: 0.5rem;
    }

    .method-text {
        color: var(--muted);
        font-size: 0.75rem;
        line-height: 1.58;
    }

    .data-caption {
        color: var(--muted);
        font-size: 0.64rem;
        line-height: 1.45;
        margin-top: 0.55rem;
    }

    .footer {
        margin-top: 4rem;
        border-top: 1px solid var(--line);
        padding-top: 1rem;
        display: flex;
        justify-content: space-between;
        gap: 2rem;
        color: var(--muted);
        font-size: 0.64rem;
        line-height: 1.6;
    }

    .footer-right {
        text-align: right;
    }

    div[data-testid="stRadio"] > div {
        gap: 0.45rem;
    }

    div[data-testid="stRadio"] label {
        background: transparent;
        border: 1px solid var(--line);
        padding: 0.38rem 0.7rem;
        border-radius: 999px;
        color: var(--muted);
        font-size: 0.7rem;
    }

    div[data-testid="stRadio"] label:hover {
        border-color: var(--blue);
        color: var(--blue);
    }

    [data-testid="stMetric"] {
        background: var(--white);
        border: 1px solid var(--line);
        padding: 0.9rem;
    }

    @media (max-width: 900px) {
        .hero-copy {
            width: 62%;
        }

        .section-copy {
            display: none;
        }
    }

    @media (max-width: 650px) {
        .mast-right {
            display: none;
        }

        .hero-copy {
            width: 78%;
            left: 1.35rem;
            top: 1.5rem;
        }

        .hero-title {
            font-size: 3rem;
        }

        .hero-image {
            height: 470px;
        }

        .hero-wrap {
            min-height: 470px;
        }

        .footer {
            flex-direction: column;
        }

        .footer-right {
            text-align: left;
        }
    }
    </style>
    """
)


(
    baseline,
    disruption,
    affected_roads,
    affected_bridges,
    buildings_exposed,
    roads_exposed,
    bridges_exposed,
) = load_data()


baseline_accessible = int(
    baseline["baseline_accessible"]
    .fillna(False)
    .sum()
)

baseline_unreachable = int(
    (~baseline["baseline_accessible"]
     .fillna(False))
    .sum()
)

cut_off = int(
    (disruption["status"] == "CUT_OFF").sum()
)

longer_routes = int(
    (disruption["status"] == "LONGER_ROUTE").sum()
)

no_change = int(
    (disruption["status"] == "NO_CHANGE").sum()
)


render_html(
    """
    <div class="masthead">
        <div class="brand">
            <div class="brand-mark"></div>
            FLOOD / INTELLIGENCE
        </div>

        <div class="mast-right">
            <span>
                <span class="status-dot"></span>
                Analysis ready
            </span>
            <span>Rasuwa Corridor</span>
            <span>26.08.2026</span>
        </div>
    </div>
    """
)


hero_path = OUTPUTS / "final_impact_map.png"

if hero_path.exists():
    with open(hero_path, "rb") as image_file:
        encoded_image = base64.b64encode(
            image_file.read()
        ).decode("utf-8")

    hero_src = f"data:image/png;base64,{encoded_image}"

    render_html(
        f"""
        <div class="hero-wrap">
            <img
                class="hero-image"
                src="{hero_src}"
                alt="Flood impact evidence map"
            >

            <div class="hero-overlay"></div>

            <div class="hero-copy">
                <div class="eyebrow">
                    Satellite damage intelligence
                </div>

                <h1 class="hero-title">
                    Flood <span>from space.</span><br>
                    Impact on the ground.
                </h1>

                <div class="hero-description">
                    A satellite-driven analysis of flood-related change,
                    terrain pathways, infrastructure exposure and
                    settlement accessibility across the Rasuwa corridor.
                </div>

                <div class="hero-meta">
                    <div class="meta-block">
                        <div class="meta-label">Event</div>
                        <div class="meta-value">26 Aug 2026</div>
                    </div>

                    <div class="meta-block">
                        <div class="meta-label">Radar pair</div>
                        <div class="meta-value">16 → 28 Aug 2026</div>
                    </div>

                    <div class="meta-block">
                        <div class="meta-label">OSM snapshot</div>
                        <div class="meta-value">27 Jul 2026</div>
                    </div>
                </div>
            </div>
        </div>
        """
    )
else:
    st.warning(
        f"Hero image not found: {hero_path}"
    )


render_html(
    """
    <div class="section-kicker">
        <div>
            <div class="section-number">00 / SIGNAL</div>
            <h2 class="section-title">At a glance</h2>
        </div>

        <div class="section-copy">
            The analysis connects satellite observations,
            terrain structure and pre-event infrastructure
            to understand potential impact.
        </div>
    </div>
    """
)


metric_columns = st.columns(4)


with metric_columns[0]:
    render_html(
        metric_html(
            "Settlements analysed",
            f"{len(disruption):,}",
            "OSM settlements used in accessibility analysis",
        )
    )


with metric_columns[1]:
    render_html(
        metric_html(
            "Potentially affected roads",
            f"{len(affected_roads):,}",
            "Road features intersecting SAR evidence",
        )
    )


with metric_columns[2]:
    render_html(
        metric_html(
            "Buildings in corridor",
            f"{len(buildings_exposed):,}",
            "Buildings inside the 100 m drainage corridor",
        )
    )


with metric_columns[3]:
    render_html(
        metric_html(
            "Potentially affected bridges",
            f"{len(affected_bridges):,}",
            "Bridge features intersecting SAR evidence",
        )
    )


render_html(
    """
    <div class="section-kicker">
        <div>
            <div class="section-number">01 / OBSERVE</div>
            <h2 class="section-title">Read the landscape</h2>
        </div>

        <div class="section-copy">
            Explore the radar signal, drainage structure and
            combined impact visualization.
        </div>
    </div>
    """
)


map_mode = st.radio(
    "Map view",
    [
        "Impact map",
        "SAR change",
        "Drainage network",
        "Before / after",
    ],
    horizontal=True,
    label_visibility="collapsed",
)


map_files = {
    "Impact map": OUTPUTS / "final_impact_map.png",
    "SAR change": OUTPUTS / "gamma0terrain_change.png",
    "Drainage network": OUTPUTS / "drainage_corridor_100m.png",
    "Before / after": OUTPUTS / "event_s1_before_after.png",
}


map_captions = {
    "Impact map": "Flood impact evidence and accessibility scenario",
    "SAR change": "Terrain-corrected Sentinel-1 radar change",
    "Drainage network": "DEM-derived drainage corridor",
    "Before / after": "Sentinel-1 before and after observations",
}


show_image(
    map_files[map_mode],
    map_captions[map_mode],
)


st.markdown(
    '<div class="data-caption">'
    'Visual evidence is interpreted as potential flood-related '
    'change, not as a confirmed damage map.'
    '</div>',
    unsafe_allow_html=True,
)


render_html(
    """
    <div class="note-box">
        <strong>Reading the evidence:</strong>
        Sentinel-1 radar change can reflect surface conditions
        and terrain effects. The workflow therefore combines the
        radar signal with terrain-derived drainage structure and
        pre-event infrastructure rather than treating every anomaly
        as confirmed flooding.
    </div>
    """
)


render_html(
    """
    <div class="section-kicker">
        <div>
            <div class="section-number">02 / TRACE</div>
            <h2 class="section-title">From terrain to impact</h2>
        </div>

        <div class="section-copy">
            The terrain model provides the physical context
            connecting observed change to drainage pathways.
        </div>
    </div>
    """
)


trace_columns = st.columns(3)


trace_cards = [
    (
        "01",
        "Observe",
        "Compare Sentinel-1 before and after observations to identify radar-related surface change.",
    ),
    (
        "02",
        "Trace",
        "Use DEM-derived flow accumulation to identify the main drainage structure and valley pathways.",
    ),
    (
        "03",
        "Overlay",
        "Place pre-event OpenStreetMap buildings, roads and bridges into that physical context.",
    ),
]


for column, (number, title, description) in zip(
    trace_columns,
    trace_cards,
):
    with column:
        render_html(
            f"""
            <div class="evidence-card">
                <div class="evidence-index">{number}</div>
                <div class="evidence-title">{title}</div>
                <div class="evidence-text">
                    {description}
                </div>
            </div>
            """
        )


render_html(
    """
    <div class="section-kicker">
        <div>
            <div class="section-number">03 / IMPACT</div>
            <h2 class="section-title">What could be affected?</h2>
        </div>

        <div class="section-copy">
            Infrastructure intersecting the analytical evidence
            is classified as potentially affected.
        </div>
    </div>
    """
)


impact_columns = st.columns(3)


with impact_columns[0]:
    render_html(
        f"""
        <div class="scenario">
            <div class="scenario-title">Buildings</div>
            <div class="scenario-big">
                {len(buildings_exposed):,}
            </div>
            <div class="scenario-small">
                Buildings located inside the hydrologic corridor.
            </div>
        </div>
        """
    )


with impact_columns[1]:
    render_html(
        f"""
        <div class="scenario">
            <div class="scenario-title">Roads</div>
            <div class="scenario-big">
                {len(affected_roads):,}
            </div>
            <div class="scenario-small">
                Road features intersecting the SAR evidence.
            </div>
        </div>
        """
    )


with impact_columns[2]:
    render_html(
        f"""
        <div class="scenario">
            <div class="scenario-title">Bridges</div>
            <div class="scenario-big">
                {len(affected_bridges):,}
            </div>
            <div class="scenario-small">
                Bridge features intersecting the SAR evidence.
            </div>
        </div>
        """
    )


st.markdown(
    "#### Potentially affected road segments"
)


road_display = affected_roads[
    [
        "osm_id",
        "highway",
        "road_length_m",
        "affected_length_m",
        "affected_fraction",
    ]
].copy()


road_display["road_length_km"] = (
    road_display["road_length_m"] / 1000
).round(2)


road_display["affected_length_m"] = (
    road_display["affected_length_m"]
).round(1)


road_display["affected_fraction_pct"] = (
    road_display["affected_fraction"] * 100
).round(2)


road_display = road_display[
    [
        "osm_id",
        "highway",
        "road_length_km",
        "affected_length_m",
        "affected_fraction_pct",
    ]
].sort_values(
    "affected_fraction_pct",
    ascending=False,
)


st.dataframe(
    road_display,
    width="stretch",
    hide_index=True,
    column_config={
        "osm_id": "OSM ID",
        "highway": "Road class",
        "road_length_km": st.column_config.NumberColumn(
            "Total length (km)",
            format="%.2f",
        ),
        "affected_length_m": st.column_config.NumberColumn(
            "Evidence overlap (m)",
            format="%.1f",
        ),
        "affected_fraction_pct": st.column_config.NumberColumn(
            "Overlap (%)",
            format="%.2f",
        ),
    },
)


render_html(
    """
    <div class="section-kicker">
        <div>
            <div class="section-number">04 / ACCESS</div>
            <h2 class="section-title">Who could lose access?</h2>
        </div>

        <div class="section-copy">
            A network scenario removes potentially affected road
            segments and recalculates settlement-to-hospital access.
        </div>
    </div>
    """
)


access_columns = st.columns(4)


access_metrics = [
    (
        "Baseline reachable",
        baseline_accessible,
        "Settlements with a pre-event hospital route",
    ),
    (
        "Baseline unreachable",
        baseline_unreachable,
        "Already disconnected in the baseline network",
    ),
    (
        "Potentially cut off",
        cut_off,
        "Had a baseline route but lose it in the scenario",
    ),
    (
        "Longer routes",
        longer_routes,
        "Still reachable, but route distance increases",
    ),
]


for column, (label, value, note) in zip(
    access_columns,
    access_metrics,
):
    with column:
        render_html(
            metric_html(
                label,
                f"{value:,}",
                note,
            )
        )


status_counts = disruption[
    "status"
].value_counts().to_dict()


render_html(
    f"""
    <div class="status-row">
        <span class="status-pill">
            BASELINE UNREACHABLE ·
            {status_counts.get("BASELINE_UNREACHABLE", 0)}
        </span>

        <span class="status-pill">
            NO CHANGE ·
            {status_counts.get("NO_CHANGE", 0)}
        </span>

        <span class="status-pill">
            LONGER ROUTE ·
            {status_counts.get("LONGER_ROUTE", 0)}
        </span>

        <span class="status-pill">
            CUT OFF ·
            {status_counts.get("CUT_OFF", 0)}
        </span>
    </div>
    """
)


access_display = disruption[
    [
        "name",
        "status",
        "baseline_distance_km",
        "post_distance_km",
        "route_increase_km",
        "route_increase_percent",
    ]
].copy()


access_display["baseline_distance_km"] = (
    access_display["baseline_distance_km"]
).round(2)


access_display["post_distance_km"] = (
    access_display["post_distance_km"]
).round(2)


access_display["route_increase_km"] = (
    access_display["route_increase_km"]
).round(2)


access_display["route_increase_percent"] = (
    access_display["route_increase_percent"]
).round(1)


st.dataframe(
    access_display.sort_values(
        ["status", "name"],
        na_position="last",
    ),
    width="stretch",
    hide_index=True,
    column_config={
        "name": "Settlement",
        "status": "Scenario status",
        "baseline_distance_km": st.column_config.NumberColumn(
            "Baseline route (km)",
            format="%.2f",
        ),
        "post_distance_km": st.column_config.NumberColumn(
            "Scenario route (km)",
            format="%.2f",
        ),
        "route_increase_km": st.column_config.NumberColumn(
            "Increase (km)",
            format="%.2f",
        ),
        "route_increase_percent": st.column_config.NumberColumn(
            "Increase (%)",
            format="%.1f",
        ),
    },
)


render_html(
    """
    <div class="note-box">
        <strong>Important distinction:</strong>
        BASELINE_UNREACHABLE does not mean flood cut-off.
        CUT_OFF is reserved for settlements that had a baseline
        hospital route but lose all reachable routes under the
        simulated disruption. The disruption is a scenario based
        on potentially affected road segments, not confirmed
        road damage.
    </div>
    """
)


render_html(
    """
    <div class="section-kicker">
        <div>
            <div class="section-number">05 / METHOD</div>
            <h2 class="section-title">How the analysis works</h2>
        </div>

        <div class="section-copy">
            A compact chain from satellite observation to
            network-level consequence.
        </div>
    </div>
    """
)


method_columns = st.columns(4)


methods = [
    (
        "01",
        "OBSERVE",
        "Compare Sentinel-1 radar observations from before and after the event.",
    ),
    (
        "02",
        "TRACE",
        "Use Copernicus DEM terrain and flow accumulation to identify drainage pathways.",
    ),
    (
        "03",
        "OVERLAY",
        "Intersect analytical evidence with pre-event OpenStreetMap infrastructure.",
    ),
    (
        "04",
        "ASSESS",
        "Simulate road disruption and recalculate settlement access to hospitals.",
    ),
]


for column, (number, title, description) in zip(
    method_columns,
    methods,
):
    with column:
        render_html(
            f"""
            <div class="method-step">
                <div class="method-num">{number}</div>
                <div class="method-title">{title}</div>
                <div class="method-text">
                    {description}
                </div>
            </div>
            """
        )


render_html(
    """
    <div class="footer">
        <div>
            Contains modified Copernicus Sentinel data 2026.<br>
            © OpenStreetMap contributors.
        </div>

        <div class="footer-right">
            Educational disaster-response prototype.<br>
            Analytical evidence is not a confirmed operational damage map.
        </div>
    </div>
    """
)