import unittest
from fractions import Fraction

from evkit.units import Quantity, DimensionError


class TestConstruction(unittest.TestCase):
    def test_string_unit_matches_tuple_unit(self):
        a = Quantity(5, 'm')
        b = Quantity(5, (1, 0, 0, 0, 0, 0, 0))
        self.assertEqual(a, b)

    def test_prefix_scaling(self):
        self.assertEqual(Quantity(1, 'km').value, 1000)
        self.assertEqual(Quantity(1, 'mm').value, 0.001)
        self.assertEqual(Quantity(1, 'g').value, 0.001)

    def test_compound_string_unit(self):
        q = Quantity(9.81, 'm/s2')
        self.assertEqual(q.base_unit, (1, 0, -2, 0, 0, 0, 0))
        self.assertAlmostEqual(q.value, 9.81)


class TestEachBaseDimension(unittest.TestCase):
    def test_length(self):
        self.assertEqual(Quantity(1, 'm').base_unit, (1, 0, 0, 0, 0, 0, 0))

    def test_mass(self):
        self.assertEqual(Quantity(1, 'kg').base_unit, (0, 1, 0, 0, 0, 0, 0))

    def test_time(self):
        self.assertEqual(Quantity(1, 's').base_unit, (0, 0, 1, 0, 0, 0, 0))

    def test_current(self):
        self.assertEqual(Quantity(1, 'A').base_unit, (0, 0, 0, 1, 0, 0, 0))

    def test_temperature(self):
        self.assertEqual(Quantity(1, 'K').base_unit, (0, 0, 0, 0, 1, 0, 0))

    def test_amount(self):
        self.assertEqual(Quantity(1, 'mol').base_unit, (0, 0, 0, 0, 0, 1, 0))

    def test_luminosity(self):
        self.assertEqual(Quantity(1, 'cd').base_unit, (0, 0, 0, 0, 0, 0, 1))


class TestOperators(unittest.TestCase):
    def test_add_same_dims(self):
        result = Quantity(500, 'm') + Quantity(2, 'km')
        self.assertAlmostEqual(result.value, 2500)

    def test_sub_same_dims(self):
        result = Quantity(5, 'km') - Quantity(500, 'm')
        self.assertAlmostEqual(result.value, 4500)

    def test_neg(self):
        self.assertEqual((-Quantity(5, 'm')).value, -5)

    def test_mul_quantities_gives_force(self):
        force = Quantity(9.81, 'm/s2') * Quantity(70, 'kg')
        self.assertEqual(force.base_unit, (1, 1, -2, 0, 0, 0, 0))
        self.assertAlmostEqual(force.value, 686.7)
        self.assertIn('N', repr(force))

    def test_mul_by_scalar(self):
        q = Quantity(5, 'm') * 3
        self.assertEqual(q.value, 15)
        self.assertEqual(q.base_unit, (1, 0, 0, 0, 0, 0, 0))

    def test_rmul_by_scalar(self):
        q = 3 * Quantity(5, 'm')
        self.assertEqual(q.value, 15)

    def test_truediv_quantities_dimensionless(self):
        result = Quantity(10, 'm') / Quantity(2, 'm')
        self.assertTrue(result.is_dimensionless)
        self.assertEqual(result.value, 5)

    def test_truediv_by_scalar(self):
        q = Quantity(10, 'm') / 2
        self.assertEqual(q.value, 5)

    def test_rtruediv_scalar(self):
        q = 1 / Quantity(4, 's')
        self.assertEqual(q.base_unit, (0, 0, -1, 0, 0, 0, 0))
        self.assertEqual(q.value, 0.25)

    def test_pow_integer(self):
        area = Quantity(3, 'm') ** 2
        self.assertEqual(area.base_unit, (2, 0, 0, 0, 0, 0, 0))
        self.assertEqual(area.value, 9)

    def test_pow_fractional_sqrt_of_area_is_length(self):
        area = Quantity(9, 'm2')
        length = area ** Fraction(1, 2)
        self.assertEqual(length.base_unit, (1, 0, 0, 0, 0, 0, 0))
        self.assertEqual(length.value, 3)

    def test_comparisons(self):
        self.assertTrue(Quantity(1, 'km') > Quantity(500, 'm'))
        self.assertTrue(Quantity(500, 'm') < Quantity(1, 'km'))
        self.assertTrue(Quantity(1000, 'm') >= Quantity(1, 'km'))
        self.assertTrue(Quantity(1000, 'm') <= Quantity(1, 'km'))
        self.assertEqual(Quantity(1000, 'm'), Quantity(1, 'km'))


class TestConversion(unittest.TestCase):
    def test_kmh_to_ms(self):
        speed = Quantity(36, 'km/h')
        self.assertAlmostEqual(speed.to('m/s'), 10.0)

    def test_ms_to_kmh(self):
        speed = Quantity(10, 'm/s')
        self.assertAlmostEqual(speed.to('km/h'), 36.0)


class TestNamedUnits(unittest.TestCase):
    def test_joule(self):
        energy = Quantity(70, 'kg') * Quantity(3, 'm') ** 2 / Quantity(2, 's') ** 2
        self.assertEqual(energy.base_unit, (2, 1, -2, 0, 0, 0, 0))
        self.assertIn('J', repr(energy))

    def test_parsec_is_a_length(self):
        d = Quantity(1, 'pc')
        self.assertEqual(d.base_unit, (1, 0, 0, 0, 0, 0, 0))
        self.assertIn('m', repr(Quantity(1, 'm')))  # 'm' stays canonical, not 'pc'


class TestEdgeCases(unittest.TestCase):
    def test_zero_value(self):
        self.assertEqual((Quantity(0, 'm') + Quantity(0, 'm')).value, 0)

    def test_negative_value(self):
        self.assertEqual(Quantity(-5, 'm').value, -5)

    def test_very_large_and_small_magnitudes(self):
        big = Quantity(1, 'Ym')     # yottametre
        small = Quantity(1, 'ym')   # yoctometre
        self.assertAlmostEqual(big.value, 1e24)
        self.assertAlmostEqual(small.value, 1e-24)


class TestErrors(unittest.TestCase):
    def test_add_incompatible_dims_raises(self):
        with self.assertRaises(DimensionError):
            Quantity(1, 'm') + Quantity(1, 's')

    def test_sub_incompatible_dims_raises(self):
        with self.assertRaises(DimensionError):
            Quantity(1, 'm') - Quantity(1, 'kg')

    def test_compare_incompatible_dims_raises(self):
        with self.assertRaises(DimensionError):
            Quantity(1, 'm') < Quantity(1, 's')

    def test_to_incompatible_unit_raises(self):
        with self.assertRaises(DimensionError):
            Quantity(1, 'm').to('s')

    def test_unknown_unit_raises(self):
        with self.assertRaises(ValueError):
            Quantity(1, 'bananas')

    def test_add_bare_number_to_dimensioned_quantity_raises(self):
        with self.assertRaises(DimensionError):
            Quantity(1, 'm') + 5


if __name__ == '__main__':
    unittest.main(verbosity=2)