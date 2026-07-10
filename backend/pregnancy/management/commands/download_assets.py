"""Download static assets used by the Ifishi PDF (run once after setup):

    python manage.py download_assets
"""
from pathlib import Path

import requests
from django.conf import settings
from django.core.management.base import BaseCommand

SVG_URL = (
    "https://upload.wikimedia.org/wikipedia/commons/1/17/"
    "Coat_of_arms_of_Rwanda.svg"
)
# Wikimedia's own PNG rendering, used when the cairo native library is not
# available (common on Windows dev machines).
PNG_FALLBACK_URL = (
    "https://upload.wikimedia.org/wikipedia/commons/thumb/1/17/"
    "Coat_of_arms_of_Rwanda.svg/120px-Coat_of_arms_of_Rwanda.svg.png"
)
HEADERS = {"User-Agent": "kibasumba-mvp/0.1 (dev asset fetch)"}


class Command(BaseCommand):
    help = "Download the Rwanda coat of arms PNG used by the Ifishi PDF."

    def handle(self, *args, **options):
        static_dir = Path(settings.BASE_DIR) / "static"
        png_path = static_dir / "coat_of_arms.png"

        if png_path.exists():
            self.stdout.write(f"{png_path} already exists — skipping download.")
            return

        static_dir.mkdir(exist_ok=True)
        svg = requests.get(SVG_URL, headers=HEADERS, timeout=30)
        svg.raise_for_status()

        try:
            import cairosvg

            cairosvg.svg2png(
                bytestring=svg.content,
                write_to=str(png_path),
                output_width=120,
                output_height=131,
            )
        except (ImportError, OSError) as e:
            self.stderr.write(
                f"cairosvg unavailable ({e}); falling back to Wikimedia's "
                f"PNG rendering."
            )
            png = requests.get(PNG_FALLBACK_URL, headers=HEADERS, timeout=30)
            png.raise_for_status()
            png_path.write_bytes(png.content)

        self.stdout.write(self.style.SUCCESS(f"Saved {png_path}"))
