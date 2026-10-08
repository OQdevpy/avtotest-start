"""Perspektivali yo'l sahnasi: qora avtomobil oq avtomobil oldiga keskin qayta tizilmoqda."""
import sys

W, H = 820, 540
VPX, VPY = 470.0, -330.0          # yo'qolish nuqtasi
L0, R0 = 40.0, 850.0             # yo'l chetlari pastda (y=H)

def k(y):                          # perspektiva koeffitsienti (pastda 1)
    return (y - VPY) / (H - VPY)

def edge(x0, y):
    return VPX + (x0 - VPX) * k(y)

def lane_x(t, y):                  # t: 0 = chap chet, 1 = o'ng chet
    l, r = edge(L0, y), edge(R0, y)
    return l + (r - l) * t

out = []
add = out.append
add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" '
    'aria-label="Qora avtomobil oq avtomobil oldiga keskin qayta tizilmoqda">')
add('''<defs>
  <linearGradient id="asph" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#6b7280"/><stop offset="1" stop-color="#4b5563"/></linearGradient>
  <linearGradient id="grass" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#5f9a3b"/><stop offset="1" stop-color="#3f7a2a"/></linearGradient>
  <linearGradient id="whiteBody" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#d7dde5"/></linearGradient>
  <linearGradient id="blackBody" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#2b3340"/><stop offset="1" stop-color="#0a0d12"/></linearGradient>
  <linearGradient id="greenBody" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#2f8f57"/><stop offset="1" stop-color="#14532d"/></linearGradient>
  <linearGradient id="glass" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#1f2937"/><stop offset="1" stop-color="#4b5563"/></linearGradient>
  <radialGradient id="redGlow"><stop offset="0" stop-color="#ff2a2a" stop-opacity="0.9"/>
    <stop offset="1" stop-color="#ff2a2a" stop-opacity="0"/></radialGradient>
  <radialGradient id="ambGlow"><stop offset="0" stop-color="#ffb020" stop-opacity="0.95"/>
    <stop offset="1" stop-color="#ffb020" stop-opacity="0"/></radialGradient>
  <filter id="soft"><feGaussianBlur stdDeviation="6"/></filter>
</defs>''')

# Fon: o't
add(f'<rect width="{W}" height="{H}" fill="url(#grass)"/>')

# Yo'l
add(f'<polygon points="{edge(L0,0):.1f},0 {edge(R0,0):.1f},0 {R0},{H} {L0},{H}" fill="url(#asph)"/>')

# Chap chetdagi asfalt (to'siq ortida yo'l davomi) — skrinshotdagi kabi kengroq yo'l
add(f'<polygon points="0,0 {edge(L0-30,0):.1f},0 {L0-30},{H} 0,{H}" fill="#5b636f"/>')

