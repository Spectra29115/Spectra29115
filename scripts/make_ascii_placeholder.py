from pathlib import Path

NAME = "SPECTRA"
TAGLINE = "mechanical eng -> ai / swe"
OUT_PATH = Path(__file__).resolve().parent.parent / "profile-ascii.svg"


def main():
    art = [
        "  ███████╗██████╗ ███████╗ ██████╗████████╗██████╗  █████╗ ",
        "  ██╔════╝██╔══██╗██╔════╝██╔════╝╚══██╔══╝██╔══██╗██╔══██╗",
        "  ███████╗██████╔╝█████╗  ██║        ██║   ██████╔╝███████║",
        "  ╚════██║██╔═══╝ ██╔══╝  ██║        ██║   ██╔══██╗██╔══██║",
        "  ███████║██║     ███████╗╚██████╗   ██║   ██║  ██║██║  ██║",
        "  ╚══════╝╚═╝     ╚══════╝ ╚═════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝",
        "",
        "          mechanical eng -> ai / swe",
    ]
    width = max(map(len, art)) * 6.2
    height = len(art) * 13
    texts = []
    for i, line in enumerate(art):
        escaped = line.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
        texts.append(f'<text x="0" y="{i*13+11}" font-family="Consolas, \'Courier New\', monospace" font-size="11" fill="{"#39d353" if i == 7 else "#c9d1d9"}" xml:space="preserve">{escaped}</text>')
    svg = f'<svg viewBox="0 0 {width:.0f} {height:.0f}" width="{width:.0f}" height="{height:.0f}" xmlns="http://www.w3.org/2000/svg">{"".join(texts)}</svg>'
    OUT_PATH.write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    main()
