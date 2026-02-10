#!/bin/bash
vendors="$(uv run vendors.py)"
uv pip install -t src/subtitleterms/vendor ${vendors}