# Tasma chiziqlari (uzuq)
def dashes(t):
    y = H
    seg = []
    while y > 0:
        dl = 46 * k(y)          # chiziq uzunligi
        gap = 40 * k(y)
        y2 = max(0, y - dl)
        x1, x2 = lane_x(t, y), lane_x(t, y2)
        w = max(1.2, 7 * k(y))
        seg.append(f'<line x1="{x1:.1f}" y1="{y:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                   f'stroke="#f1f5f9" stroke-width="{w:.1f}" stroke-linecap="round"/>')
        y = y2 - gap
    return "".join(seg)
add(dashes(1/3)); add(dashes(2/3))

# Chetki sidirg'a chiziqlar
for t in (0.015, 0.985):
    add(f'<line x1="{lane_x(t,H):.1f}" y1="{H}" x2="{lane_x(t,0):.1f}" y2="0" stroke="#f8fafc" stroke-width="5"/>')

# To'siqlar: oq-qora bloklar (chap va o'ng)
def barrier(side):
    x0 = L0 - 12 if side == "L" else R0 + 12
    parts = []
    y, i = H + 10, 0
    while y > -10:
        h = 30 * k(y)
        y2 = y - h
        xa, xb = edge(x0, y), edge(x0, y2)
        hh = 46 * k(y)          # to'siq balandligi
        th = 20 * k(y)          # qalinligi
        col = "#f8fafc" if i % 2 == 0 else "#111827"
        hb = 46 * k(y2)
        sx = -1 if side == "L" else 1
        pts = (f"{xa:.1f},{y:.1f} {xb:.1f},{y2:.1f} "
               f"{xb+sx*0.55*hb:.1f},{y2-0.75*hb:.1f} {xa+sx*0.55*hh:.1f},{y-0.75*hh:.1f}")
        parts.append(f'<polygon points="{pts}" fill="{col}" stroke="#9ca3af" stroke-width="0.6"/>')
        y, i = y2, i + 1
    return "".join(parts)
add(barrier("L")); add(barrier("R"))

# O'ng tomondagi panjara (simli to'siq) va ustunlar
for yy in range(H, -40, -38):
    x = edge(R0 + 70, yy)
    add(f'<line x1="{x:.1f}" y1="{yy:.1f}" x2="{x:.1f}" y2="{yy-70*k(yy):.1f}" stroke="#374151" stroke-width="{max(1,3*k(yy)):.1f}"/>')
add(f'<line x1="{edge(R0+70,H):.1f}" y1="{H-60}" x2="{edge(R0+70,0):.1f}" y2="{-60*k(0):.1f}" stroke="#374151" stroke-width="2" opacity="0.7"/>')

def car(cx, by, s, body, rot=0, brake=False, left_signal=False):
    """Sedan, orqa-yuqoridan ko'rinish. cx — markaz, by — bamper pasti, s — masshtab."""
    w = 150 * s
    def P(*pts):
        return " ".join(pts)
    X = lambda f: f"{cx + f*w:.1f}"
    Y = lambda d: f"{by - d*s:.1f}"
    g = [f'<g transform="rotate({rot} {cx:.1f} {by - 70*s:.1f})">']
    g.append(f'<ellipse cx="{cx:.1f}" cy="{by+3*s:.1f}" rx="{w*0.64:.1f}" ry="{13*s:.1f}" fill="#000" opacity="0.4" filter="url(#soft)"/>')
    for dx in (-0.42, 0.42):
        g.append(f'<rect x="{cx+dx*w-w*0.075:.1f}" y="{by-24*s:.1f}" width="{w*0.15:.1f}" height="{26*s:.1f}" rx="{6*s:.1f}" fill="#0a0a0a"/>')
    # pastki kuzov
    g.append(f'<path d="M{X(-0.5)},{Y(12)} Q{X(-0.52)},{Y(46)} {X(-0.43)},{Y(58)} Q{cx:.1f},{Y(63)} {X(0.43)},{Y(58)} '
             f'Q{X(0.52)},{Y(46)} {X(0.5)},{Y(12)} Q{cx:.1f},{Y(-3)} {X(-0.5)},{Y(12)} Z" fill="url(#{body})"/>')
    # bagaj
    g.append(f'<path d="M{X(-0.43)},{Y(58)} L{X(-0.38)},{Y(79)} Q{cx:.1f},{Y(83)} {X(0.38)},{Y(79)} L{X(0.43)},{Y(58)} '
             f'Q{cx:.1f},{Y(63)} {X(-0.43)},{Y(58)} Z" fill="url(#{body})"/>')
    g.append(f'<path d="M{X(-0.42)},{Y(60)} Q{cx:.1f},{Y(65)} {X(0.42)},{Y(60)}" stroke="#000" stroke-opacity="0.25" stroke-width="{1.5*s:.1f}" fill="none"/>')
    # orqa oyna
    g.append(f'<path d="M{X(-0.36)},{Y(81)} L{X(-0.28)},{Y(106)} Q{cx:.1f},{Y(110)} {X(0.28)},{Y(106)} L{X(0.36)},{Y(81)} '
             f'Q{cx:.1f},{Y(85)} {X(-0.36)},{Y(81)} Z" fill="url(#glass)"/>')
    g.append(f'<path d="M{X(-0.22)},{Y(103)} L{X(-0.05)},{Y(86)}" stroke="#fff" stroke-opacity="0.18" stroke-width="{4*s:.1f}"/>')
    # tom
    g.append(f'<path d="M{X(-0.28)},{Y(107)} L{X(-0.26)},{Y(139)} Q{cx:.1f},{Y(145)} {X(0.26)},{Y(139)} L{X(0.28)},{Y(107)} '
             f'Q{cx:.1f},{Y(111)} {X(-0.28)},{Y(107)} Z" fill="url(#{body})"/>')
    g.append(f'<path d="M{X(-0.2)},{Y(135)} Q{cx:.1f},{Y(140)} {X(0.2)},{Y(135)}" stroke="#fff" stroke-opacity="0.22" stroke-width="{3*s:.1f}" fill="none"/>')
    # oldingi oyna uchi
    g.append(f'<path d="M{X(-0.25)},{Y(140)} L{X(-0.21)},{Y(153)} Q{cx:.1f},{Y(157)} {X(0.21)},{Y(153)} L{X(0.25)},{Y(140)} '
             f'Q{cx:.1f},{Y(145)} {X(-0.25)},{Y(140)} Z" fill="url(#glass)" opacity="0.9"/>')
    # ko'zgular
    for dx in (-1, 1):
        g.append(f'<ellipse cx="{cx+dx*w*0.36:.1f}" cy="{by-112*s:.1f}" rx="{w*0.05:.1f}" ry="{5*s:.1f}" fill="url(#{body})" stroke="#000" stroke-opacity="0.3" stroke-width="0.6"/>')
    # stop-chiroqlar
    for dx in (-1, 1):
        x = cx + dx * w * 0.35
        g.append(f'<path d="M{x-dx*w*0.0:.1f},{by-50*s:.1f} l{dx*w*0.13:.1f},{-2*s:.1f} l0,{11*s:.1f} l{-dx*w*0.13:.1f},{2*s:.1f} Z" fill="{"#ff2a2a" if brake else "#8b1c1c"}"/>')
        if brake:
            g.append(f'<circle cx="{x+dx*w*0.06:.1f}" cy="{by-45*s:.1f}" r="{32*s:.1f}" fill="url(#redGlow)"/>')
    if brake:
        g.append(f'<rect x="{cx-w*0.11:.1f}" y="{by-84*s:.1f}" width="{w*0.22:.1f}" height="{4*s:.1f}" rx="2" fill="#ff2a2a"/>')
    g.append(f'<rect x="{cx-w*0.13:.1f}" y="{by-34*s:.1f}" width="{w*0.26:.1f}" height="{13*s:.1f}" rx="{2*s:.1f}" fill="#f1f5f9" stroke="#64748b" stroke-width="0.8"/>')
    g.append(f'<path d="M{X(-0.47)},{Y(16)} Q{cx:.1f},{Y(4)} {X(0.47)},{Y(16)}" stroke="#000" stroke-opacity="0.3" stroke-width="{3*s:.1f}" fill="none"/>')
    if left_signal:
        x = cx - w * 0.47
        g.append(f'<rect x="{x:.1f}" y="{by-51*s:.1f}" width="{w*0.06:.1f}" height="{11*s:.1f}" rx="2" fill="#ffb020"/>')
        g.append(f'<circle cx="{x+w*0.03:.1f}" cy="{by-46*s:.1f}" r="{28*s:.1f}" fill="url(#ambGlow)"/>')
    g.append('</g>')
    return "".join(g)

# Uzoqdagi yashil avtomobil (o'ng tasma)
yg = 70
add(car(lane_x(0.83, yg), yg, k(yg) * 0.95, "greenBody"))
# Qora avtomobil: o'ng tasmadan o'rta tasmaga keskin kirib kelmoqda
yb = 300
add(car(lane_x(0.62, yb), yb, k(yb) * 0.95, "blackBody", rot=-10, left_signal=True))
# Oq avtomobil: o'rta tasma, tormozlamoqda
yw = 505
add(car(lane_x(0.5, yw), yw, k(yw) * 0.95, "whiteBody", brake=True))

# Kichik brend belgisi
add(f'<text x="{W-14}" y="{H-14}" text-anchor="end" font-family="Lato, Arial, sans-serif" font-weight="800" font-size="15" fill="#ffffff" opacity="0.75">pravaexpress<tspan fill="#ef4444">.uz</tspan></text>')
add('</svg>')
open(sys.argv[1], "w").write("\n".join(out))
