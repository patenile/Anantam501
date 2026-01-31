#!/usr/bin/env python3
"""
check_flaky_tests.py: Detects flaky/repeatedly failing tests from JUnit XML reports.
- Looks for tests that failed in the last N runs (default: 3)
- Prints a summary and exits nonzero if flakiness is detected
- Can be used in CI to trigger notifications
"""
import os
import sys
import glob
import xml.etree.ElementTree as ET
from collections import defaultdict

REPORTS_DIR = "reports"
HISTORY_DEPTH = 3  # Number of recent runs to check


# Find all JUnit XML files in reports/
def find_junit_reports():
    return sorted(glob.glob(os.path.join(REPORTS_DIR, "*-junit.xml")))


def parse_failures(xml_path):
    failures = set()
    try:
        tree = ET.parse(xml_path)
        for testcase in tree.findall(".//testcase"):
            if (
                testcase.find("failure") is not None
                or testcase.find("error") is not None
            ):
                name = (
                    testcase.attrib.get("classname", "")
                    + "."
                    + testcase.attrib.get("name", "")
                )
                failures.add(name)
    except Exception as e:
        print(f"[WARN] Could not parse {xml_path}: {e}")
    return failures


def main():
    all_reports = find_junit_reports()
    if not all_reports:
        print("[INFO] No JUnit XML reports found.")
        sys.exit(0)
    # Only check the last N runs
    recent_reports = all_reports[-HISTORY_DEPTH:]
    fail_history = defaultdict(int)
    for report in recent_reports:
        for test in parse_failures(report):
            fail_history[test] += 1
    flaky = [t for t, count in fail_history.items() if count >= 2]
    if flaky:
        print("[FLAKY] The following tests failed in multiple recent runs:")
        for t in flaky:
            print(f"  - {t}")
        sys.exit(1)
    else:
        print("[INFO] No flaky tests detected in recent runs.")
        sys.exit(0)


if __name__ == "__main__":
    main()
