from requests import get, RequestException
from pathlib import Path
from time import time
from unveil.exceptions import DownloadInterrupted

from rich.progress import (
    Progress,
    BarColumn,
    DownloadColumn,
    TransferSpeedColumn,
    TimeRemainingColumn,
)


def _download_file(
    url: str,
    filename: str,
    use_cache: bool = True,
    headers: dict = None,
    cache_ttl: int = 3600,
) -> Path:
    cache_dir = Path.home() / ".unveil/cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / filename
    temp_path = cache_dir / f"{filename}.tmp"

    if use_cache and cache_path.exists():
        file_age = time() - cache_path.stat().st_mtime
        if file_age < cache_ttl:
            # log.info(f"Using cached file: {cache_path}")
            print(f"Using cached file: {cache_path}")
            return cache_path

    # log.info(f"Downloading file from {url}...")
    print(f"Downloading file from {url}...")
    try:
        with (
            get(url, headers=headers, stream=True)
            if headers
            else get(url, stream=True) as response
        ):
            response.raise_for_status()
            total_size = int(response.headers.get("Content-Length", 0))

            with Progress(
                "[progress.description]{task.description}",
                BarColumn(),
                DownloadColumn(),
                TransferSpeedColumn(),
                TimeRemainingColumn(),
            ) as progress:
                task = progress.add_task("[cyan]Downloading...", total=total_size)

                with open(temp_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                        progress.update(task, advance=len(chunk))

        if cache_path.exists():
            cache_path.unlink()

        temp_path.rename(cache_path)
        print(f"File downloaded and cached at: {cache_path}")
    except (RequestException, KeyboardInterrupt) as e:
        # log.error(e)
        print(f"Download failed: {e}")
        temp_path.unlink(missing_ok=True)
        raise DownloadInterrupted("Please re-run program, download failed!")

    return cache_path
