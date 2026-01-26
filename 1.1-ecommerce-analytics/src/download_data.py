from __future__ import annotations

from pathlib import Path
import urllib.request

UCI_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/00352/Online%20Retail.xlsx"

def project_root() -> Path:
    return Path(__file__).resolve().parents[1]

def download_online_retail(force: bool = False) -> Path:
    root = project_root()
    raw_dir = root / "data" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    out_path = raw_dir / "Online_Retail.xlsx"

    if out_path.exists() and not force:
        print(f"✅ Dataset already exists: {out_path}")
        return out_path

    print(f"⬇️ Downloading dataset to: {out_path}")
    urllib.request.urlretrieve(UCI_URL, out_path)
    print("✅ Download complete")
    return out_path

if __name__ == "__main__":
    download_online_retail()
