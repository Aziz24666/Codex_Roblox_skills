#!/usr/bin/env python3
"""Transparent bootstrap for the compressed, versioned V21 tool source."""
from __future__ import annotations

import gzip
from pathlib import Path

_source_path = Path(__file__).with_name(Path(__file__).name + ".gz")
_source = gzip.decompress(_source_path.read_bytes())
exec(compile(_source, str(Path(__file__)), "exec"), globals())
