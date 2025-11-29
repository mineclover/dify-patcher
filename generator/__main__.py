"""Allow running the generator as a module: python -m generator"""

from .cli import main

if __name__ == '__main__':
    raise SystemExit(main())
