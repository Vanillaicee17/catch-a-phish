from __future__ import annotations

import argparse
import shutil
from pathlib import Path

API_PLACEHOLDER = "__API_BASE_URL__"
EXTENSIONS = {
    "chrome": "background.js",
    "firefox": "background.js",
}
EXCLUDED_NAMES = {"catch.zip", "__pycache__", ".DS_Store"}


def copy_extension(source_dir: Path, destination_dir: Path) -> None:
    shutil.copytree(
        source_dir,
        destination_dir,
        ignore=shutil.ignore_patterns(*EXCLUDED_NAMES),
    )


def inject_api_base_url(background_file: Path, api_base_url: str) -> None:
    original = background_file.read_text(encoding="utf-8")
    if API_PLACEHOLDER not in original:
        raise ValueError(f"Missing API placeholder in {background_file}")

    rendered = original.replace(API_PLACEHOLDER, api_base_url.rstrip("/"))
    background_file.write_text(rendered, encoding="utf-8")


def package_extension(name: str, source_dir: Path, output_dir: Path, api_base_url: str) -> None:
    unpacked_dir = output_dir / f"{name}-unpacked"
    if unpacked_dir.exists():
        shutil.rmtree(unpacked_dir)

    copy_extension(source_dir, unpacked_dir)
    inject_api_base_url(unpacked_dir / EXTENSIONS[name], api_base_url)

    archive_path = output_dir / f"catch-a-phish-{name}"
    zip_file = archive_path.with_suffix(".zip")
    if zip_file.exists():
        zip_file.unlink()

    shutil.make_archive(str(archive_path), "zip", root_dir=unpacked_dir)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build Chrome and Firefox extension packages with a concrete API URL."
    )
    parser.add_argument(
        "--api-base-url",
        required=True,
        help="Base URL for the deployed backend, for example https://api.catchaphish.com",
    )
    parser.add_argument(
        "--output-dir",
        default="dist",
        help="Directory where unpacked builds and zip archives will be written.",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    output_dir = (repo_root / args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    for name in EXTENSIONS:
        package_extension(name, repo_root / name, output_dir, args.api_base_url)
        print(f"Built {name} extension in {output_dir}")


if __name__ == "__main__":
    main()
