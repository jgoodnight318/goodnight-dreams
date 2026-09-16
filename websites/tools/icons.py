#!/usr/bin/env python3
"""Shared inline-SVG line icon set, per DESIGN.md: 26x26, 2px stroke, currentColor (gold via
`.service svg { color: var(--gold) }`), no fills, no raster imagery anywhere on the page.
Reuses Jarmer Electric's exact icon markup where the concept transfers across trades, and
adds a small number of new icons for HVAC / auto-repair / painting service tiles.
"""

_WRAP = ('<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
         'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{}</svg>')


def _svg(inner):
    return _WRAP.format(inner)


ICONS = {
    # from Jarmer Electric — reused as-is where the concept transfers
    "panel": _svg('<rect x="5" y="2.5" width="14" height="19" rx="1.5"/><line x1="9" y1="7" x2="15" y2="7"/>'
                  '<line x1="9" y1="11" x2="15" y2="11"/><line x1="9" y1="15" x2="12" y2="15"/>'),
    "wiring": _svg('<path d="M4 14c3-8 13-8 16 0"/><path d="M4 14v4"/><path d="M20 14v4"/><circle cx="12" cy="9" r="1.6"/>'),
    "lighting": _svg('<path d="M9 18h6"/><path d="M10 21h4"/><path d="M12 3a6 6 0 0 0-3.5 10.9c.8.6 1.5 1.6 1.5 2.6h4c0-1 '
                      '.7-2 1.5-2.6A6 6 0 0 0 12 3z"/>'),
    "bolt": _svg('<polyline points="13 2 6 13.5 12 13.5 11 22 18 10.5 12 10.5 13 2"/>'),
    "remodel": _svg('<path d="M3 21v-8l9-7 9 7v8"/><path d="M9 21v-6h6v6"/>'),
    "shield-check": _svg('<path d="M12 2 4 5v6c0 5 3.4 9.4 8 11 4.6-1.6 8-6 8-11V5l-8-3z"/><polyline points="9 12 11 14 15 9.5"/>'),
    # HVAC
    "flame": _svg('<path d="M12 2c1.5 3-2 4.5-2 7.5a2 2 0 0 0 4 0c1.5 1.2 2 2.7 2 4.2a5 5 0 0 1-10 0C6 9.5 9.5 6.5 12 2z"/>'),
    "snowflake": _svg('<line x1="12" y1="2" x2="12" y2="22"/><line x1="4.5" y1="6" x2="19.5" y2="18"/>'
                       '<line x1="19.5" y1="6" x2="4.5" y2="18"/><line x1="3" y1="12" x2="21" y2="12"/>'),
    "duct": _svg('<rect x="3" y="8" width="18" height="8" rx="1"/><line x1="7" y1="8" x2="7" y2="16"/>'
                 '<line x1="12" y1="8" x2="12" y2="16"/><line x1="17" y1="8" x2="17" y2="16"/>'),
    "gauge": _svg('<circle cx="12" cy="13" r="8"/><path d="M12 13 15.5 9"/><path d="M9 6.5 8 4"/><path d="M15 6.5 16 4"/>'),
    "fridge": _svg('<rect x="6" y="2" width="12" height="20" rx="1.5"/><line x1="6" y1="10" x2="18" y2="10"/>'
                    '<line x1="9" y1="5" x2="9" y2="7.5"/><line x1="9" y1="13" x2="9" y2="15.5"/>'),
    "wrench-hvac": _svg('<path d="M14.7 6.3a4 4 0 0 0-5.4 5.4L4 17l3 3 5.3-5.3a4 4 0 0 0 5.4-5.4l-2.3 2.3-2-2z"/>'),
    # Auto repair
    "car": _svg('<path d="M4 16v-3.5L6 8h12l2 4.5V16"/><path d="M4 16h16"/><circle cx="7.5" cy="17.5" r="1.6"/>'
                '<circle cx="16.5" cy="17.5" r="1.6"/>'),
    "tire": _svg('<circle cx="12" cy="12" r="8.5"/><circle cx="12" cy="12" r="3"/><line x1="12" y1="3.5" x2="12" y2="7.2"/>'
                 '<line x1="12" y1="16.8" x2="12" y2="20.5"/><line x1="3.5" y1="12" x2="7.2" y2="12"/>'
                 '<line x1="16.8" y1="12" x2="20.5" y2="12"/>'),
    "battery": _svg('<rect x="3" y="8" width="16" height="10" rx="1"/><line x1="19" y1="11" x2="21" y2="11"/>'
                     '<line x1="19" y1="15" x2="21" y2="15"/><line x1="8" y1="8" x2="8" y2="5.5"/>'
                     '<line x1="13" y1="8" x2="13" y2="5.5"/>'),
    "oil": _svg('<path d="M12 3c2.2 3.4-2.8 5.6-2.8 9.3a2.8 2.8 0 0 0 5.6 0C14.8 8.6 12 6.4 12 3z"/>'
                '<path d="M8.5 20.5h7"/>'),
    "wrench": _svg('<path d="M14.7 6.3a4 4 0 0 0-5.4 5.4L4 17l3 3 5.3-5.3a4 4 0 0 0 5.4-5.4l-2.3 2.3-2-2z"/>'),
    "brake": _svg('<circle cx="12" cy="12" r="8.5"/><path d="M12 3.5v5"/><path d="M12 15.5v5"/>'
                   '<path d="M4.4 8.3 9 10.9"/><path d="M15 13.1l4.6 2.6"/>'),
    # Painting
    "roller": _svg('<rect x="3" y="4" width="12" height="6" rx="1.5"/><line x1="17" y1="7" x2="21" y2="7"/>'
                    '<line x1="21" y1="7" x2="21" y2="15"/><line x1="21" y1="15" x2="17" y2="15"/>'
                    '<line x1="17" y1="15" x2="17" y2="21"/>'),
    "brush": _svg('<path d="M19 3 12 10"/><path d="M9 13c-3 0-4 2-4 4 0 2-1 3-1 3s2 1 4 1c2 0 4-1 4-4 0-2 1-3 1-3"/>'
                   '<path d="M12 10c1 1 3 3 4 4"/>'),
    "prep": _svg('<rect x="4" y="3" width="16" height="18" rx="1.5"/><line x1="8" y1="8" x2="16" y2="8"/>'
                 '<line x1="8" y1="12" x2="16" y2="12"/><line x1="8" y1="16" x2="12" y2="16"/>'),
    "clock": _svg('<circle cx="12" cy="12" r="8.5"/><polyline points="12 7 12 12 15.5 14"/>'),
}


def icon(key):
    try:
        return ICONS[key]
    except KeyError:
        raise KeyError(f"no icon named {key!r}; available: {sorted(ICONS)}")
