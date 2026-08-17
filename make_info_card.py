from pathlib import Path

OUT_PATH = Path(__file__).resolve().parent.parent / "info-card.svg"
TITLE = "spectra@github"
ENTRIES = [
    ("Now", "Mechanical Eng (Yr 2) -> Software / AI Eng"),
    ("Prev", "CAD + FEA portfolio: EV pack, F1 wishbone, robotic arm"),
    ("Stack", "Python, TypeScript, Next.js, Node.js, SQLite, Ollama"),
    ("Building", "Agent-O7 (agentic OS) + RecruitIQ (ATS platform)"),
    ("Goal", "MS in Germany -- TU Munich / RWTH Aachen / KIT"),
]


def main():
    width, row_h, top, left = 490, 26, 46, 18
    height = top + len(ENTRIES) * row_h + 18
    rows = []
    for i, (key, value) in enumerate(ENTRIES):
        y = top + i * row_h
        rows.append(f'<text x="{left}" y="{y}" font-family="Consolas, \'Courier New\', monospace" font-size="13"><tspan fill="#39d353">{key}</tspan><tspan fill="#c9d1d9">  {value}</tspan></text>')
    svg = f'''<svg viewBox="0 0 {width} {height}" width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <rect x="0.5" y="0.5" width="{width-1}" height="{height-1}" rx="8" fill="#0d1117" stroke="#30363d"/>
  <rect x="0.5" y="0.5" width="{width-1}" height="28" rx="8" fill="#161b22"/>
  <rect x="0.5" y="20.5" width="{width-1}" height="8" fill="#161b22"/>
  <circle cx="16" cy="14" r="5" fill="#ff5f56"/><circle cx="32" cy="14" r="5" fill="#ffbd2e"/><circle cx="48" cy="14" r="5" fill="#27c93f"/>
  <text x="{width/2}" y="18" text-anchor="middle" fill="#8b949e" font-family="Consolas, 'Courier New', monospace" font-size="12">{TITLE}</text>
  {''.join(rows)}
</svg>'''
    OUT_PATH.write_text(svg, encoding="utf-8")
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
