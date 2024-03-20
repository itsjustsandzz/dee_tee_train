import itertools
from Compiler import types, library, instructions, util
from Compiler.library import *

def dest_comp(B):
    Bt = B.transpose()
    St_flat = Bt.get_vector().prefix_sum()
    Tt_flat = Bt.get_vector() * St_flat.get_vector()
    Tt = types.Matrix(*Bt.sizes, B.value_type)
    Tt.assign_vector(Tt_flat)
    return sum(Tt) - 1

def reveal_sort(k, D, reverse=False):
    """ Sort in place according to "perfect" key. The name hints at the fact
    that a random order of the keys is revealed.

    :param k: vector or Array of sint containing exactly :math:`0,\dots,n-1`
      in any order
    :param D: Array or MultiArray to sort
    :param reverse: wether :py:obj:`key` is a permutation in forward or
      backward order

    """
    assert len(k) == len(D)
    library.break_point()
    shuffle = types.sint.get_secure_shuffle(len(k))
    k_prime = k.get_vector().secure_permute(shuffle).reveal()
    idx = types.Array.create_from(k_prime)
    if reverse:
        D.assign_vector(D.get_slice_vector(idx))
        library.break_point()
        D.secure_permute(shuffle, reverse=True)
    else:
        D.secure_permute(shuffle)
        library.break_point()
        v = D.get_vector()
        D.assign_slice_vector(idx, v)
    library.break_point()
    instructions.delshuffle(shuffle)

"""
def quick_sort_partition(a, i = -1):
    i_p = MemValue(i)
    m = len(a)
    e = Array.create_from(a)
    for j in range(0, m-1):
        c = e[j] <= e[m-1]
        c_revealed = c.reveal()
        @if_(c_revealed == 1)
        def _():
            i_p.iadd(1)
            e[i_p], e[j] = util.cond_swap(c, e[i_p], e[j])
    i_p.iadd(1)
    p = i_p
    e[p], e[m-1] = util.cond_swap(sint(1), e[p], e[m-1])
    return p, e
"""

def quick_sort_partition(a, left, right):
    i_p = MemValue(left-1)
    @for_range(left, right)
    def _(j):
        c = a[j] <= a[right]
        c_revealed = c.reveal()
        @if_(c_revealed == 1)
        def _():
            i_p.iadd(1)
            a[i_p], a[j] = util.cond_swap(c, a[i_p], a[j])
    i_p.iadd(1)
    p = i_p
    a[p], a[right] = util.cond_swap(sint(1), a[p], a[right])
    return p

def quick_sort(a, left, right):
    """
    :param a: Array or MultiArray to sort
    """
    @if_(left < right)
    def _():
        p = quick_sort_partition(a, left, right)
        @if_(left < p-1)
        def _():
            quick_sort(a, left, p-1)
        @if_(p+1 < right)
        def _():
            quick_sort(a, p+1, right)

def radix_sort(k, D, n_bits=None, signed=True):
    """ Sort in place according to key.

    :param k: keys (vector or Array of sint or sfix)
    :param D: Array or MultiArray to sort
    :param n_bits: number of bits in keys (int)
    :param signed: whether keys are signed (bool)

    """
    assert len(k) == len(D)
    bs = types.Matrix.create_from(k.get_vector().bit_decompose(n_bits))
    if signed and len(bs) > 1:
        bs[-1][:] = bs[-1][:].bit_not()
    radix_sort_from_matrix(bs, D)

def radix_sort_from_matrix(bs, D):
    n = len(D)
    for b in bs:
        assert(len(b) == n)
    B = types.sint.Matrix(n, 2)
    h = types.Array.create_from(types.sint(types.regint.inc(n)))
    @library.for_range(len(bs))
    def _(i):
        b = bs[i]
        B.set_column(0, 1 - b.get_vector())
        B.set_column(1, b.get_vector())
        c = types.Array.create_from(dest_comp(B))
        reveal_sort(c, h, reverse=False)
        @library.if_e(i < len(bs) - 1)
        def _():
            reveal_sort(h, bs[i + 1], reverse=True)
        @library.else_
        def _():
            reveal_sort(h, D, reverse=True)

def radix_sort_permutation_from_matrix(bs, D):
    n = len(D)
    for b in bs:
        assert(len(b) == n)
    B = types.sint.Matrix(n, 2)
    h = types.Array.create_from(types.sint(types.regint.inc(n)))
    @library.for_range(len(bs))
    def _(i):
        b = bs[i]
        B.set_column(0, 1 - b.get_vector())
        B.set_column(1, b.get_vector())
        c = types.Array.create_from(dest_comp(B))
        reveal_sort(c, h, reverse=False)
        @library.if_e(i < len(bs) - 1)
        def _():
            reveal_sort(h, bs[i + 1], reverse=True)
        @library.else_
        def _():
            reveal_sort(h, D, reverse=True)
    return h
