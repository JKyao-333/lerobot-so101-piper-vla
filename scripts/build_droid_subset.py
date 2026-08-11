#!/usr/bin/env python3
"""Build a selective raw DROID subset from GCS.

The full raw DROID bucket is too large for typical training machines. This
script samples episode directories from the official GCS bucket and downloads
only after an explicit ``--execute-download`` opt-in. It selects:

  - trajectory.h5
  - top-level metadata *.json
  - recordings/MP4/*.mp4, excluding *-stereo.mp4

It preserves the official directory layout under the chosen output root.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import os
import random
import shutil
import subprocess
import sys
from pathlib import Path

DEFAULT_GCS_ROOT = "gs://gresearch/robotics/droid_raw/1.0.1"
WINDOWS_INVALID_FILENAME_CHARS = '<>:"\\|?*'


def run(cmd: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, capture_output=True, check=check)


def gsutil_ls(uri: str) -> list[str]:
    proc = run(["gsutil", "ls", uri], check=False)
    if proc.returncode != 0:
        return []
    return [x.strip() for x in proc.stdout.splitlines() if x.strip()]


def gsutil_cp(src: str, dst: Path, *, no_clobber: bool = True) -> bool:
    dst.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["gsutil", "cp"]
    if no_clobber:
        cmd.append("-n")
    cmd += [src, str(dst)]
    proc = run(cmd, check=False)
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr)
        return False
    return True


def normalize_gcs_dir(uri: str) -> str:
    return uri.rstrip("/")


def episode_relpath(gcs_episode: str, gcs_root: str) -> str:
    root = normalize_gcs_dir(gcs_root)
    ep = normalize_gcs_dir(gcs_episode)
    if not ep.startswith(root + "/"):
        raise ValueError(f"{ep} is not under {root}")
    return ep[len(root) + 1 :]


def remote_basename(uri: str) -> str:
    return uri.rstrip("/").rsplit("/", 1)[-1]


def safe_local_name(name: str) -> str:
    if os.name != "nt":
        return name
    return "".join(
        "_" if ch in WINDOWS_INVALID_FILENAME_CHARS or ord(ch) < 32 else ch for ch in name
    ).rstrip(" .")


def local_episode_path(output_root: Path, rel: str) -> Path:
    parts = [safe_local_name(part) for part in rel.split("/")]
    return output_root / "1.0.1" / Path(*parts)


def read_existing(existing_files: list[str], gcs_root: str) -> set[str]:
    existing: set[str] = set()
    for fname in existing_files:
        if not fname:
            continue
        path = Path(fname)
        if not path.exists():
            continue
        for line in path.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            if line.startswith("gs://"):
                try:
                    existing.add(episode_relpath(line, gcs_root))
                except ValueError:
                    continue
            else:
                marker = "/1.0.1/"
                if marker in line:
                    existing.add(line.split(marker, 1)[1].strip("/"))
    return existing


def dir_size_bytes(path: Path) -> int:
    total = 0
    if not path.exists():
        return 0
    for root, _, files in os.walk(path):
        for name in files:
            try:
                total += (Path(root) / name).stat().st_size
            except OSError:
                pass
    return total


def list_episode_dirs(
    gcs_root: str,
    *,
    labs: list[str],
    statuses: list[str],
    max_dates_per_status: int | None,
    max_episodes_per_date: int | None,
) -> list[str]:
    """Hierarchically list episode dirs without recursively listing the bucket."""
    lab_dirs = [x for x in gsutil_ls(gcs_root.rstrip("/") + "/") if x.endswith("/")]
    lab_dirs = [x for x in lab_dirs if x.rstrip("/").split("/")[-1] not in {"aggregated"}]
    if labs:
        wanted = set(labs)
        lab_dirs = [x for x in lab_dirs if x.rstrip("/").split("/")[-1] in wanted]
    episodes: list[str] = []
    for lab in lab_dirs:
        print(f"LIST lab {lab}", flush=True)
        status_dirs = [x for x in gsutil_ls(lab) if x.endswith("/")]
        if statuses:
            status_dirs = [x for x in status_dirs if x.rstrip("/").split("/")[-1] in statuses]
        for status_dir in status_dirs:
            print(f"  LIST status {status_dir}", flush=True)
            dates = [x for x in gsutil_ls(status_dir) if x.endswith("/")]
            if max_dates_per_status is not None:
                dates = dates[:max_dates_per_status]
            for date_dir in dates:
                eps = [normalize_gcs_dir(x) for x in gsutil_ls(date_dir) if x.endswith("/")]
                if max_episodes_per_date is not None:
                    eps = eps[:max_episodes_per_date]
                episodes.extend(eps)
                print(f"    {date_dir} -> {len(eps)} episodes", flush=True)
    return episodes


def remote_episode_files(gcs_episode: str) -> tuple[list[str], list[str], list[str]]:
    top = gsutil_ls(gcs_episode.rstrip("/") + "/")
    h5 = [x for x in top if x.endswith("/trajectory.h5")]
    jsons = [x for x in top if x.endswith(".json")]
    mp4s = [
        x
        for x in gsutil_ls(gcs_episode.rstrip("/") + "/recordings/MP4/*.mp4")
        if x.endswith(".mp4") and not x.endswith("-stereo.mp4")
    ]
    return h5, jsons, mp4s


def download_episode(
    gcs_episode: str, output_root: Path, gcs_root: str, *, no_clobber: bool
) -> bool:
    rel = episode_relpath(gcs_episode, gcs_root)
    local_episode = local_episode_path(output_root, rel)
    h5s, jsons, mp4s = remote_episode_files(gcs_episode)
    if not h5s or not jsons or len(mp4s) < 2:
        print(
            f"SKIP missing required files: {gcs_episode} "
            f"h5={len(h5s)} json={len(jsons)} mp4={len(mp4s)}",
            flush=True,
        )
        return False
    ok = True
    for src in h5s + jsons:
        ok = (
            gsutil_cp(
                src, local_episode / safe_local_name(remote_basename(src)), no_clobber=no_clobber
            )
            and ok
        )
    for src in mp4s:
        ok = (
            gsutil_cp(
                src,
                local_episode / "recordings" / "MP4" / safe_local_name(remote_basename(src)),
                no_clobber=no_clobber,
            )
            and ok
        )
    print(f"{'DOWNLOADED' if ok else 'PARTIAL'} {gcs_episode} -> {local_episode}", flush=True)
    return ok


def write_list(path: str | None, rows: list[str]) -> None:
    if not path:
        return
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(rows) + ("\n" if rows else ""))


def enough_space(output_root: Path, max_bytes: int, max_gb: float) -> bool:
    used = dir_size_bytes(output_root)
    free = shutil.disk_usage(output_root).free
    if used >= max_bytes:
        print(
            f"STOP output root reached max-gb: {used / (1024**3):.2f} >= {max_gb:.2f}", flush=True
        )
        return False
    if free < 20 * (1024**3):
        print(f"STOP low free space: {free / (1024**3):.2f}GB", flush=True)
        return False
    return True


def download_episodes_parallel(
    episodes: list[str],
    *,
    output_root: Path,
    gcs_root: str,
    target_episodes: int,
    max_bytes: int,
    max_gb: float,
    workers: int,
    no_clobber: bool,
    downloaded_list_output: str | None,
) -> list[str]:
    """Download episodes concurrently, bounded by `workers`.

    We submit only a small rolling window of futures so `target_episodes` and
    disk limits remain reasonably tight. Already-present files are skipped by
    `gsutil cp -n`, so interrupted runs can be resumed safely.
    """
    downloaded: list[str] = []
    next_idx = 0
    futures: dict[concurrent.futures.Future[bool], str] = {}

    def submit_one(executor: concurrent.futures.ThreadPoolExecutor) -> bool:
        nonlocal next_idx
        if next_idx >= len(episodes) or len(downloaded) + len(futures) >= target_episodes:
            return False
        if not enough_space(output_root, max_bytes, max_gb):
            return False
        ep = episodes[next_idx]
        next_idx += 1
        fut = executor.submit(download_episode, ep, output_root, gcs_root, no_clobber=no_clobber)
        futures[fut] = ep
        return True

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        for _ in range(workers):
            if not submit_one(executor):
                break
        while futures and len(downloaded) < target_episodes:
            done, _ = concurrent.futures.wait(
                futures, return_when=concurrent.futures.FIRST_COMPLETED
            )
            for fut in done:
                ep = futures.pop(fut)
                try:
                    ok = fut.result()
                except Exception as e:  # noqa: BLE001
                    print(f"ERROR {ep}: {e}", flush=True)
                    ok = False
                if ok:
                    downloaded.append(ep)
                    write_list(downloaded_list_output, downloaded)
                    print(f"PROGRESS downloaded={len(downloaded)}/{target_episodes}", flush=True)
                while len(futures) < workers and len(downloaded) + len(futures) < target_episodes:
                    if not submit_one(executor):
                        break
    return downloaded


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gcs-root", default=DEFAULT_GCS_ROOT)
    parser.add_argument("--output-root", default="data/droid_raw_subset")
    parser.add_argument("--target-episodes", type=int, default=10)
    parser.add_argument("--max-gb", type=float, default=50.0)
    parser.add_argument("--seed", type=int, default=239)
    parser.add_argument("--labs", nargs="*", default=[])
    parser.add_argument("--statuses", nargs="*", default=["success", "failure"])
    parser.add_argument("--max-dates-per-status", type=int, default=None)
    parser.add_argument("--max-episodes-per-date", type=int, default=None)
    parser.add_argument("--existing-list", action="append", default=[])
    parser.add_argument("--episode-list-input", default=None)
    parser.add_argument("--episode-list-output", default=None)
    parser.add_argument("--downloaded-list-output", default=None)
    parser.add_argument("--list-only", action="store_true")
    parser.add_argument(
        "--execute-download",
        action="store_true",
        help="explicitly allow data download and local writes",
    )
    parser.add_argument("--no-clobber", action="store_true", default=True)
    parser.add_argument(
        "--workers", type=int, default=1, help="number of episodes to download concurrently"
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    gcs_root = normalize_gcs_dir(args.gcs_root)
    output_root = Path(args.output_root)

    existing = read_existing(args.existing_list, gcs_root)
    print(f"existing episodes to exclude: {len(existing)}", flush=True)
    if args.episode_list_input:
        print(f"reading remote episode dirs from {args.episode_list_input}", flush=True)
        episodes = [
            normalize_gcs_dir(x)
            for x in Path(args.episode_list_input).read_text().splitlines()
            if x.strip()
        ]
    else:
        print("listing remote episode dirs...", flush=True)
        episodes = list_episode_dirs(
            gcs_root,
            labs=args.labs,
            statuses=args.statuses,
            max_dates_per_status=args.max_dates_per_status,
            max_episodes_per_date=args.max_episodes_per_date,
        )
    before = len(episodes)
    episodes = [ep for ep in episodes if episode_relpath(ep, gcs_root) not in existing]
    rng = random.Random(args.seed)
    rng.shuffle(episodes)
    print(f"remote episodes: {before}, after exclude: {len(episodes)}", flush=True)

    write_list(args.episode_list_output, episodes)

    if args.list_only or not args.execute_download:
        for ep in episodes[: args.target_episodes]:
            print(ep)
        if not args.execute_download:
            print("preview only: pass --execute-download to download data", flush=True)
        return 0

    output_root.mkdir(parents=True, exist_ok=True)
    max_bytes = int(args.max_gb * (1024**3))
    if args.workers <= 1:
        downloaded: list[str] = []
        for ep in episodes:
            if len(downloaded) >= args.target_episodes:
                break
            if not enough_space(output_root, max_bytes, args.max_gb):
                break
            if download_episode(ep, output_root, gcs_root, no_clobber=args.no_clobber):
                downloaded.append(ep)
                write_list(args.downloaded_list_output, downloaded)
                print(f"PROGRESS downloaded={len(downloaded)}/{args.target_episodes}", flush=True)
    else:
        downloaded = download_episodes_parallel(
            episodes,
            output_root=output_root,
            gcs_root=gcs_root,
            target_episodes=args.target_episodes,
            max_bytes=max_bytes,
            max_gb=args.max_gb,
            workers=args.workers,
            no_clobber=args.no_clobber,
            downloaded_list_output=args.downloaded_list_output,
        )

    write_list(args.downloaded_list_output, downloaded)
    print(f"downloaded episodes: {len(downloaded)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
