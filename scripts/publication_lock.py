"""Process-safe advisory locks for one checkout's publication transactions."""
from contextlib import contextmanager
import os
from pathlib import Path
import time


@contextmanager
def publication_lock(path: Path, *, timeout: float = 30):
    """Serialize cooperating processes; branch integration handles other hosts.

    Keep the lock inode after release: deleting it would let later processes
    lock a different inode while an earlier waiter still holds the old one.
    The OS releases the advisory lock if its process crashes.
    """
    path = Path(path)
    if path.is_symlink():
        raise ValueError("Publication lock must not be a symlink")
    path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags, 0o600)
    with os.fdopen(descriptor, "r+b") as handle:
        if os.name == "nt":
            import msvcrt
            if path.stat().st_size == 0:
                handle.write(b"0")
                handle.flush()
            def lock():
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            def unlock():
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl
            def lock():
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            def unlock():
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        deadline = time.monotonic() + timeout
        while True:
            try:
                lock()
                break
            except (BlockingIOError, OSError):
                if time.monotonic() >= deadline:
                    raise TimeoutError("Another publication transaction is active in this checkout")
                time.sleep(0.05)
        try:
            yield
        finally:
            unlock()
