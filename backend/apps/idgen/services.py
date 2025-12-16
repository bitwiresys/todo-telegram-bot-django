from __future__ import annotations

from contextlib import suppress

from django.db import IntegrityError, transaction

from backend.apps.idgen.models import Sequence


def _base36_encode(value: int) -> str:
    """Args: value. Returns: base36 string."""
    if value < 0:
        raise ValueError("value must be >= 0")
    if value == 0:
        return "0"

    alphabet = "0123456789abcdefghijklmnopqrstuvwxyz"
    out: list[str] = []
    current = value
    while current:
        current, rem = divmod(current, 36)
        out.append(alphabet[rem])
    return "".join(reversed(out))


def next_id(sequence_name: str, prefix: str, width: int = 13) -> str:
    """Args: sequence_name, prefix, width. Returns: new deterministic id."""
    with transaction.atomic():
        try:
            seq = Sequence.objects.select_for_update().get(name=sequence_name)
        except Sequence.DoesNotExist:
            with suppress(IntegrityError):
                Sequence.objects.create(name=sequence_name, value=0)
            seq = Sequence.objects.select_for_update().get(name=sequence_name)

        seq.value += 1
        seq.save(update_fields=["value"])

        encoded = _base36_encode(seq.value).zfill(width)
        return f"{prefix}{encoded}"
