# ABOUTME: Downloads images from Plex server and saves them locally.
# ABOUTME: Converts authenticated Plex image URLs to local static files for deployment.

import hashlib
import re
from pathlib import Path
from typing import Any

import httpx
from rich.console import Console

console = Console()


def slugify(text: str) -> str:
    """Convert text to a safe filename slug."""
    # Remove special characters, keep alphanumeric and spaces
    text = re.sub(r'[^\w\s-]', '', text.lower())
    # Replace spaces with hyphens
    text = re.sub(r'[-\s]+', '-', text).strip('-')
    return text[:50]  # Limit length


def download_images(
    stats: dict[str, Any],
    username: str,
    output_dir: Path,
) -> dict[str, Any]:
    """Download all images from Plex and update stats with local paths.

    Args:
        stats: The processed stats dictionary containing image_urls
        username: The username for organizing images
        output_dir: Base output directory (typically frontend/public)

    Returns:
        Updated stats with local image paths
    """
    images_dir = output_dir / "images" / username
    images_dir.mkdir(parents=True, exist_ok=True)

    downloaded = 0
    failed = 0

    # Process top_artists
    for artist in stats.get("top_artists", []):
        if artist.get("image_url"):
            local_path = _download_image(
                artist["image_url"],
                f"artist-{slugify(artist['name'])}",
                images_dir,
            )
            if local_path:
                artist["image_url"] = f"/images/{username}/{local_path.name}"
                downloaded += 1
            else:
                artist["image_url"] = None
                failed += 1

    # Process top_tracks
    for track in stats.get("top_tracks", []):
        if track.get("image_url"):
            local_path = _download_image(
                track["image_url"],
                f"track-{slugify(track['artist'])}-{slugify(track['name'])}",
                images_dir,
            )
            if local_path:
                track["image_url"] = f"/images/{username}/{local_path.name}"
                downloaded += 1
            else:
                track["image_url"] = None
                failed += 1

    # Process top_albums
    for album in stats.get("top_albums", []):
        if album.get("image_url"):
            local_path = _download_image(
                album["image_url"],
                f"album-{slugify(album.get('artist', 'unknown'))}-{slugify(album['name'])}",
                images_dir,
            )
            if local_path:
                album["image_url"] = f"/images/{username}/{local_path.name}"
                downloaded += 1
            else:
                album["image_url"] = None
                failed += 1

    console.print(f"    [green]Downloaded {downloaded} images[/green]", end="")
    if failed > 0:
        console.print(f" [yellow]({failed} failed)[/yellow]")
    else:
        console.print()

    return stats


def _download_image(url: str, name: str, output_dir: Path) -> Path | None:
    """Download a single image from URL.

    Args:
        url: The Plex image URL (with token)
        name: Base name for the file
        output_dir: Directory to save the image

    Returns:
        Path to downloaded file, or None if failed
    """
    # Create a hash of the URL for uniqueness
    url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
    filename = f"{name}-{url_hash}.jpg"
    filepath = output_dir / filename

    # Skip if already downloaded
    if filepath.exists():
        return filepath

    try:
        with httpx.Client(timeout=30.0, follow_redirects=True) as client:
            response = client.get(url)
            response.raise_for_status()

            # Determine file extension from content type
            content_type = response.headers.get("content-type", "image/jpeg")
            if "png" in content_type:
                filepath = filepath.with_suffix(".png")
            elif "gif" in content_type:
                filepath = filepath.with_suffix(".gif")
            elif "webp" in content_type:
                filepath = filepath.with_suffix(".webp")

            filepath.write_bytes(response.content)
            return filepath

    except Exception as e:
        console.print(f"    [dim red]Failed to download {name}: {e}[/dim red]")
        return None
