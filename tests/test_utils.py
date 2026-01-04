from pathlib import Path
from utils import chapter_id_from_path


def test_chapter_id_from_path_simple():
    assert chapter_id_from_path(Path("chapters/1000_zh.txt")) == "1000"
    assert chapter_id_from_path("chapters/1000_vi.txt") == "1000"
    assert chapter_id_from_path("/tmp/2000_en.md") == "2000"
