"""The Python shell around the CEVG renderer: voice now, the MCP server later.

It talks to the Rust core through the `cevg` command-line tool and to Sarvam
over HTTPS, and uses only the Python standard library.
"""

__all__ = ["sarvam", "voice", "narrate"]
