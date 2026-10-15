import argparse
import pathlib
import subprocess
import unittest

MARKER = "CREW_PUBLIC_GATEWAY_FIXTURE_V1: disposable synthetic merge observation only.\n"
MARKER_PATH = "crew-wayfinder-gateway-fixture.txt"


def valid_marker(content):
    return content == MARKER


def valid_changes(paths):
    return paths == [MARKER_PATH]


class FixtureContract(unittest.TestCase):
    def test_exact_marker(self):
        self.assertTrue(valid_marker(MARKER))

    def test_empty_marker(self):
        self.assertFalse(valid_marker(""))

    def test_modified_marker(self):
        self.assertFalse(valid_marker(MARKER + "unexpected\n"))

    def test_expected_file(self):
        self.assertTrue(valid_changes([MARKER_PATH]))

    def test_missing_changes(self):
        self.assertFalse(valid_changes([]))

    def test_workflow_change(self):
        self.assertFalse(valid_changes([MARKER_PATH, ".github/workflows/fixture.yml"]))

    def test_other_file(self):
        self.assertFalse(valid_changes(["outside.txt"]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--base")
    parser.add_argument("--head")
    arguments = parser.parse_args()
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(FixtureContract))
    if not result.wasSuccessful() or result.testsRun != 7:
        raise SystemExit(1)
    if arguments.base or arguments.head:
        if not arguments.base or not arguments.head:
            raise SystemExit("Both base and head are required")
        changed = subprocess.check_output(["git", "diff", "--name-only", "--no-renames", arguments.base, arguments.head], text=True).splitlines()
        if not valid_changes(changed):
            raise SystemExit("Fixture PR must change only the marker file: " + repr(changed))
        if not valid_marker(pathlib.Path(MARKER_PATH).read_text()):
            raise SystemExit("Actual head marker does not match the fixture contract")
        print("Actual fixture head marker and changed-file scope verified")
