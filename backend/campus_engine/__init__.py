"""Campus Chommie engine.

Pure Python with no web, UI or database imports (tests/architecture/test_engine_boundaries.py
enforces it), so the same logic serves the Flask API, the WhatsApp bot and anything else
that needs it. Services call the engine; routes never do.
"""

__version__ = "0.1.0"
