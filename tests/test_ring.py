import pytest
from plum import NotFoundLookupError

from ring import (
    Element,
    One,
    Zero,
    Wrapped,
    Scaled,
    Join,
    Product,
    Sum,

    add,
    mul,

    get_ring,
    new
)
from ring.ring import filter_most_specific
from .util import A, B, C


def test_equality_element():
    assert Element() != Element()


def test_equality_one_zero():
    assert One() == One()
    assert One() != Zero()
    assert Zero() == Zero()


def test_equality_scaled():
    assert Scaled(One(), 1) == Scaled(One(), 1)
    assert Scaled(One(), 2) != Scaled(One(), 1)
    assert Scaled(Zero(), 1) != Scaled(One(), 1)


def test_equality_product():
    assert Product(One(), Zero()) == Product(One(), Zero())
    assert Product(One(), Zero()) == Product(Zero(), One())
    assert Product(One(), Zero()) != Product(One(), One())


def test_equality_sum():
    assert Sum(One(), Zero()) == Sum(One(), Zero())
    assert Sum(One(), Zero()) == Sum(Zero(), One())
    assert Sum(One(), Zero()) != Sum(One(), One())


def test_addition():
    assert str(A() + 1) == 'A() + 1'
    assert str(1 + A()) == '1 + A()'


def test_subtraction():
    assert str(1 - A()) == '1 + -1 * A()'
    assert str(A() - 1) == 'A() + -1 * 1'
    assert str(A() - A()) == '0'
    assert str(B() - A()) == 'B() + -1 * A()'


def test_negation():
    assert str(-A()) == '-1 * A()'


def test_name():
    assert A.__name__ == 'A'


def test_str():
    assert str(1 - A()) == '1 + -1 * A()'


def test_repr():
    assert repr(1 - A()) == '1 + -1 * A()'


def test_power():
    with pytest.raises(ValueError):
        A() ** -1
    with pytest.raises(NotFoundLookupError):
        A() ** .5
    assert str(A() ** 0) == '1'
    assert str(A() ** 1) == 'A()'
    assert str(A() ** 2) == 'A() * A()'
    assert str(A() ** 3) == 'A() * A() * A()'


def test_terms():
    e = A() + A() * B() + C() * C() + B()
    assert e.num_terms == 4
    assert str(e.term(0)) == 'A()'
    assert str(e.term(1)) == 'A() * B()'
    assert str(e.term(2)) == 'C() * C()'
    assert str(e.term(3)) == 'B()'
    with pytest.raises(IndexError):
        e.term(4)
    with pytest.raises(IndexError):
        A().term(1)


def test_factors():
    e = A() * B()
    assert e.num_factors == 2
    assert str(e.factor(0)) == 'A()'
    assert str(e.factor(1)) == 'B()'
    with pytest.raises(IndexError):
        e.factor(2)

    e = (A() + A()) * C() * (B() + C())
    assert e.num_factors == 4
    assert str(e.factor(0)) == '2'
    assert str(e.factor(1)) == 'A()'
    assert str(e.factor(2)) == 'C()'
    assert str(e.factor(3)) == 'B() + C()'
    with pytest.raises(IndexError):
        e.factor(4)
    with pytest.raises(IndexError):
        A().factor(1)


def test_indexing_wrapped():
    e = 5 * A()
    assert str(e[0]) == 'A()'
    with pytest.raises(IndexError):
        e[1]


def test_indexing_sum():
    e = A() + B()
    assert str(e[0]) == 'A()'
    assert str(e[1]) == 'B()'
    with pytest.raises(IndexError):
        e[2]


def test_indexing_product():
    e = A() * B()
    assert str(e[0]) == 'A()'
    assert str(e[1]) == 'B()'
    with pytest.raises(IndexError):
        e[2]


def test_display_formatter():
    assert (3 * (Element() + 4)).display(lambda x: x ** 2) == \
           '9 * (Element() + 16 * 1)'


def test_add_fallback():
    with pytest.raises(RuntimeError):
        add('1', '2')


def test_mul_fallback():
    with pytest.raises(RuntimeError):
        mul('1', '2')


def test_get_ring():
    for x in [Element(), One(), Zero()]:
        assert get_ring(x) == Element

    with pytest.raises(RuntimeError):
        get_ring(1)


def test_new():
    class Kernel(Element):
        pass

    class SumKernel(Kernel, Sum):
        pass

    get_ring.extend(Kernel)(lambda _: Kernel)

    # Test that the ring is correctly registered.
    assert get_ring(SumKernel(Kernel(), Kernel())) == Kernel

    # Test the creation of a sum type, which should succeed.
    assert new(Kernel(), Sum) == SumKernel

    # Test the creation of a sum type, which should fail.
    with pytest.raises(RuntimeError):
        new(Kernel(), Product)


def test_filter_most_specific():
    class T1:
        pass

    class T2(T1):
        pass

    assert set(filter_most_specific([int, str])) == {int, str}
    assert set(filter_most_specific([int, str, object])) == {int, str}
    assert set(filter_most_specific([int, object, str])) == {int, str}
    assert set(filter_most_specific([T1, T2])) == {T2}
    assert set(filter_most_specific([T2, T1])) == {T2}
    assert set(filter_most_specific([int, T1, object, str, T2])) == \
           {int, str, T2}
