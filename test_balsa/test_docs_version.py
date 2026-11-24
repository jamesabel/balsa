"""
Tests for the documentation version. All tests in this file are AI-authored (see the marker above each test).
"""

import runpy
from pathlib import Path

from balsa import __version__

sphinx_conf_path = Path(__file__).parent.parent / "docs" / "source" / "conf.py"


# AI-GENERATED TEST (Claude Code) - delete this line to make this test human-owned.
def test_docs_version_is_package_version():
    # the Sphinx configuration is a plain Python file: run it the way Sphinx does and check the version it reports
    sphinx_conf = runpy.run_path(str(sphinx_conf_path))
    assert sphinx_conf["release"] == __version__
    major, minor, _unused_patch = __version__.split(".")
    assert sphinx_conf["version"] == f"{major}.{minor}"
