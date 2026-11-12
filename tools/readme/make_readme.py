#!/usr/bin/env python3
"""Writes voltzz900's GitHub profile page: README.md (English), README.pt-BR.md (Brazilian Portuguese) and the
pictures they show (.github/readme/*.svg): a banner and one card per mod, drawn here from tools/readme/mods.json.
Each card opens that mod's own repository.

Edit mods.json (a mod's line, its category, its registry status) and run this again.
Usage: python3 tools/readme/make_readme.py
"""
import base64
import json
import random
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[2]
DATA = json.loads((Path(__file__).with_name("mods.json")).read_text())
OUT = ROOT / ".github/readme"
USER = "https://github.com/voltzz900"

SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
STAR_COLOURS = ["#F0B33A", "#E0562A", "#C23CE6", "#4FD8F0"]

WORDS = {
    "en": {"review": "In review", "catalog": "In the catalog", "content": "content mod", "native": "native mod",
           "both": "native + content mod", "by": "by voltzz900"},
    "pt": {"review": "Em revisão", "catalog": "No catálogo", "content": "mod de conteúdo", "native": "mod nativo",
           "both": "mod nativo + conteúdo", "by": "por voltzz900"},
}

# A 5x7 pixel alphabet of our own, for the banner's title.
GLYPHS = {
    "V": ["X...X", "X...X", "X...X", "X...X", ".X.X.", ".X.X.", "..X.."],
    "A": [".XXX.", "X...X", "X...X", "XXXXX", "X...X", "X...X", "X...X"],
    "S": [".XXXX", "X....", "X....", ".XXX.", "....X", "....X", "XXXX."],
    "T": ["XXXXX", "..X..", "..X..", "..X..", "..X..", "..X..", "..X.."],
    "M": ["X...X", "XX.XX", "X.X.X", "X.X.X", "X...X", "X...X", "X...X"],
    "O": [".XXX.", "X...X", "X...X", "X...X", "X...X", "X...X", ".XXX."],
    "D": ["XXXX.", "X...X", "X...X", "X...X", "X...X", "X...X", "XXXX."],
    " ": ["...", "...", "...", "...", "...", "...", "..."],
}


def data_uri(path):
    return "data:image/png;base64," + base64.b64encode((ROOT / path).read_bytes()).decode()


def mix(a, b, t):
    a, b = [int(a[i:i + 2], 16) for i in (1, 3, 5)], [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02X}" for x, y in zip(a, b))


def banner(lang):
    w, h = 1200, 420
    rnd = random.Random(7)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
           '<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">'
           '<stop offset="0" stop-color="#07051A"/><stop offset="0.6" stop-color="#1A1036"/>'
           '<stop offset="1" stop-color="#2B1546"/></linearGradient>'
           '<radialGradient id="glow" cx="0.5" cy="0.42" r="0.5"><stop offset="0" stop-color="#C23CE6" stop-opacity="0.35"/>'
           '<stop offset="1" stop-color="#C23CE6" stop-opacity="0"/></radialGradient></defs>',
           f'<rect width="{w}" height="{h}" rx="18" fill="url(#sky)"/>',
           f'<rect width="{w}" height="{h}" rx="18" fill="url(#glow)"/>']
    # Square pixel stars, some in the Vast metals' colours.
    for _ in range(140):
        x, y = rnd.randrange(8, w - 8), rnd.randrange(8, h - 8)
        s = rnd.choice([2, 2, 2, 3, 4])
        c = rnd.choice(["#FFFFFF", "#FFFFFF", "#D9D2FF"] + STAR_COLOURS)
        out.append(f'<rect x="{x}" y="{y}" width="{s}" height="{s}" fill="{c}" opacity="{rnd.uniform(0.35, 0.95):.2f}"/>')
    # The title in pixel blocks, each column tinted along the star's colours, with a drop shadow.
    title, px = "VAST MODS", 13
    width = sum((len(GLYPHS[ch][0]) + 1) * px for ch in title) - px
    x0, y0 = (w - width) // 2, 70
    for shadow in (True, False):
        x = x0
        for ch in title:
            g = GLYPHS[ch]
            for gy, row in enumerate(g):
                for gx, cell in enumerate(row):
                    if cell != "X":
                        continue
                    t = (x + gx * px - x0) / max(1, width)
                    i = min(2, int(t * 3))
                    col = mix(STAR_COLOURS[i], STAR_COLOURS[i + 1], t * 3 - i)
                    col = mix("#FFFFFF", col, 0.35 + 0.65 * gy / 6)
                    dx, dy = (6, 6) if shadow else (0, 0)
                    fill = "#0B0618" if shadow else col
                    out.append(f'<rect x="{x + gx * px + dx}" y="{y0 + gy * px + dy}" width="{px}" height="{px}" fill="{fill}"/>')
            x += (len(g[0]) + 1) * px
    sub = {"en": "Mods for Horizon, Minecraft: Java Edition 26.3 rewritten in Rust",
           "pt": "Mods para o Horizon, o Minecraft: Java Edition 26.3 reescrito em Rust"}[lang]
    out.append(f'<text x="{w // 2}" y="{y0 + 7 * px + 52}" text-anchor="middle" font-family="{SANS}" font-size="26" '
               f'font-weight="600" fill="#EDE7FF">{escape(sub)}</text>')
    # The family's icons in a row.
    icons = [m for m in DATA["mods"]]
    size, gap = 64, 18
    total = len(icons) * size + (len(icons) - 1) * gap
    x = (w - total) // 2
    for m in icons:
        out.append(f'<rect x="{x - 4}" y="{h - 118}" width="{size + 8}" height="{size + 8}" rx="12" fill="#FFFFFF" fill-opacity="0.08"/>')
        out.append(f'<image x="{x}" y="{h - 114}" width="{size}" height="{size}" href="{data_uri(m["icon"])}" '
                   'style="image-rendering:pixelated"/>')
        x += size + gap
    n = len(DATA["mods"])
    foot = {"en": f"{n} mods · open source · English and Português", "pt": f"{n} mods · código aberto · English e Português"}[lang]
    out.append(f'<text x="{w // 2}" y="{h - 20}" text-anchor="middle" font-family="{SANS}" font-size="17" fill="#A99FC8">{escape(foot)}</text>')
    out.append("</svg>")
    return "\n".join(out)


