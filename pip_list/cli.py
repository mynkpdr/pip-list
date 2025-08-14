"""
pip_list — Lists installed pip packages with their sizes

A fast and human-readable tool to analyze disk space usage of installed Python packages.
"""

import os
import sys
import argparse
import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from importlib.metadata import distributions
except ImportError:
    from importlib_metadata import distributions  # For Python <3.8

def get_folder_size(path):
    """Calculate total size of files inside a folder, recursively.

    Uses os.scandir for speed, skips files that can't be accessed.
    """
    if not path or not os.path.exists(path):
        return 0

    size = 0
    try:
        with os.scandir(path) as it:
            for entry in it:
                try:
                    if entry.is_file(follow_symlinks=False):
                        size += entry.stat().st_size
                    elif entry.is_dir(follow_symlinks=False):
                        size += get_folder_size(entry.path)
                except Exception:
                    # Ignore files/dirs we can't access
                    pass
    except Exception:
        # Permission denied or other OS error
        pass

    return size

def analyze_package(dist):
    """Get package name and size in MB.

    Tries to sum sizes of listed files; if not possible, falls back to scanning package folder.
    """
    try:
        name = dist.metadata.get('Name', 'UNKNOWN')
        size_bytes = 0

        if hasattr(dist, 'files') and dist.files:
            for f in dist.files:
                try:
                    file_path = dist.locate_file(f)
                    if file_path and file_path.exists():
                        size_bytes += file_path.stat().st_size
                except Exception:
                    pass
        else:
            folder = getattr(dist, '_path', None)
            if folder and os.path.exists(folder):
                size_bytes = get_folder_size(folder)

        return (name, size_bytes / (1024 * 1024))
    except Exception:
        # Could not analyze package for some reason
        return None

def get_installed_packages():
    """Return list of (package_name, size_mb) tuples for installed packages.

    Uses ThreadPoolExecutor to speed things up.
    """
    dists = list(distributions())
    print(f"Found {len(dists)} packages installed...")

    packages = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(analyze_package, dist): dist for dist in dists}

        done = 0
        for future in as_completed(futures):
            result = future.result()
            if result:
                packages.append(result)
            done += 1
            if done % 10 == 0 or done == len(dists):
                print(f"\rProcessed {done}/{len(dists)} packages...", end='', flush=True)

    print()  # newline after progress
    return packages

def pretty_size(size_mb):
    """Convert size in MB to human-readable string."""
    if size_mb < 0.001:
        return f"{int(size_mb * 1024 * 1024)} B"
    elif size_mb < 1:
        return f"{size_mb * 1024:.1f} KB"
    elif size_mb >= 1024:
        return f"{size_mb / 1024:.2f} GB"
    else:
        return f"{size_mb:.2f} MB"

def print_packages(packages, sort_by='name', descending=False, filter_str=None, show_total=False):
    """Print a nicely formatted list of packages with sizes.

    Supports sorting and filtering by name substring.
    """
    if filter_str:
        before = len(packages)
        packages = [p for p in packages if filter_str.lower() in p[0].lower()]
        if len(packages) < before:
            print(f"Filtered packages from {before} to {len(packages)} using filter '{filter_str}'")

    if sort_by == 'name':
        packages.sort(key=lambda p: p[0].lower(), reverse=descending)
    elif sort_by == 'size':
        packages.sort(key=lambda p: p[1], reverse=descending)

    if not packages:
        print("No packages to display.")
        return

    sort_arrow = "↓" if descending else "↑"
    print(f"\nPackages (sorted by {sort_by} {sort_arrow}):")
    print("=" * 60)
    print(f"{'Package':40} {'Size':>15}")
    print("-" * 60)

    total_size = 0
    for name, size in packages:
        total_size += size
        print(f"{name:40} {pretty_size(size):>15}")

    if show_total:
        print("=" * 60)
        print(f"{'TOTAL':40} {pretty_size(total_size):>15}")
        print(f"Total packages: {len(packages)}")

    print()

def main():
    # Import version here to avoid circular imports
    try:
        from pip_list import __version__
    except ImportError:
        __version__ = "unknown"
    
    parser = argparse.ArgumentParser(
        description="List installed pip packages and their sizes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pip-list --sort size --desc
  pip-list --filter numpy
  pip-list --top 10
  pip-list --min-size 5
"""
    )
    parser.add_argument('--version', action='version', version=f'pip-list {__version__}')
    parser.add_argument('--sort', choices=['name', 'size'], default='size', help='Sort by name or size')
    parser.add_argument('--desc', action='store_true', help='Sort descending')
    parser.add_argument('--filter', type=str, help='Filter packages by name substring')
    parser.add_argument('--top', type=int, metavar='N', help='Show top N largest packages only')
    parser.add_argument('--min-size', type=float, metavar='MB', help='Show packages larger than given size in MB')
    parser.add_argument('--max-size', type=float, metavar='MB', help='Show packages smaller than given size in MB')
    parser.add_argument('--json', action='store_true', help='Output in JSON format (not implemented yet)')

    args = parser.parse_args()

    print("Starting package size analysis...")
    start = time.time()

    packages = get_installed_packages()
    if not packages:
        print("No packages found.")
        sys.exit(1)

    if args.min_size:
        before = len(packages)
        packages = [p for p in packages if p[1] >= args.min_size]
        if len(packages) < before:
            print(f"Filtered packages to >= {args.min_size} MB ({len(packages)}/{before})")
    
    if args.max_size:
        before = len(packages)
        packages = [p for p in packages if p[1] <= args.max_size]
        if len(packages) < before:
            print(f"Filtered packages to <= {args.max_size} MB ({len(packages)}/{before})")

    if args.top:
        packages.sort(key=lambda p: p[1], reverse=True)
        packages = packages[:args.top]
        print(f"Showing top {len(packages)} packages")
    
    if args.json:
        output = [
            {"package": name, "size_mb": size}
            for name, size in packages
        ]
        print(json.dumps(output, indent=2))
        sys.exit(1)
    else:
        print_packages(packages, sort_by=args.sort, descending=args.desc, filter_str=args.filter, show_total=True)

    elapsed = time.time() - start
    print(f"Analysis done in {elapsed:.2f} seconds")


if __name__ == "__main__":
    main()
