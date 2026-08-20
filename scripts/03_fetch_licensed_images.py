"""Download only image URLs whose reusable license is explicit in the manifest."""
from __future__ import annotations
import argparse, hashlib, json, mimetypes, os
from pathlib import Path
from urllib.parse import urlparse
from _fetch import fetch

ALLOWED_LICENSES = {"CC0-1.0", "CC-BY-4.0", "CC-BY-SA-4.0", "PUBLIC-DOMAIN", "OWNER-PERMISSION"}
ALLOWED_HOSTS = {"r2.thesportsdb.com", "upload.wikimedia.org"}

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", type=Path, default=Path("assets/licensed"))
    args = parser.parse_args()
    records = json.loads(args.manifest.read_text(encoding="utf-8"))
    args.output.mkdir(parents=True, exist_ok=True)
    completed = []
    for item in records:
        required = {"asset_id","subject_id","url","source_page","license","credit"}
        if not required.issubset(item): raise ValueError(f"Missing manifest fields: {required-set(item)}")
        if item["license"] not in ALLOWED_LICENSES: raise ValueError(f"Unapproved license: {item['license']}")
        if urlparse(item["url"]).hostname not in ALLOWED_HOSTS: raise ValueError("Image host is not allow-listed")
        result = fetch(item["url"])
        if not result.content_type.lower().startswith("image/"): raise ValueError("URL did not return an image")
        extension = mimetypes.guess_extension(result.content_type.split(";")[0]) or ".img"
        target = args.output / f"{item['asset_id']}{extension}"
        temporary = target.with_suffix(target.suffix + ".tmp")
        temporary.write_bytes(result.body); os.replace(temporary, target)
        completed.append({**item, "local_path":str(target), "sha256":hashlib.sha256(result.body).hexdigest(),
                          "content_type":result.content_type, "fetched_at":result.fetched_at})
    (args.output / "manifest.json").write_text(json.dumps(completed, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"downloaded {len(completed)} licensed images")

if __name__ == "__main__": main()
