from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

import pytest
from django.conf import settings
from django.db import close_old_connections

from backend.apps.idgen.services import next_id


@pytest.mark.django_db(transaction=True)
def test_next_id_unique_and_prefixed() -> None:
    """Args: none. Returns: None."""
    a = next_id("task", "tsk_", width=10)
    b = next_id("task", "tsk_", width=10)

    assert a != b
    assert a.startswith("tsk_")
    assert b.startswith("tsk_")
    assert len(a) == len("tsk_") + 10


@pytest.mark.django_db(transaction=True)
def test_next_id_parallel_no_collisions() -> None:
    """Args: none. Returns: None."""
    if "sqlite" in settings.DATABASES["default"]["ENGINE"]:
        workers = 1
        per_worker = 50
    else:
        workers = 5
        per_worker = 20

    def worker() -> list[str]:
        close_old_connections()
        return [next_id("category", "cat_", width=12) for _ in range(per_worker)]

    with ThreadPoolExecutor(max_workers=workers) as ex:
        results = list(ex.map(lambda _: worker(), range(workers)))

    flat = [x for batch in results for x in batch]
    assert len(flat) == len(set(flat))
