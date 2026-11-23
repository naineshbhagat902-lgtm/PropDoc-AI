"""Lawful property-tax planning maths for PropDoc AI (India).

All rates are defaults that can be overridden in the UI. They reflect the
rules as understood in late 2026 (Income-tax Act 2025 in force from
1 April 2026; sections were renumbered but the substance of the property
provisions is unchanged). Always confirm with a Chartered Accountant.
"""

LTCG_RATE = 0.125            # long-term gain, no indexation
LTCG_INDEXED_RATE = 0.20     # optional for property bought before 23-Jul-2024
CESS = 0.04
LONG_TERM_MONTHS = 24        # immovable property
CAP_54 = 100_000_000         # Rs 10 crore ceiling on Sec 54 / 54F exemption
CAP_54EC = 5_000_000         # Rs 50 lakh ceiling on 54EC bonds
TDS_RATE = 0.01              # buyer's TDS on property purchase (old Sec 194-IA)
TDS_THRESHOLD = 5_000_000    # Rs 50 lakh


def inr(x: float) -> str:
    """Format a number in the Indian digit-grouping style."""
    x = int(round(x))
    s = str(abs(x))
    if len(s) > 3:
        head, tail = s[:-3], s[-3:]
        parts = []
        while len(head) > 2:
            parts.insert(0, head[-2:])
            head = head[:-2]
        if head:
            parts.insert(0, head)
        s = ",".join(parts + [tail])
    return ("-" if x < 0 else "") + "₹" + s


def words(x: float) -> str:
    """Human friendly: 1.20 crore / 45.00 lakh."""
    x = abs(float(x))
    if x >= 1e7:
        return f"{x / 1e7:.2f} crore"
    if x >= 1e5:
        return f"{x / 1e5:.2f} lakh"
    return inr(x)


def buyer_costs(value, stamp_pct=6.0, reg_pct=1.0, reg_cap=30_000):
    stamp = value * stamp_pct / 100
    reg = min(value * reg_pct / 100, reg_cap)
    tds = value * TDS_RATE if value >= TDS_THRESHOLD else 0.0
    return {
        "stamp": stamp,
        "registration": reg,
        "total_govt": stamp + reg,
        "tds": tds,
        "seller_receives": value - tds,
        "all_in": value + stamp + reg,
    }


def capital_gains(sale, cost, improvement=0.0, expenses=0.0, months=0,
                  indexed_cost=0.0, surcharge_pct=0.0, slab_pct=30.0,
                  house=0.0, bonds=0.0):
    """Capital-gains tax on a residential property sale with Sec 54 / 54EC."""
    is_long = months > LONG_TERM_MONTHS
    net_sale = sale - expenses
    gain = net_sale - cost - improvement
    out = {"is_long": is_long, "gain": gain, "method": "", "rate": 0.0,
           "ex54": 0.0, "ex54ec": 0.0, "taxable": 0.0,
           "tax": 0.0, "surcharge": 0.0, "cess": 0.0, "total": 0.0}
    if gain <= 0:
        out["method"] = "No taxable gain (loss or break-even)"
        return out

    if is_long:
        rate, method, base = LTCG_RATE, "12.5% without indexation", gain
        if indexed_cost > 0:
            g_idx = max(net_sale - indexed_cost, 0.0)
            if g_idx * LTCG_INDEXED_RATE < gain * LTCG_RATE:
                rate, method, base = LTCG_INDEXED_RATE, "20% with indexation", g_idx
        ex54 = min(house, base, CAP_54)
        ex54ec = min(bonds, CAP_54EC, base - ex54)
        out.update(ex54=ex54, ex54ec=ex54ec)
        taxable = base - ex54 - ex54ec
    else:
        rate, method, taxable = slab_pct / 100, "Short-term: taxed at your slab rate", gain

    tax = taxable * rate
    sur = tax * min(surcharge_pct, 15.0 if is_long else 37.0) / 100
    cess = (tax + sur) * CESS
    out.update(method=method, rate=rate, taxable=taxable, tax=tax,
               surcharge=sur, cess=cess, total=tax + sur + cess)
    return out


def scenarios(**kw):
    """Compare reinvestment strategies to find the lowest lawful tax."""
    kw = {k: v for k, v in kw.items() if k not in ("house", "bonds")}
    base = capital_gains(house=0, bonds=0, **kw)
    if not base["is_long"] or base["gain"] <= 0:
        return [{"Strategy": "No reinvestment option (short-term or no gain)",
                 "You invest": 0.0, "Tax payable": base["total"]}]
    g = base["gain"]
    plans = [
        ("1. Pay tax, no reinvestment", 0.0, 0.0),
        ("2. 54EC bonds (up to ₹50 lakh)", 0.0, min(g, CAP_54EC)),
        ("3. Buy new house worth the gain (Sec 54)", g, 0.0),
        ("4. ₹50 lakh bonds + house for the rest", max(g - CAP_54EC, 0.0), min(g, CAP_54EC)),
    ]
    rows = []
    for name, house, bonds in plans:
        r = capital_gains(house=house, bonds=bonds, **kw)
        rows.append({"Strategy": name, "You invest": house + bonds,
                     "Tax payable": r["total"]})
    return rows
