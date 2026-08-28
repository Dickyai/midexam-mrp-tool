# =========================================================
# MRP LOT SIZING SYSTEM — versi web (PyScript)
# Logika inti IDENTIK dengan versi Colab, hanya input()
# blocking diganti dengan parameter fungsi agar bisa
# dipanggil dari form HTML.
# =========================================================

from math import inf
from pyscript import document, window

SETUP_COST = 650
HOLDING_COST = 1.5
LEAD_TIME = 1
PERIODS = 12

pairs = [
    (1, 2), (1, 7), (1, 8), (7, 2), (7, 3), (7, 8),
    (2, 6), (2, 7), (2, 8), (6, 2), (6, 3), (6, 4)
]


def generate_requirement(digits, a, b):
    d1 = digits[a - 1]
    d2 = digits[b - 1]

    if d1 == 0 and d2 == 0:
        d1 = digits[0]
        d2 = digits[-1]
    elif d1 == 0:
        return d2 * 10

    return int(f"{d1}{d2}") * 10


def calc_holding_cost(demands, start, end):
    hc = 0
    for j in range(start + 1, end + 1):
        hc += demands[j] * (j - start) * HOLDING_COST
    return hc


def calc_part_period(demands, start, end):
    pp = 0
    for j in range(start + 1, end + 1):
        pp += demands[j] * (j - start)
    return pp


def heuristic_mcp(nr, start):
    best_end = start
    prev_value = inf
    details = []

    for j in range(start, PERIODS):
        hc = calc_holding_cost(nr, start, j)
        total = SETUP_COST + hc
        periods = j - start + 1
        value = total / periods

        if value <= prev_value:
            decision = "LANJUT"
            prev_value = value
            best_end = j
        else:
            decision = "STOP"

        details.append({
            "coverage": f"{start+1}-{j+1}", "holding": round(hc, 2),
            "total": round(total, 2), "mcp": round(value, 2), "decision": decision
        })

        if decision == "STOP":
            break

    qty = sum(nr[start:best_end + 1])
    return best_end, qty, details


def heuristic_ppb(nr, start):
    EPP = SETUP_COST / HOLDING_COST
    best_end = start
    details = []

    for j in range(start, PERIODS):
        pp = calc_part_period(nr, start, j)
        decision = "LANJUT" if pp <= EPP else "STOP"
        if decision == "LANJUT":
            best_end = j

        details.append({
            "coverage": f"{start+1}-{j+1}", "part_period": round(pp, 2),
            "EPP": round(EPP, 2), "decision": decision
        })

        if decision == "STOP":
            break

    qty = sum(nr[start:best_end + 1])
    return best_end, qty, details


def heuristic_ltc(nr, start):
    best_end = start
    smallest_diff = inf
    details = []

    for j in range(start, PERIODS):
        hc = calc_holding_cost(nr, start, j)
        diff = abs(SETUP_COST - hc)

        if diff <= smallest_diff:
            decision = "LANJUT"
            smallest_diff = diff
            best_end = j
        else:
            decision = "STOP"

        details.append({
            "coverage": f"{start+1}-{j+1}", "holding_cost": round(hc, 2),
            "setup_cost": SETUP_COST, "difference": round(diff, 2), "decision": decision
        })

        if decision == "STOP":
            break

    qty = sum(nr[start:best_end + 1])
    return best_end, qty, details


def heuristic_luc(nr, start):
    best_end = start
    prev_value = inf
    details = []

    for j in range(start, PERIODS):
        hc = calc_holding_cost(nr, start, j)
        total = SETUP_COST + hc
        units = sum(nr[start:j + 1])
        value = inf if units == 0 else total / units

        if value <= prev_value:
            decision = "LANJUT"
            prev_value = value
            best_end = j
        else:
            decision = "STOP"

        details.append({
            "coverage": f"{start+1}-{j+1}", "holding": round(hc, 2),
            "total": round(total, 2), "luc": round(value, 4), "decision": decision
        })

        if decision == "STOP":
            break

    qty = sum(nr[start:best_end + 1])
    return best_end, qty, details


def run_mrp(method_name, heuristic, gross_requirement, initial_inventory=0, scheduled_receipts=None):
    if scheduled_receipts is None:
        scheduled_receipts = {}

    sr = [0] * PERIODS
    for k, v in scheduled_receipts.items():
        sr[k - 1] = v

    ohi = [0] * PERIODS
    nr = [0] * PERIODS
    porec = [0] * PERIODS
    porel = [0] * PERIODS
    lot_tables = []

    previous_ohi = initial_inventory
    t = 0

    while t < PERIODS:
        available = previous_ohi + sr[t]

        if available >= gross_requirement[t]:
            nr[t] = 0
            ohi[t] = available - gross_requirement[t]
            previous_ohi = ohi[t]
            t += 1
            continue

        nr[t] = gross_requirement[t] - available

        future_nr = [0] * PERIODS
        temp_inventory = previous_ohi

        for x in range(t, PERIODS):
            available_future = temp_inventory + sr[x]
            if available_future >= gross_requirement[x]:
                future_nr[x] = 0
                temp_inventory = available_future - gross_requirement[x]
            else:
                future_nr[x] = gross_requirement[x] - available_future
                temp_inventory = 0

        end_period, qty, details = heuristic(future_nr, t)

        porec[t] = qty
        release_period = t - LEAD_TIME
        if release_period >= 0:
            porel[release_period] = qty

        available += qty
        ohi[t] = available - gross_requirement[t]
        if ohi[t] < 0:
            ohi[t] = 0
        previous_ohi = ohi[t]

        for k in range(t + 1, end_period + 1):
            previous_ohi = previous_ohi - gross_requirement[k] + sr[k]
            if previous_ohi < 0:
                previous_ohi = 0
            ohi[k] = previous_ohi

        lot_tables.append({"start": t + 1, "end": end_period + 1, "qty": qty, "details": details})
        t = end_period + 1

    total_setup = sum(1 for x in porec if x > 0) * SETUP_COST
    total_holding = sum(ohi) * HOLDING_COST
    total_cost = total_setup + total_holding

    return {
        "method": method_name, "GR": gross_requirement, "SR": sr, "OHI": ohi, "NR": nr,
        "PORec": porec, "PORel": porel, "lot_tables": lot_tables,
        "setup_cost": total_setup, "holding_cost": total_holding, "total_cost": total_cost
    }


