"""Isolated JSON persistence for customer, cart and order records."""
import json
import os
import tempfile
from pathlib import Path
from threading import RLock

_LOCK = RLock()
DEFAULT_FILE = Path(__file__).resolve().parents[2] / 'data' / 'commerce.json'


class CommerceRepository:
    def __init__(self, path=None):
        self.path = Path(path or os.environ.get('COMMERCE_DATA_PATH', DEFAULT_FILE))
        self.lock = _LOCK

    def read(self):
        if not self.path.exists():
            return {'customers': {}, 'carts': {}, 'orders': {}}
        with self.path.open(encoding='utf-8') as f:
            result = json.load(f)
        for key in ('customers', 'carts', 'orders'):
            result.setdefault(key, {})
        return result

    def save(self, data):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, name = tempfile.mkstemp(prefix='.commerce-', suffix='.tmp', dir=self.path.parent)
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
                f.flush()
                os.fsync(f.fileno())
            os.replace(name, self.path)
        finally:
            if os.path.exists(name):
                os.unlink(name)
