import streamlit as st


def render_html(html_str: str) -> None:
    """
    Randează HTML fără a permite parser-ului Markdown să interpreteze
    liniile indentate (4+ spații) drept blocuri de cod <pre><code>.
    """
    clean = "\n".join(line.strip() for line in html_str.splitlines() if line.strip())
    if hasattr(st, "html"):
        st.html(clean)
    else:
        st.markdown(clean, unsafe_allow_html=True)


def load_css():
    render_html("""
<style>
/* Stil container principal */
.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 2.5rem !important;
    max-width: 1400px !important;
}

/* Banner informativ de sus */
.info-alert-banner {
    background: rgba(30, 58, 138, 0.2);
    border: 1px solid rgba(59, 130, 246, 0.35);
    border-radius: 10px;
    padding: 10px 16px;
    margin-bottom: 8px;
    font-size: 13px;
    color: #93c5fd;
}

/* Banner informativ ordine medie */
.order-alert-banner,
.footer-alert-banner {
    background: rgba(16, 185, 129, 0.12);
    border: 1px solid rgba(16, 185, 129, 0.35);
    border-radius: 10px;
    padding: 10px 16px;
    margin-top: 0;
    margin-bottom: 18px;
    font-size: 13px;
    color: #6ee7b7;
    font-weight: 500;
}

/* Card unitate */
.unit-block {
    background: #141824;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 16px 18px;
    margin-bottom: 18px;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25);
}

.unit-block-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    padding-bottom: 10px;
    margin-bottom: 12px;
}

.unit-title {
    font-size: 15px;
    font-weight: 700;
    color: #ffffff;
    margin: 0;
}

.unit-stats-badges {
    display: flex;
    gap: 16px;
    font-size: 13px;
    font-weight: 600;
}

.badge-boys {
    color: #60a5fa;
}

.badge-girls {
    color: #f87171;
}

.section-subtitle {
    font-size: 12px;
    color: #94a3b8;
    margin-top: 8px;
    margin-bottom: 6px;
    font-weight: 600;
}

/* Grilă sloturi */
.slots-container {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 4px;
    margin-bottom: 12px;
}

.slot-item {
    min-width: 95px;
    max-width: 125px;
    flex: 1 0 95px;
    height: 46px;
    border-radius: 8px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 3px 5px;
    box-sizing: border-box;
}

.slot-name {
    font-size: 11px;
    font-weight: 600;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 100%;
}

.slot-avg {
    font-size: 11px;
    opacity: 0.92;
    font-weight: 600;
}

.slot-boy {
    background: #1d4ed8;
    color: #ffffff;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.25);
}

.slot-girl {
    background: #b91c1c;
    color: #ffffff;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.25);
}

.slot-empty-boy {
    border: 1.5px dashed rgba(59, 130, 246, 0.45);
    background: rgba(30, 58, 138, 0.06);
}

.slot-empty-girl {
    border: 1.5px dashed rgba(239, 68, 68, 0.45);
    background: rgba(153, 27, 27, 0.06);
}

.slot-highlight {
    background: #f59e0b !important;
    color: #000000 !important;
    font-weight: 700 !important;
    box-shadow: 0 0 10px rgba(245, 158, 11, 0.8) !important;
}

/* Panou Statistici generale */
.stats-panel {
    background: #141824;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 18px;
    box-shadow: 0 4px 18px rgba(0, 0, 0, 0.25);
}

/* Pe PC / Laptop / Tabletă mare (>= 992px): panoul din dreapta rămâne fixat (sticky) la derulare printre unități */
@media (min-width: 992px) {
    /* Asigurăm că niciun container părinte nu blochează comportamentul sticky */
    .block-container,
    div[data-testid="stVerticalBlock"]:has(> div[data-testid="stHorizontalBlock"]:has(.stats-panel)),
    div[data-testid="stVerticalBlock"]:has(.stats-panel) {
        overflow: visible !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.stats-panel) {
        display: flex !important;
        flex-direction: row !important;
        align-items: flex-start !important;
        overflow: visible !important;
    }

    /* Coloana de statistici (stColumn) devine STICKY la nivel de coloană flex */
    div[data-testid="stHorizontalBlock"]:has(.stats-panel) > div[data-testid="stColumn"]:has(.stats-panel),
    div[data-testid="stHorizontalBlock"]:has(.stats-panel) > div[data-testid="stColumn"]:nth-child(2) {
        order: 2 !important;
        position: -webkit-sticky !important;
        position: sticky !important;
        top: 60px !important;
        align-self: flex-start !important;
        z-index: 40 !important;
        overflow: visible !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.stats-panel) > div[data-testid="stColumn"]:not(:has(.stats-panel)),
    div[data-testid="stHorizontalBlock"]:has(.stats-panel) > div[data-testid="stColumn"]:nth-child(1) {
        order: 1 !important;
        overflow: visible !important;
    }

    .stats-panel {
        max-height: calc(100vh - 80px) !important;
        overflow-y: auto !important;
    }

    .stats-panel::-webkit-scrollbar {
        width: 4px;
    }
    .stats-panel::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.15);
        border-radius: 4px;
    }
}

/* Pe telefoane smartphone (< 992px): panoul este mutat sus, deasupra primelor unități */
@media (max-width: 991px) {
    div[data-testid="stHorizontalBlock"]:has(.stats-panel) {
        display: flex !important;
        flex-direction: column !important;
        width: 100% !important;
    }

    /* Panoul de statistici este ordonat primul (order: -1) */
    div[data-testid="stHorizontalBlock"]:has(.stats-panel) > div[data-testid="stColumn"]:has(.stats-panel),
    div[data-testid="stHorizontalBlock"]:has(.stats-panel) > div[data-testid="stColumn"]:nth-child(2) {
        order: -1 !important;
        position: static !important;
        top: auto !important;
        width: 100% !important;
        min-width: 100% !important;
        margin-bottom: 24px !important;
    }

    /* Unitățile de practică vin imediat sub statistici (order: 2) */
    div[data-testid="stHorizontalBlock"]:has(.stats-panel) > div[data-testid="stColumn"]:not(:has(.stats-panel)),
    div[data-testid="stHorizontalBlock"]:has(.stats-panel) > div[data-testid="stColumn"]:nth-child(1) {
        order: 2 !important;
        width: 100% !important;
        min-width: 100% !important;
    }

    .stats-panel {
        position: static !important;
        top: auto !important;
        max-height: none !important;
        overflow-y: visible !important;
    }
}

.stats-title {
    font-size: 16px;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 14px;
}

.kpi-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
    margin-bottom: 10px;
}

.kpi-card {
    border-radius: 8px;
    padding: 10px 4px;
    text-align: center;
}

.kpi-blue {
    background: rgba(30, 58, 138, 0.25);
    border: 1px solid rgba(59, 130, 246, 0.3);
}

.kpi-blue .kpi-num {
    color: #60a5fa;
}

.kpi-green {
    background: rgba(16, 185, 129, 0.18);
    border: 1px solid rgba(16, 185, 129, 0.35);
}

.kpi-green .kpi-num {
    color: #34d399;
}

.kpi-amber {
    background: rgba(245, 158, 11, 0.18);
    border: 1px solid rgba(245, 158, 11, 0.35);
}

.kpi-amber .kpi-num {
    color: #fbbf24;
}

.kpi-num {
    font-size: 20px;
    font-weight: 800;
    line-height: 1.1;
    margin-bottom: 2px;
}

.kpi-lbl {
    font-size: 10px;
    color: #94a3b8;
    font-weight: 500;
}

.kpi-sub-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    margin-bottom: 16px;
}

.kpi-sub-card {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 8px;
    padding: 8px 6px;
    text-align: center;
}

.kpi-sub-val {
    display: block;
    font-size: 12px;
    font-weight: 700;
    color: #f1f5f9;
}

.kpi-sub-lbl {
    display: block;
    font-size: 10px;
    color: #64748b;
    margin-top: 2px;
}

.stats-occupancy-block {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 10px;
    padding: 12px;
    margin-bottom: 16px;
}

.occupancy-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 6px;
}

.occupancy-label {
    font-size: 12px;
    font-weight: 600;
    color: #e2e8f0;
}

.occupancy-pct {
    font-size: 13px;
    font-weight: 700;
    color: #3b82f6;
}

.occupancy-bar-bg {
    width: 100%;
    height: 7px;
    background: #1e293b;
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 6px;
}

.occupancy-bar-fill {
    height: 100%;
    background: #3b82f6;
    border-radius: 4px;
    transition: width 0.3s ease;
}

.occupancy-footer {
    font-size: 11px;
    color: #94a3b8;
}

.top-units-title {
    font-size: 12px;
    font-weight: 600;
    color: #e2e8f0;
    margin-bottom: 10px;
}

.top-unit-row {
    margin-bottom: 9px;
}

.top-unit-info {
    display: flex;
    justify-content: space-between;
    font-size: 11px;
    margin-bottom: 3px;
}

.top-unit-name {
    color: #cbd5e1;
    font-weight: 500;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 170px;
}

.top-unit-pct {
    color: #60a5fa;
    font-weight: 600;
}

.top-unit-bar-bg {
    width: 100%;
    height: 5px;
    background: #1e293b;
    border-radius: 3px;
    overflow: hidden;
}

.top-unit-bar-fill {
    height: 100%;
    background: #2563eb;
    border-radius: 3px;
}

.legend-title {
    font-size: 11px;
    font-weight: 600;
    color: #94a3b8;
    margin-top: 16px;
    margin-bottom: 6px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.legend-row {
    display: flex;
    gap: 12px;
    font-size: 11px;
    color: #cbd5e1;
}

.legend-item {
    display: flex;
    align-items: center;
    gap: 5px;
}

.legend-box {
    width: 12px;
    height: 12px;
    border-radius: 3px;
    display: inline-block;
}

.legend-boy {
    background: #1d4ed8;
}

.legend-girl {
    background: #b91c1c;
}

.legend-empty {
    border: 1.5px dashed rgba(255, 255, 255, 0.4);
    background: rgba(255, 255, 255, 0.05);
}
</style>
""")


