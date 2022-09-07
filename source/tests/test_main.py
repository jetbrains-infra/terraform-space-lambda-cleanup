"""Unit tests file"""
import logging
import os
import unittest
from datetime import datetime

from lambda_function import main

logging.basicConfig(level=logging.DEBUG)


def get_case_data(path):
    """Collect case"""
    script_dir = os.path.dirname(__file__)
    rel_path = path
    abs_file_path = os.path.join(script_dir, rel_path)
    with open(abs_file_path, encoding="UTF-8") as file:
        content = file.read().splitlines()
    input_list = []
    for i in content:
        input_list.append(datetime.strptime(i, "%Y-%m-%d-%H:%M:%S"))
    return input_list


class TestFilterDateCaseOne(unittest.TestCase):
    """Unit tests for main.filter_date"""

    def setUp(self):
        self.result = main.filter_date(get_case_data("fixtures/case_one/input.txt"))
        self.expected = get_case_data("fixtures/case_one/expected.txt")

    def test_python_function(self):
        """Unit tests for case one"""
        self.assertListEqual(self.result, self.expected)


class TestFilterDateCaseTwo(unittest.TestCase):
    """Unit tests for main.filter_date"""

    def setUp(self):
        self.result = main.filter_date(get_case_data("fixtures/case_two/input.txt"))
        self.expected = get_case_data("fixtures/case_two/expected.txt")

    def test_python_function(self):
        """Unit tests for case two"""
        self.assertListEqual(self.result, self.expected)


class TestFilterDateCaseThree(unittest.TestCase):
    """Unit tests for main.filter_date"""

    def setUp(self):
        self.result = main.filter_date(get_case_data("fixtures/case_three/input.txt"))
        self.expected = get_case_data("fixtures/case_three/expected.txt")

    def test_python_function(self):
        """Unit tests for case three"""
        self.assertListEqual(self.result, self.expected)


class TestFilterDateCaseFour(unittest.TestCase):
    """Unit tests for main.filter_date"""

    def setUp(self):
        self.result = main.filter_date(get_case_data("fixtures/case_four/input.txt"))
        self.expected = get_case_data("fixtures/case_four/expected.txt")

    def test_python_function(self):
        """Unit tests for case four"""
        self.assertListEqual(self.result, self.expected)


if __name__ == "__main__":
    unittest.main()