def wrap(text, limit):
    """One line if it fits, else two of about the same length."""
    if len(text) <= limit:
        return [text]
    words = text.split()
    best = min(range(1, len(words)), key=lambda k: abs(len(" ".join(words[:k])) - len(" ".join(words[k:]))))
    return [" ".join(words[:best]), " ".join(words[best:])]


def card(m, lang):
    w, h = 600, 132
    words = WORDS[lang]
    badge = words[m["status"]]
    bg, fg = ("#F5C451", "#3A2A00") if m["status"] == "review" else ("#7BE0A0", "#073A1B")
    bw = 16 + 8.4 * len(badge)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
           f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="14" fill="#151022" stroke="#33264D" stroke-width="2"/>',
           f'<rect x="20" y="22" width="88" height="88" rx="14" fill="#FFFFFF" fill-opacity="0.06"/>',
           f'<image x="24" y="26" width="80" height="80" href="{data_uri(m["icon"])}" style="image-rendering:pixelated"/>',
           f'<text x="128" y="52" font-family="{SANS}" font-size="23" font-weight="700" fill="#FFFFFF">{escape(m["name"])}</text>',
           f'<rect x="{w - 20 - bw:.0f}" y="26" width="{bw:.0f}" height="26" rx="13" fill="{bg}"/>',
           f'<text x="{w - 20 - bw / 2:.0f}" y="44" text-anchor="middle" font-family="{SANS}" font-size="14" font-weight="700" fill="{fg}">{escape(badge)}</text>']
    for i, line in enumerate(wrap(m[lang], 52)[:2]):
        out.append(f'<text x="128" y="{78 + i * 20}" font-family="{SANS}" font-size="16" fill="#CFC7E6">{escape(line)}</text>')
    meta = f'{words[m["kind"]]} · {words["by"]}'
    out.append(f'<text x="128" y="{h - 14}" font-family="{SANS}" font-size="13" fill="#8C82A8">{escape(meta)}</text>')
    out.append("</svg>")
    return "\n".join(out)