def render_unit_card(unit_name: str, unit: dict, cautare: str = "") -> None:
    boys = sorted(unit["option1"]["boys"], key=lambda s: s.get("average", 0), reverse=True)
    girls = sorted(unit["option1"]["girls"], key=lambda s: s.get("average", 0), reverse=True)

    boys_cap = unit.get("boys_capacity", 0)
    girls_cap = unit.get("girls_capacity", 0)

    clean_unit_title = unit_name.replace("UM_", "UM ")

    # Badge-uri din dreapta antetului
    boys_badge = f'<span class="badge-boys">Băieți: {len(boys)} / {boys_cap}</span>' if boys_cap > 0 else ""
    girls_badge = f'<span class="badge-girls">Fete: {len(girls)} / {girls_cap}</span>' if girls_cap > 0 else ""

    # Sloturi băieți
    boys_slots_html = ""
    if boys_cap > 0:
        boys_slots = []
        for s in boys:
            name = f"{s.get('last_name', '')} {s.get('first_name', '')}"
            avg = f"({s.get('average', '')})"
            is_highlight = bool(cautare and (cautare in name.lower()))
            cls = "slot-highlight" if is_highlight else "slot-boy"
            boys_slots.append(
                f'<div class="slot-item {cls}"><span class="slot-name">{name}</span><span class="slot-avg">{avg}</span></div>'
            )
        for _ in range(max(boys_cap - len(boys), 0)):
            boys_slots.append('<div class="slot-item slot-empty-boy"></div>')

        boys_slots_html = f"""
        <div class="section-subtitle">Băieți ({boys_cap} locuri)</div>
        <div class="slots-container">{"".join(boys_slots)}</div>
        """

    # Sloturi fete
    girls_slots_html = ""
    if girls_cap > 0:
        girls_slots = []
        for s in girls:
            name = f"{s.get('last_name', '')} {s.get('first_name', '')}"
            avg = f"({s.get('average', '')})"
            is_highlight = bool(cautare and (cautare in name.lower()))
            cls = "slot-highlight" if is_highlight else "slot-girl"
            girls_slots.append(
                f'<div class="slot-item {cls}"><span class="slot-name">{name}</span><span class="slot-avg">{avg}</span></div>'
            )
        for _ in range(max(girls_cap - len(girls), 0)):
            girls_slots.append('<div class="slot-item slot-empty-girl"></div>')

        girls_slots_html = f"""
        <div class="section-subtitle">Fete ({girls_cap} locuri)</div>
        <div class="slots-container">{"".join(girls_slots)}</div>
        """

    card_html = f"""
    <div class="unit-block">
        <div class="unit-block-header">
            <div class="unit-title">🏢 {clean_unit_title}</div>
            <div class="unit-stats-badges">{boys_badge} &nbsp;&nbsp; {girls_badge}</div>
        </div>
        {boys_slots_html}
        {girls_slots_html}
    </div>
    """
    render_html(card_html)


