"""Deterministic, deliberately narrow dining-table planning engine.

This is a hackathon prototype, not an engineered or reviewed construction plan.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from datetime import date


SCHEMA_VERSION = 1
TEMPLATE_VERSION = "plywood-pocket-apron-1"
PRICE_DATE = "2026-10-25"
KERF = 0.125  # inches per crosscut
HEIGHT = 30.0
OVERHANG = 2.0

TOOLS = {
    "circular_saw": "Circular saw with a straightedge guide",
    "miter_saw": "Miter saw rated to cut actual 3.5 in square stock",
    "drill": "Drill/driver and suitable bits",
    "pocket_jig": "Pocket-hole jig for 3/4 in stock",
    "clamps": "Clamps",
    "square": "Framing or combination square",
    "tape": "Tape measure",
    "sander": "Sander or sanding block",
    "ppe": "Safety glasses, hearing protection, and dust protection",
}

CATALOG = {
    "top_sheet": {"label": "3/4 in plywood sheet", "kind": "lumber", "length": 96.0, "width": 48.0, "thickness": 0.75, "unitPrice": 69.0},
    "leg_stock": {"label": "4×4 lumber, actual 3.5×3.5 in, 8 ft", "kind": "lumber", "length": 96.0, "width": 3.5, "thickness": 3.5, "unitPrice": 22.0},
    "apron_stock": {"label": "1×4 lumber, actual 0.75×3.5 in, 8 ft", "kind": "lumber", "length": 96.0, "width": 3.5, "thickness": 0.75, "unitPrice": 13.0},
    "angle_bracket": {"label": "Small steel angle bracket", "kind": "hardware", "packSize": 4, "unitPrice": 6.0},
    "pocket_screw": {"label": "1 1/4 in pocket-hole screw", "kind": "hardware", "packSize": 50, "unitPrice": 8.0},
    "top_screw": {"label": "#8 × 1/2 in wood screw for plywood top", "kind": "hardware", "packSize": 25, "unitPrice": 5.0},
    "apron_screw": {"label": "#8 × 3/4 in wood screw for aprons", "kind": "hardware", "packSize": 25, "unitPrice": 5.0},
    "finish": {"label": "Water-based clear finish, 1 qt", "kind": "supply", "packSize": 1, "unitPrice": 22.0},
    "sandpaper": {"label": "Assorted sandpaper, 1 pack", "kind": "supply", "packSize": 1, "unitPrice": 7.0},
    "brush": {"label": "Finish applicator, 1 pack", "kind": "supply", "packSize": 1, "unitPrice": 5.0},
}

REQUIRED_HARDWARE = {"angle_bracket": 8, "pocket_screw": 16, "top_screw": 8, "apron_screw": 8, "finish": 1, "sandpaper": 1, "brush": 1}


@dataclass
class PlanError(Exception):
    message: str
    field: str | None = None

    def as_dict(self):
        return {"error": self.message, "field": self.field}


def _number(value, field, minimum=None, maximum=None):
    try:
        if isinstance(value, bool):
            raise ValueError()
        result = float(value)
    except (ValueError, TypeError):
        raise PlanError(f"Enter a valid {field}.", field) from None
    if not math.isfinite(result) or (minimum is not None and result < minimum) or (maximum is not None and result > maximum):
        limits = f" between {minimum} and {maximum}" if minimum is not None and maximum is not None else ""
        raise PlanError(f"Enter a {field}{limits}.", field)
    return result


def _whole(value, field, minimum=0, maximum=1000):
    result = _number(value, field, minimum, maximum)
    if result != int(result):
        raise PlanError(f"Enter a whole-number {field}.", field)
    return int(result)


def _part(part_id, label, length, width, thickness, material):
    return {"id": part_id, "label": label, "length": round(length, 3), "width": width, "thickness": thickness, "material": material}


def _pack_parts(parts, capacity=96.0):
    """Repeatable first-fit decreasing stock assignment, with kerf per cut."""
    bins = []
    for part in sorted(parts, key=lambda item: (-item["length"], item["id"])):
        need = part["length"] + KERF
        if need > capacity + 1e-8:
            raise PlanError(f"{part['id']} cannot fit an 8 ft board including saw kerf.")
        target = next((stock for stock in bins if stock["remaining"] + 1e-8 >= need), None)
        if target is None:
            target = {"stockId": f"S{len(bins) + 1}", "partIds": [], "remaining": capacity}
            bins.append(target)
        target["partIds"].append(part["id"])
        target["remaining"] = round(target["remaining"] - need, 3)
    return bins


def _inventory(items):
    if not isinstance(items, list) or len(items) > 30:
        raise PlanError("Provide no more than 30 owned-material entries.", "inventory")
    confirmed = {sku: 0 for sku in CATALOG}
    entries = []
    for index, raw in enumerate(items):
        if not isinstance(raw, dict) or raw.get("sku") not in CATALOG:
            raise PlanError(f"Owned-material entry {index + 1} has an unknown item.", "inventory")
        sku = raw["sku"]
        catalog = CATALOG[sku]
        quantity = _whole(raw.get("quantity"), "owned quantity", 1, 1000)
        is_confirmed = raw.get("confirmed") is True
        reason = "Confirm this item before it can reduce purchases."
        matching = False
        if is_confirmed:
            if catalog["kind"] == "lumber":
                try:
                    matching = all(abs(_number(raw.get(key), f"owned {key}", 0.1, 200) - catalog[key]) <= 0.01 for key in ("length", "width", "thickness"))
                except PlanError:
                    matching = False
                reason = "Matches one complete catalog stock unit." if matching else "Actual dimensions differ from the supported stock unit; set aside for review."
            else:
                matching = True
                reason = "Confirmed matching item."
        if matching:
            confirmed[sku] += quantity
        entries.append({"sku": sku, "label": catalog["label"], "quantity": quantity, "confirmed": is_confirmed, "matching": matching, "reason": reason})
    return confirmed, entries


def build_plan(raw):
    if not isinstance(raw, dict):
        raise PlanError("Provide a plan request.")
    idea = str(raw.get("idea", "")).strip()[:500]
    if not idea:
        raise PlanError("Describe the table you want to build.", "idea")
    length = _number(raw.get("length"), "table length", 48, 72)
    width = _number(raw.get("width"), "table width", 28, 40)
    if round(length * 4) != length * 4 or round(width * 4) != width * 4:
        raise PlanError("Use quarter-inch increments for table dimensions.", "dimensions")
    budget = _number(raw.get("budget"), "budget", 0, 100000)
    skill = raw.get("skill")
    if skill not in ("beginner", "intermediate"):
        raise PlanError("Choose beginner or intermediate instruction detail.", "skill")
    if raw.get("confirmed") is not True:
        raise PlanError("Review and confirm your inputs before generating.", "confirmed")
    tools = raw.get("tools")
    if not isinstance(tools, list) or any(tool not in TOOLS for tool in tools):
        raise PlanError("Select your available tools from the checklist.", "tools")
    missing_tools = [name for key, name in TOOLS.items() if key not in tools]
    if missing_tools:
        raise PlanError("This template requires: " + "; ".join(missing_tools) + ". Add the tools before generating a ready-to-build plan.", "tools")

    leg_length = HEIGHT - CATALOG["top_sheet"]["thickness"]
    long_apron = length - 2 * (OVERHANG + CATALOG["leg_stock"]["width"])
    short_apron = width - 2 * (OVERHANG + CATALOG["leg_stock"]["width"])
    parts = [_part("T1", "Tabletop", length, width, 0.75, "top_sheet")]
    parts += [_part(f"L{i}", "Leg", leg_length, 3.5, 3.5, "leg_stock") for i in range(1, 5)]
    parts += [_part(f"A{i}", "Long apron", long_apron, 3.5, 0.75, "apron_stock") for i in range(1, 3)]
    parts += [_part(f"B{i}", "Short apron", short_apron, 3.5, 0.75, "apron_stock") for i in range(1, 3)]

    leg_bins = _pack_parts([p for p in parts if p["material"] == "leg_stock"])
    apron_bins = _pack_parts([p for p in parts if p["material"] == "apron_stock"])
    if length > 96 or width > 48:
        raise PlanError("The tabletop does not fit one supported plywood sheet.")
    stock = {"top_sheet": [{"stockId": "TOP-1", "partIds": ["T1"], "remaining": None}], "leg_stock": leg_bins, "apron_stock": apron_bins}
    confirmed_inventory, inventory_entries = _inventory(raw.get("inventory", []))

    required = {"top_sheet": 1, "leg_stock": len(leg_bins), "apron_stock": len(apron_bins), **REQUIRED_HARDWARE}
    shopping = []
    total = 0.0
    for sku, count in required.items():
        item = CATALOG[sku]
        owned_units = min(confirmed_inventory[sku], count)
        remaining = count - owned_units
        if item["kind"] == "lumber":
            purchase_units = remaining
            purchase_label = "stock units"
        else:
            purchase_units = math.ceil(remaining / item["packSize"])
            purchase_label = f"packs of {item['packSize']}"
        cost = round(purchase_units * item["unitPrice"], 2)
        total += cost
        shopping.append({"sku": sku, "label": item["label"], "needed": count, "ownedUsed": owned_units, "toBuy": purchase_units, "purchaseUnit": purchase_label, "unitPrice": item["unitPrice"], "cost": cost})
    total = round(total, 2)

    detail = skill == "beginner"
    steps = [
        {"id": "S1", "title": "Check and mark every piece", "partIds": [p["id"] for p in parts], "tools": ["tape", "square"], "action": "Confirm the actual stock sizes. Mark each cut using the part IDs in the cut list.", "detail": "Measure twice from the same reference edge. Mark the waste side of each line and label every piece before cutting." if detail else "Mark and label all parts.", "check": "All nine parts are marked and match the cut list.", "safety": "Inspect stock for damage before cutting. Set damaged pieces aside."},
        {"id": "S2", "title": "Cut the tabletop", "partIds": ["T1"], "tools": ["circular_saw", "square", "clamps"], "action": f"Cut T1 from the plywood sheet to {length:g} × {width:g} in.", "detail": "Support the whole sheet, clamp a straightedge guide, and make the cut on the waste side of the mark." if detail else "Use a clamped straightedge guide.", "check": "T1 measures the requested length and width and its corners are square.", "safety": "Wear eye, hearing, and dust protection. Keep hands clear of the blade path."},
        {"id": "S3", "title": "Cut the legs and aprons", "partIds": ["L1", "L2", "L3", "L4", "A1", "A2", "B1", "B2"], "tools": ["miter_saw", "tape", "square"], "action": f"Cut four legs to {leg_length:g} in, two long aprons to {long_apron:g} in, and two short aprons to {short_apron:g} in.", "detail": "Keep matched pieces together. Account for the 1/8 in saw kerf shown in the stock assignment." if detail else "Label each piece as it is cut.", "check": "Each matched pair has equal length; all part IDs are present.", "safety": "Use a saw rated for the 3.5 in square leg stock. Clamp short pieces and keep hands outside the saw's marked safe zone."},
        {"id": "S4", "title": "Dry fit the base", "partIds": ["L1", "L2", "L3", "L4", "A1", "A2", "B1", "B2"], "tools": ["clamps", "square"], "action": "Place the aprons between the legs, flush with the top of each leg. Clamp without fasteners.", "detail": "Long aprons run along the table length; short aprons close the ends. Check that the outer leg faces are 2 in in from the tabletop edges." if detail else "Check the 2 in tabletop overhang.", "check": "The frame is square and the tabletop overhang is even on all sides.", "safety": "Support the frame while clamping so it cannot tip."},
        {"id": "S5", "title": "Fasten the apron frame", "partIds": ["L1", "L2", "L3", "L4", "A1", "A2", "B1", "B2"], "tools": ["pocket_jig", "drill", "clamps", "square"], "action": "Drill two pocket holes at each apron end and join the aprons to the legs with 16 pocket-hole screws.", "detail": "Set the jig for actual 3/4 in apron thickness, clamp each joint, and check square after tightening." if detail else "Clamp and check square as you fasten.", "check": "All eight apron ends are fixed; the base sits level and remains square.", "safety": "Follow the jig and driver instructions; clamp each workpiece before drilling."},
        {"id": "S6", "title": "Attach the tabletop", "partIds": ["T1", "L1", "L2", "L3", "L4", "A1", "A2", "B1", "B2"], "tools": ["drill", "tape", "clamps"], "action": "Center T1 over the base. Fasten eight angle brackets to the aprons and the underside of T1 using eight 3/4 in apron screws and eight 1/2 in top screws.", "detail": "Pre-drill shallow pilot holes. Check screw length against actual material thickness so no screw reaches the tabletop face." if detail else "Pre-drill and check screw depth.", "check": "The top is centered with a 2 in overhang; no fastener pierces the surface.", "safety": "Use a depth stop and keep hands clear of the drilling point."},
        {"id": "S7", "title": "Sand and finish", "partIds": ["T1", "L1", "L2", "L3", "L4", "A1", "A2", "B1", "B2"], "tools": ["sander", "ppe"], "action": "Ease sharp edges, sand all accessible surfaces, and apply the clear finish according to its label.", "detail": "Remove dust between coats. Follow the chosen product's coating and cure times before putting the table into service." if detail else "Follow the finish label for coating and cure times.", "check": "Edges feel smooth and the finish has cured for the time stated by its manufacturer.", "safety": "Use ventilation and protective equipment specified on the finish label. Control sanding dust."},
    ]

    ids = {part["id"] for part in parts}
    assert len(ids) == len(parts)
    assert all(set(step["partIds"]) <= ids for step in steps)
    assigned = [part_id for bins in stock.values() for bin_item in bins for part_id in bin_item["partIds"]]
    assert sorted(assigned) == sorted(ids)

    canonical = {"idea": idea, "length": length, "width": width, "budget": budget, "skill": skill, "tools": sorted(tools), "inventory": inventory_entries}
    revision = hashlib.sha256(json.dumps(canonical, sort_keys=True).encode()).hexdigest()[:10]
    return {
        "schemaVersion": SCHEMA_VERSION, "templateId": TEMPLATE_VERSION, "revision": revision,
        "prototypeNotice": "Prototype plan only. Have the construction method and final dimensions reviewed before a physical build; no load rating or certification is claimed.",
        "inputs": {"idea": idea, "length": length, "width": width, "height": HEIGHT, "budget": budget, "skill": skill, "units": "in", "currency": "USD"},
        "geometry": {"length": length, "width": width, "height": HEIGHT, "legSize": 3.5, "overhang": OVERHANG, "apronDepth": 3.5},
        "parts": parts, "stockAssignment": stock, "shopping": shopping, "inventory": inventory_entries,
        "tools": [{"id": key, "label": label, "available": True} for key, label in TOOLS.items()],
        "steps": steps,
        "estimate": {"purchaseSubtotal": total, "budget": budget, "overBudget": total > budget, "priceDate": PRICE_DATE, "priceSource": "Illustrative sample prices, not retailer quotes", "exclusions": "Tax, delivery, and tool purchases are excluded."},
        "policy": {"kerf": KERF, "stockRule": "Only confirmed, exact-size catalog stock units count. No offcuts or partial-board matching.", "height": HEIGHT},
    }
