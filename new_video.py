import re
from pathlib import Path


def get_next_index(videos_dir: Path, pictures_dir: Path) -> int:
    video_pattern = re.compile(r"^video(\d+)\.py$")
    thumb_pattern = re.compile(r"^video(\d+)_thumbnail\.py$")

    max_num = 0

    if videos_dir.exists():
        for file in videos_dir.iterdir():
            if file.is_file():
                match = video_pattern.match(file.name)
                if match:
                    max_num = max(max_num, int(match.group(1)))

    if pictures_dir.exists():
        for file in pictures_dir.iterdir():
            if file.is_file():
                match = thumb_pattern.match(file.name)
                if match:
                    max_num = max(max_num, int(match.group(1)))

    return max_num + 1


def create_next_files(base_dir: str = ".") -> tuple[Path, Path]:
    base = Path(base_dir)
    videos_dir = base / "videos"
    pictures_dir = base / "pictures"

    videos_dir.mkdir(parents=True, exist_ok=True)
    pictures_dir.mkdir(parents=True, exist_ok=True)

    next_num = get_next_index(videos_dir, pictures_dir)

    video_file = videos_dir / f"video{next_num}.py"
    thumbnail_file = pictures_dir / f"video{next_num}_thumbnail.py"

    video_file.write_text(f"# Video script {next_num}\n", encoding="utf-8")
    thumbnail_file.write_text(
        f"# Thumbnail script for video {next_num}\n", encoding="utf-8"
    )

    return video_file, thumbnail_file


if __name__ == "__main__":
    created_video, created_thumb = create_next_files()
    print(f"Created: {created_video}")
    print(f"Created: {created_thumb}")
