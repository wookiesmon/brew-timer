"""Entry point: ``python -m main --venue coinbase --product BTC-USD --analyze``."""
import sys

from cli import main

if __name__ == "__main__":
    sys.exit(main())
