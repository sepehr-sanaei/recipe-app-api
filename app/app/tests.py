"""
Simple Test for Calc
"""

from django.test import SimpleTestCase
from app import calc


class CalcTest(SimpleTestCase):
    """Test for calc view"""

    def test_add_numbers(self):
        """testing the add functionality for clac view"""
        res = calc.add(10, 11)
        self.assertEqual(res, 21)

    def test_subtract_numbers(self):
        """testing the substract functionality of calc view"""
        res = calc.subtract(20, 30)
        self.assertEqual(res, -10)
