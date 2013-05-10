import unittest

import os

from lillebror import BaseSampler, ProcessSampler
from mock import MagicMock, patch, call


class TestBaseSampler(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_sample_fail(self):
        s = BaseSampler()
        try:
            s.sample()
        except NotImplementedError:
            assert True

    def test_get_sample_fail(self):
        s = BaseSampler()
        try:
            s._get_sample()
        except NotImplementedError:
            assert True


class TestProcessSampler(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_pid(self):
        s = ProcessSampler(10)
        assert s._pid == 10

    def test_no_pid(self):
        s = ProcessSampler()
        pid = os.getpid()
        assert s._pid == pid

    def test_get_sample_fail(self):
        s = ProcessSampler()
        try:
            s._get_sample(None)
        except NotImplementedError:
            assert True

    def test_get_sample(self):
        s = ProcessSampler()
        try:
            s._get_sample(None)
        except NotImplementedError:
            assert True
