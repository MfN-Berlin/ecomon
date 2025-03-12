from datetime import datetime


def parse_datetime(filename_stem):
    # Split filename into parts (e.g., "prefix_20231015_120000" -> ["prefix", "20231015", "120000"])
    parts = filename_stem.split("_")

    # Get the datetime parts (last two elements)
    if len(parts) < 2:
        raise ValueError(f"Invalid filename format: {filename_stem}")
    date_part = parts[-2]
    time_part = parts[-1]

    # Try different datetime formats
    try:
        return datetime.strptime(f"{date_part}_{time_part}", "%y%m%d_%H%M%S")
    except ValueError:
        pass
    try:
        return datetime.strptime(f"{date_part}_{time_part}", "%Y%m%d_%H%M%S")
    except ValueError:
        pass
    try:
        return datetime.strptime(f"{date_part}_{time_part}", "%Y%m%d_%H%M%S00")
    except ValueError as e:
        raise ValueError(
            f"Unable to parse datetime from filename: {filename_stem}"
        ) from e
