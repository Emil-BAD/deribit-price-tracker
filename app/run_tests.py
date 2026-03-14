import argparse
import sys

import pytest


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Test runner for this project (supports selective runs via pytest args)."
    )
    parser.add_argument(
        "--path",
        default="app/tests",
        help="Test path or file to run (default: app/tests).",
    )
    parser.add_argument(
        "pytest_args",
        nargs=argparse.REMAINDER,
        help="Additional pytest args, e.g. -k test_name or -m marker.",
    )
    args = parser.parse_args()

    pytest_args = [args.path]
    if args.pytest_args:
        if args.pytest_args[0] == "--":
            pytest_args.extend(args.pytest_args[1:])
        else:
            pytest_args.extend(args.pytest_args)

    return pytest.main(pytest_args)


if __name__ == "__main__":
    raise SystemExit(main())
