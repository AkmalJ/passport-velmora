"""Entrypoint: build the Velmora passport spread into the output directory."""
import os

from generate import build


def main() -> None:
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = build(os.path.join(out_dir, "entry.png"))
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
