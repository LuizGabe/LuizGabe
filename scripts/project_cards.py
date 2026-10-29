"""Build bilingual, theme-aware project headers from the original vector logos."""

from html import escape
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets" / "projects"
ET.register_namespace("", "http://www.w3.org/2000/svg")

PROJECTS = {
    "nebula": {
        "name": "Nebula",
        "category": ("AUDIO / AI / AUTOMATION", "ÁUDIO / IA / AUTOMAÇÃO"),
        "tagline": ("From recorded audio to useful documents.", "Do áudio gravado a documentos úteis."),
        "light": ("#7350a3", "#f9f7fc", "#e4d9f0", "#ede5f6"),
        "dark": ("#c4a4ed", "#191620", "#393044", "#272031"),
        "glyph": "M0 22v16m12-28v40m12-50v60m12-47v34m12-29v24m12-16v8",
    },
    "aether": {
        "name": "Aether",
        "category": ("FINANCE / DESKTOP / INTEGRATIONS", "FINANÇAS / DESKTOP / INTEGRAÇÕES"),
        "tagline": ("Personal finances, with a local home.", "Finanças pessoais, no seu computador."),
        "light": ("#286950", "#f5f9f6", "#d5e5db", "#e4efe8"),
        "dark": ("#93cbb0", "#141d19", "#2c4236", "#203027"),
        "glyph": "M0 48l14-17 13 7 17-25 16 4m-14-4h14v14",
    },
    "caegs": {
        "name": "CAEGS Shop",
        "category": ("COMMERCE / PIX / OPERATIONS", "COMÉRCIO / PIX / OPERAÇÃO"),
        "tagline": ("Student merchandise, from checkout to pickup.", "Produtos para estudantes, do pagamento à retirada."),
        "light": ("#514aa9", "#f7f7fc", "#dcdcf0", "#e9e9f6"),
        "dark": ("#b7b4f0", "#171723", "#34344d", "#242438"),
        "glyph": "M6 18h48l4 38H2zm12 0V12a12 12 0 0 1 24 0v6",
    },
}


def render(key, project, index, theme, locale):
    pt = locale == "pt-BR"
    accent, surface, border, tile = project[theme]
    ink = "#e6edf3" if theme == "dark" else "#293b34"
    muted = "#b0b7be" if theme == "dark" else "#58675f"
    category = escape(project["category"][pt])
    tagline = escape(project["tagline"][pt])
    name = project["name"]
    icon = ET.parse(ASSETS / f"{key}-icon.svg").getroot()
    # Nest the original vector artwork; preserve gradients and paths without rasterizing.
    icon.set("x", "39")
    icon.set("y", "37")
    icon.set("width", "102")
    icon.set("height", "102")
    icon.set("aria-hidden", "true")
    for child in list(icon):
        if child.tag.rsplit("}", 1)[-1] in ("title", "desc"):
            icon.remove(child)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="176" viewBox="0 0 1000 176" role="img" aria-labelledby="title desc">
  <title id="title">{name}</title>
  <desc id="desc">{tagline}</desc>
  <rect x="1" y="1" width="998" height="174" rx="18" fill="{surface}" stroke="{border}"/>
  <path d="M18 35q-3 51 0 106" fill="none" stroke="{accent}" stroke-width="3" stroke-linecap="round"/>
  <rect x="31" y="29" width="118" height="118" rx="24" fill="{tile}"/>
  <defs><clipPath id="icon-clip"><rect x="39" y="37" width="102" height="102" rx="16"/></clipPath></defs>
  <g clip-path="url(#icon-clip)">{ET.tostring(icon, encoding="unicode")}</g>
  <g font-family="'Segoe UI', Arial, sans-serif">
    <text x="178" y="46" font-family="Consolas, monospace" font-size="13" letter-spacing="1.5" fill="{accent}">{category}</text>
    <text x="176" y="94" font-size="38" font-weight="650" letter-spacing="-1" fill="{ink}">{name}</text>
    <text x="178" y="128" font-size="18" fill="{muted}">{tagline}</text>
    <text x="950" y="42" text-anchor="end" font-family="Consolas, monospace" font-size="13" fill="{accent}">0{index} /</text>
  </g>
  <path d="{project['glyph']}" transform="translate(862 65)" fill="none" stroke="{accent}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" opacity="0.65"/>
  <path d="M853 138q35-4 82 0m-77 4q33-3 68 0" fill="none" stroke="{accent}" stroke-width="1.2" stroke-linecap="round" opacity="0.35"/>
</svg>
'''


def main():
    for index, (key, project) in enumerate(PROJECTS.items(), start=1):
        for theme in ("light", "dark"):
            for locale in ("en", "pt-BR"):
                filename = ASSETS / f"{key}-{theme}-{locale}.svg"
                filename.write_text(render(key, project, index, theme, locale), encoding="utf-8")


if __name__ == "__main__":
    main()