def render_stats_sidebar(specializare: str, monitor: dict, students: list, choices: list) -> None:
    from monitor_utils import normalize_spec

    norm_spec = normalize_spec(specializare)
    spec_students = [s for s in students if normalize_spec(s.get("specialization", "")) == norm_spec]
    total_students = len(spec_students)

    choices_map = {c["student_id"]: c for c in choices}
    enrolled_count = len([s for s in spec_students if s["id"] in choices_map and choices_map[s["id"]].get("option1")])
    unenrolled_count = max(total_students - enrolled_count, 0)

    spec_units = monitor.get(specializare, {})
    total_capacity = sum(u.get("boys_capacity", 0) + u.get("girls_capacity", 0) for u in spec_units.values())
    total_occupied = sum(len(u["option1"]["boys"]) + len(u["option1"]["girls"]) for u in spec_units.values())

    occupancy_pct = (total_occupied / total_capacity * 100) if total_capacity > 0 else 0
    enrolled_pct = (enrolled_count / total_students * 100) if total_students > 0 else 0
    unenrolled_pct = (unenrolled_count / total_students * 100) if total_students > 0 else 0

    # Top 5 unități după gradul de ocupare
    top_units = []
    for u_name, u_data in spec_units.items():
        cap = u_data.get("boys_capacity", 0) + u_data.get("girls_capacity", 0)
        occ = len(u_data["option1"]["boys"]) + len(u_data["option1"]["girls"])
        pct = (occ / cap * 100) if cap > 0 else 0
        top_units.append((u_name, occ, cap, pct))

    top_units.sort(key=lambda x: (x[1], x[3]), reverse=True)
    top_5 = top_units[:5]

    top_units_html = ""
    for u_name, occ, cap, pct in top_5:
        clean_name = u_name.replace("UM_", "UM ")
        top_units_html += f"""
        <div class="top-unit-row">
            <div class="top-unit-info">
                <span class="top-unit-name" title="{u_name}">{clean_name}</span>
                <span class="top-unit-pct">{pct:.1f}%</span>
            </div>
            <div class="top-unit-bar-bg">
                <div class="top-unit-bar-fill" style="width: {min(pct, 100):.1f}%;"></div>
            </div>
        </div>
        """

    stats_html = f"""
    <div class="stats-panel">
        <div class="stats-title">Statistici generale</div>

        <div class="kpi-grid">
            <div class="kpi-card kpi-blue">
                <div class="kpi-num">{total_students}</div>
                <div class="kpi-lbl">Total elevi</div>
            </div>
            <div class="kpi-card kpi-green">
                <div class="kpi-num">{enrolled_count}</div>
                <div class="kpi-lbl">Cu opțiune</div>
            </div>
            <div class="kpi-card kpi-amber">
                <div class="kpi-num">{unenrolled_count}</div>
                <div class="kpi-lbl">Fără opțiune</div>
            </div>
        </div>

        <div class="kpi-sub-row">
            <div class="kpi-sub-card">
                <span class="kpi-sub-val">{enrolled_count} ({enrolled_pct:.1f}%)</span>
                <span class="kpi-sub-lbl">au ales opțiunea</span>
            </div>
            <div class="kpi-sub-card">
                <span class="kpi-sub-val">{unenrolled_count} ({unenrolled_pct:.1f}%)</span>
                <span class="kpi-sub-lbl">fără opțiune</span>
            </div>
        </div>

        <div class="stats-occupancy-block">
            <div class="occupancy-header">
                <span class="occupancy-label">Grad de ocupare</span>
                <span class="occupancy-pct">{occupancy_pct:.1f}%</span>
            </div>
            <div class="occupancy-bar-bg">
                <div class="occupancy-bar-fill" style="width: {min(occupancy_pct, 100):.1f}%;"></div>
            </div>
            <div class="occupancy-footer">Locuri ocupate: {total_occupied} / {total_capacity}</div>
        </div>

        <div class="top-units-title">Top 5 unități după gradul de ocupare</div>
        <div class="top-units-list">
            {top_units_html if top_units_html else '<div style="color: #64748b; font-size: 11px;">Nicio opțiune exprimată încă</div>'}
        </div>

        <div class="legend-title">Legendă</div>
        <div class="legend-row">
            <div class="legend-item"><span class="legend-box legend-boy"></span> Băieți</div>
            <div class="legend-item"><span class="legend-box legend-girl"></span> Fete</div>
            <div class="legend-item"><span class="legend-box legend-empty"></span> Loc liber</div>
        </div>
    </div>
    """
    render_html(stats_html)