TEXT = {
    "en": {
        "switch": '<b>English</b> · <a href="README.pt-BR.md">Português (Brasil)</a>',
        "intro": "Our own mods for <a href=\"https://github.com/horizon-rust/horizon\">Horizon</a>: ores and metals, "
                 "adventure, end-game crafts and tools for modpack makers. Some are new ideas, some take a Java mod's "
                 "idea and make it our own: new names, new art, built for Horizon.",
        "mods": "Mods", "next": "What's next", "install": "How to install", "build": "Source code",
        "bugs": "Found a bug?", "credits": "Credits",
        "steps": ["Open the **Horizon launcher** and go to **Mods**.",
                  "Find a Vast mod and press **Install**. A native mod also needs **Native build > Build**.",
                  "Start the game. A mod made of two halves (native + content) needs both installed."],
        "native": "Native mods are compiled into the game and are not sandboxed: build only code you trust. Every mod here is open source, and each repository's README says what its native half changes in the game.",
        "build_text": "Each card opens the mod's own repository, with its README, releases, tools and licence (Vast Ores' repository holds Vast Depths too). The content mods are generated by a Python script in their `tools/`; the native mods are bundles for Horizon's native build.",
        "bug_text": "Open an issue in that mod's repository: say what happened and how to make it happen again, and add a screenshot if you can. English or Portuguese.",
        "credit_text": "Made by **voltzz900**, under the MIT licence. Vast Adventures and Vast Spawners are built from the MIT code and data of Shadows_of_Fire's Apotheosis and Apothic Spawners; their repositories keep the notices. Not an official Minecraft product. Not approved by or associated with Mojang or Microsoft.",
    },
    "pt": {
        "switch": '<a href="README.md">English</a> · <b>Português (Brasil)</b>',
        "intro": "Nossos mods para o <a href=\"https://github.com/horizon-rust/horizon\">Horizon</a>: minérios e metais, "
                 "aventura, crafts de fim de jogo e ferramentas para quem monta modpacks. Alguns são ideias novas, outros "
                 "pegam a ideia de um mod do Java e fazem do nosso jeito: nomes novos, arte nova, feitos para o Horizon.",
        "mods": "Mods", "next": "O que vem por aí", "install": "Como instalar", "build": "Código",
        "bugs": "Achou um bug?", "credits": "Créditos",
        "steps": ["Abra o **launcher do Horizon** e vá em **Mods**.",
                  "Ache um mod Vast e clique em **Install**. Mod nativo também precisa de **Native build > Build**.",
                  "Abra o jogo. Mod de duas metades (nativo + conteúdo) precisa das duas instaladas."],
        "native": "Mods nativos são compilados dentro do jogo e não ficam isolados: só compile código em que você confia. Todo mod aqui é código aberto, e o README de cada repositório diz o que a metade nativa muda no jogo.",
        "build_text": "Cada card abre o repositório do mod, com README, releases, ferramentas e licença (o repositório do Vast Ores também tem o Vast Depths). Os mods de conteúdo são gerados por um script Python no seu `tools/`; os nativos são bundles para o native build do Horizon.",
        "bug_text": "Abra uma issue no repositório do mod: diga o que aconteceu e como repetir, e mande um print se puder. Inglês ou português.",
        "credit_text": "Feito por **voltzz900**, sob a licença MIT. Vast Adventures e Vast Spawners são feitos a partir do código e dos dados MIT do Apotheosis e do Apothic Spawners, de Shadows_of_Fire; os repositórios deles guardam os avisos. Não é um produto oficial do Minecraft. Não é aprovado pela Mojang ou pela Microsoft nem associado a elas.",
    },
}


def readme(lang):
    t = TEXT[lang]
    suffix = "" if lang == "en" else "-pt"
    lines = [f'<p align="center">{t["switch"]}</p>', "",
             f'<p align="center"><img src=".github/readme/banner{suffix}.svg" alt="Vast Mods" width="100%"></p>', "",
             f'<p align="center">{t["intro"]}</p>', "", f"## {t['mods']}", ""]
    for cat in DATA["categories"]:
        mods = [m for m in DATA["mods"] if m["category"] == cat["id"]]
        lines += [f"### {cat['emoji']} {cat[lang]}", "", "<p>"]
        for m in mods:
            lines.append(f'<a href="{USER}/{m["repo"]}"><img src=".github/readme/card-{m["id"]}{suffix}.svg" '
                         f'alt="{escape(m["name"])}" width="49%"></a>')
        lines += ["</p>", ""]
    lines += [f"## {t['next']}", ""] + [f"- {item}" for item in DATA["next"][lang]] + [""]
    lines += [f"## {t['install']}", ""] + [f"{i + 1}. {s}" for i, s in enumerate(t["steps"])] + ["", t["native"], ""]
    lines += [f"## {t['build']}", "", t["build_text"], ""]
    lines += [f"## {t['bugs']}", "", t["bug_text"], ""]
    lines += [f"## {t['credits']}", "", t["credit_text"], ""]
    return "\n".join(lines)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for lang, suffix in (("en", ""), ("pt", "-pt")):
        (OUT / f"banner{suffix}.svg").write_text(banner(lang))
        for m in DATA["mods"]:
            (OUT / f"card-{m['id']}{suffix}.svg").write_text(card(m, lang))
    (ROOT / "README.md").write_text(readme("en"))
    (ROOT / "README.pt-BR.md").write_text(readme("pt"))
    print(f"{len(DATA['mods'])} mods, {len(list(OUT.glob('*.svg')))} pictures")


if __name__ == "__main__":
    main()
