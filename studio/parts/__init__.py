"""Part registry — maps a part name to its generator.

The scene spec refers to parts by name only ("gear"), never by code, so a
render job can never execute arbitrary Python. To add a part: write a pure
generator in a bucket module and register it here.
"""
from . import mechanical

REGISTRY = {
    "gear": mechanical.make_gear,
}


def build(part, params):
    if part not in REGISTRY:
        raise ValueError(f"unknown part '{part}'. known: {sorted(REGISTRY)}")
    return REGISTRY[part](**(params or {}))
