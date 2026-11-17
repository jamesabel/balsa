"""
Tests for the package version. All tests in this file are AI-authored (see the marker above each test).
"""

import re

from balsa import __version__

# release tags are "v" + this version (see .github/workflows/publish.yml), so it must be a plain X.Y.Z release version
release_version_regex = re.compile(r"^\d+\.\d+\.\d+$")


# AI-GENERATED TEST (Claude Code) - delete this line to make this test human-owned.
def test_version_is_release_version():
    assert release_version_regex.match(__version__) is not None, __version__
