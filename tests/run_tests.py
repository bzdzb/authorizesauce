#!/usr/bin/env python
import os
import sys
from unittest import TestCase
if not hasattr(TestCase, 'assertIsNotNone'):
    from unittest2 import TestLoader, TextTestRunner
else:
    from unittest import TestLoader, TextTestRunner


if __name__ == '__main__':
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    authorize_dir = os.path.join(tests_dir, os.path.pardir)
    sys.path.insert(0, authorize_dir)
    suite = TestLoader().discover(tests_dir)
    runner = TextTestRunner(verbosity=1)
    runner.run(suite)
