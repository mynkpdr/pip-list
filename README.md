# pip-list

A fast and human-readable tool to list installed pip packages with their sizes, supporting sorting, filtering, and more.

## Features

- Lists all installed pip packages with their installed size
- Sort packages by name or size (ascending/descending)
- Filter packages by name substring
- Show only the top N largest packages
- Show only packages larger than a given size (in MB)
- Displays total size and package count
- Fast, uses multi-threading for speed
- JSON output supported

## Installation

```bash
pip install pip-list
```

## Usage

```bash
pip-list [OPTIONS]
```

### Options

- `--version`           Show version and exit
- `--sort name|size`    Sort by name or size (default: size)
- `--desc`              Sort in descending order
- `--filter TEXT`       Filter packages by name substring
- `--top N`             Show top N largest packages only
- `--min-size MB`       Show packages larger than given size in MB
- `--max-size MB`       Show packages lesser than given size in MB
- `--json`              Show packages in JSON format

### Examples

List all packages sorted by size (default):

```bash
pip-list
```

List all packages sorted by name:

```bash
pip-list --sort name
```

Show top 10 largest packages:

```bash
pip-list --top 10
```

Show only packages larger than 5 MB:

```bash
pip-list --min-size 5
```

Show only packages lesser than 50 MB:

```bash
pip-list --max-size 50
```

Filter packages containing "numpy":

```bash
pip-list --filter numpy
```

Sort by size descending:

```bash
pip-list --sort size --desc
```

Show packages in JSON format:

```bash
pip-list --json
```

## License

MIT
