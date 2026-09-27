import argparse
import sys

from .pipeline import verify_config


def main(args: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Open Food Facts Quality CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    verify_parser = subparsers.add_parser("verify-config", help="Verify a frozen specification bundle")
    verify_parser.add_argument("--bundle", required=True, help="Path to the specification bundle directory")
    verify_parser.add_argument("--expected-sha256", required=True, help="Expected SHA-256 of the freeze_manifest.json")

    parsed_args = parser.parse_args(args)

    if parsed_args.command == "verify-config":
        success = verify_config(parsed_args.bundle, parsed_args.expected_sha256)
        if not success:
            sys.stderr.write("Verification failed.\n")
            return 1
        return 0
    return 1

if __name__ == "__main__":
    sys.exit(main())