def compute_all(npm: str):
    if len(npm) != 8 or not npm.isdigit():
        raise ValueError("NPM harus 8 digit angka")

    digits = [int(x) for x in npm]

    GR = [generate_requirement(digits, a, b) for a, b in pairs]

    mcp_sr = {4: digits[4] * 10, 8: digits[5] * 10}
    ppb_initial = generate_requirement(digits, 4, 7)
    ltc_initial = generate_requirement(digits, 1, 7)
    luc_initial = generate_requirement(digits, 3, 4)
    luc_sr = {2: digits[5] * 10}

    mcp = run_mrp("MCP - Minimum Cost per Period", heuristic_mcp, GR, 0, mcp_sr)
    ppb = run_mrp("PPB - Part-Period Balancing", heuristic_ppb, GR, ppb_initial, {})
    ltc = run_mrp("LTC - Least Total Cost", heuristic_ltc, GR, ltc_initial, {})
    luc = run_mrp("LUC - Least Unit Cost", heuristic_luc, GR, luc_initial, luc_sr)

    return {"GR": GR, "results": [mcp, ppb, ltc, luc]}


# =========================================================
# RENDER KE DOM (dipanggil dari tombol di index.html)
# =========================================================

DETAIL_LABELS = {
    "holding": "Holding Cost",
    "total": "Total Cost",
    "mcp": "Nilai MCP",
    "part_period": "Part-Period",
    "EPP": "EPP (batas)",
    "holding_cost": "Holding Cost",
    "setup_cost": "Setup Cost",
    "difference": "Selisih |Setup-Holding|",
    "luc": "Nilai LUC",
}


def render_table(result):
    rows = [
        ("GR", result["GR"]), ("SR", result["SR"]), ("OHI", result["OHI"]),
        ("NR", result["NR"]), ("PORec", result["PORec"]), ("PORel", result["PORel"]),
    ]

    head = "".join(f"<th>{i}</th>" for i in range(1, PERIODS + 1))
    body = ""
    for name, data in rows:
        cells = "".join(f"<td>{round(v, 2)}</td>" for v in data)
        body += f"<tr><th class='row-label'>{name}</th>{cells}</tr>"

    lots_html = ""
    for lot in result["lot_tables"]:
        sample = lot["details"][0]
        value_keys = [k for k in sample.keys() if k not in ("coverage", "decision")]

        header_cells = "<th>Coverage</th>" + "".join(
            f"<th>{DETAIL_LABELS.get(k, k)}</th>" for k in value_keys
        ) + "<th>Keputusan</th>"

        detail_rows = ""
        for d in lot["details"]:
            value_cells = "".join(f"<td>{d[k]}</td>" for k in value_keys)
            deco = "decision-go" if d["decision"] == "LANJUT" else "decision-stop"
            detail_rows += (
                f"<tr><td class='coverage-cell'>{d['coverage']}</td>{value_cells}"
                f"<td class='{deco}'>{d['decision']}</td></tr>"
            )

        lots_html += f"""
        <div class="lot-block">
          <p class="lot-title">Order Periode {lot['start']}–{lot['end']} &middot; Qty {lot['qty']}</p>
          <div class="table-scroll">
            <table class="lot-detail">
              <thead><tr>{header_cells}</tr></thead>
              <tbody>{detail_rows}</tbody>
            </table>
          </div>
        </div>"""

    return f"""
    <section class="method-card">
      <div class="method-header">
        <h3>{result['method']}</h3>
        <div class="cost-pills">
          <span class="pill">Setup {result['setup_cost']:.0f}</span>
          <span class="pill">Holding {result['holding_cost']:.0f}</span>
          <span class="pill total">Total {result['total_cost']:.0f}</span>
        </div>
      </div>
      <div class="table-scroll">
        <table class="mrp-table">
          <thead><tr><th class="row-label">Periode</th>{head}</tr></thead>
          <tbody>{body}</tbody>
        </table>
      </div>
      <details>
        <summary>Detail lot sizing</summary>
        {lots_html}
      </details>
    </section>
    """


def on_submit(event=None):
    npm_input = document.querySelector("#npm-input")
    error_box = document.querySelector("#error-box")
    output = document.querySelector("#output")

    npm = npm_input.value.strip()
    error_box.innerText = ""
    output.innerHTML = ""

    try:
        data = compute_all(npm)
    except ValueError as e:
        error_box.innerText = str(e)
        return

    gr_html = "<p class='gr-line'><strong>Gross Requirement:</strong> " + ", ".join(str(g) for g in data["GR"]) + "</p>"
    output.innerHTML = gr_html + "".join(render_table(r) for r in data["results"])