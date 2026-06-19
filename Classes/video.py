import hashlib
import os

class Video:
    def __init__(self, path: str):
        self.path: str = path
        self.name: str = os.path.splitext(os.path.basename(path))[0]
        self.creation_time: float = os.path.getctime(path)
        self.video_id: str = self.hash_video_file(self.path)

    def hash_video_file(self, path: str, chunk_size: int = 1024 * 1024) -> str:
        digest = hashlib.sha256()
        with open(path, "rb") as f:
            while chunk := f.read(chunk_size):
                digest.update(chunk)
        return digest.hexdigest()