from Compiler.types import *
from Compiler.sorting import *
from Compiler.library import *
from Compiler import util, oram

from itertools import accumulate
import math

debug = False
debug_split = False
max_leaves = None

def get_type(x):
    if isinstance(x, (Array, SubMultiArray)):
        return x.value_type
    elif isinstance(x, (tuple, list)):
        x = x[0] + x[-1]
        if util.is_constant(x):
            return cint
        else:
            return type(x)
    else:
        return type(x)

def GetSortPerm(keys, *to_sort, n_bits=None, time=False):
    for k in keys:
        assert len(k) == len(keys[0])
    n_bits = n_bits or [None] * len(keys)
    bs = Matrix.create_from(sum([k.get_vector().bit_decompose(nb)
             for k, nb in reversed(list(zip(keys, n_bits)))], []))
    get_vec = lambda x: x[:] if isinstance(x, Array) else x
    res = Matrix.create_from(get_vec(x).v if isinstance(get_vec(x), sfix) else x
                             for x in to_sort)
    res = res.transpose()
    return radix_sort_permutation_from_matrix(bs, res)

def PrefixSum(x):
    return x.get_vector().prefix_sum()

def PrefixSumR(x):
    tmp = get_type(x).Array(len(x))
    tmp.assign_vector(x)
    break_point()
    tmp[:] = tmp.get_reverse_vector().prefix_sum()
    break_point()
    return tmp.get_reverse_vector()

def PrefixSum_inv(x):
    tmp = get_type(x).Array(len(x) + 1)
    tmp.assign_vector(x, base=1)
    tmp[0] = 0
    return tmp.get_vector(size=len(x), base=1) - tmp.get_vector(size=len(x))

def PrefixSumR_inv(x):
    tmp = get_type(x).Array(len(x) + 1)
    tmp.assign_vector(x)
    tmp[-1] = 0
    return tmp.get_vector(size=len(x)) - tmp.get_vector(base=1, size=len(x))

def ApplyPermutation(perm, x):
    res = Array.create_from(x)
    reveal_sort(perm, res, False)
    return res

def ApplyInversePermutation(perm, x):
    res = Array.create_from(x)
    reveal_sort(perm, res, True)
    return res

class SortPerm:
    def __init__(self, x):
        B = sint.Matrix(len(x), 2)
        B.set_column(0, 1 - x.get_vector())
        B.set_column(1, x.get_vector())
        self.perm = Array.create_from(dest_comp(B))
    def apply(self, x):
        res = Array.create_from(x)
        reveal_sort(self.perm, res, False)
        return res
    def unapply(self, x):
        res = Array.create_from(x)
        reveal_sort(self.perm, res, True)
        return res

def Sort(keys, *to_sort, n_bits=None, time=False):
    if time:
        start_timer(1)
    for k in keys:
        assert len(k) == len(keys[0])
    n_bits = n_bits or [None] * len(keys)
    bs = Matrix.create_from(
        sum([k.get_vector().bit_decompose(nb)
             for k, nb in reversed(list(zip(keys, n_bits)))], []))
    get_vec = lambda x: x[:] if isinstance(x, Array) else x
    res = Matrix.create_from(get_vec(x).v if isinstance(get_vec(x), sfix) else x
                             for x in to_sort)
    res = res.transpose()
    if time:
        start_timer(11)
    radix_sort_from_matrix(bs, res)
    if time:
        stop_timer(11)
        stop_timer(1)
    res = res.transpose()
    return [sfix._new(get_vec(x), k=get_vec(y).k, f=get_vec(y).f)
            if isinstance(get_vec(y), sfix)
            else x for (x, y) in zip(res, to_sort)]

def VectMax(key, *data, debug=False):
    def reducer(x, y):
        b = x[0]*y[1] > y[0]*x[1]
        if debug:
            print_ln('x: %s y: %s', util.reveal(x), util.reveal(y))
            print_ln('max b=%s', b.reveal())
        return [b.if_else(xx, yy) for xx, yy in zip(x, y)]
    if debug:
        key = list(key)
        data = [list(x) for x in data]
        print_ln('vect max key=%s data=%s', util.reveal(key), util.reveal(data))
    res = util.tree_reduce(reducer, zip(key, *data))
    if debug:
        print_ln('vect max res=%s', util.reveal(res))
    return res

def GroupSum(g, x):
    assert len(g) == len(x)
    p = PrefixSumR(x) * g
    pi = SortPerm(g.get_vector().bit_not())
    p1 = pi.apply(p)
    s1 = PrefixSumR_inv(p1)
    d1 = PrefixSum_inv(s1)
    d = pi.unapply(d1) * g
    return PrefixSum(d)

def GroupPrefixSum(g, x):
    assert len(g) == len(x)
    s = get_type(x).Array(len(x) + 1)
    s[0] = 0
    s.assign_vector(PrefixSum(x), base=1)
    q = get_type(s).Array(len(x))
    q.assign_vector(s.get_vector(size=len(x)) * g)
    return s.get_vector(size=len(x), base=1) - GroupSum(g, q)

def Custom_GT_Fractions(x_num, x_den, y_num, y_den, n_threads=2):
    b = (x_num*y_den) > (x_den*y_num)
    b = Array.create_from(b).get_vector()
    return b

def GroupMax(g, keys, *x, debug=False):
    if debug:
        print_ln('group max input g=%s keys=%s x=%s', util.reveal(g),
                 util.reveal(keys), util.reveal(x))
        print_ln("Zipped keys and data: %s", util.reveal((x[0]).get_vector(size=4)))
        print_ln("Shifted Zipped keys and data: %s", util.reveal(x[0].get_vector(size=4, base=1)))
        print_ln("Shifted Zipped keys and data: %s", util.reveal(x[0].get_vector(size=4, base=2)))
    assert len(keys) == len(g)
    for xx in x:
        assert len(xx) == len(g)
    n = len(g)
    m = int(math.ceil(math.log(n, 2)))
    keys = Array.create_from(keys)
    x = [Array.create_from(xx) for xx in x]
    g_new = Array.create_from(g)
    g_old = g_new.same_shape()
    for d in range(m):
        w = 2 ** d
        g_old[:] = g_new[:]
        break_point()
        vsize = n - w
        g_new.assign_vector(g_old.get_vector(size=vsize).bit_or(
            g_old.get_vector(size=vsize, base=w)), base=w)
        b = Custom_GT_Fractions(keys.get_vector(size=vsize), x[0].get_vector(size=vsize), keys.get_vector(size=vsize, base=w), x[0].get_vector(size=vsize, base=w))
        for xx in [keys] + x:
            a = b.if_else(xx.get_vector(size=vsize),
                          xx.get_vector(size=vsize, base=w))
            xx.assign_vector(g_old.get_vector(size=vsize, base=w).if_else(
                xx.get_vector(size=vsize, base=w), a), base=w)
        break_point()
        if debug:
            print_ln('group max w=%s b=%s a=%s keys=%s x=%s g=%s', w, b.reveal(),
                     util.reveal(a), util.reveal(keys),
                     util.reveal(x), g_new.reveal())
    t = sint.Array(len(g))
    t[-1] = 1
    t.assign_vector(g.get_vector(size=n - 1, base=1))
    if debug:
        print_ln('group max end g=%s t=%s keys=%s x=%s', util.reveal(g),
                 util.reveal(t), util.reveal(keys), util.reveal(x))
    return [GroupSum(g, t[:] * xx) for xx in [keys] + x]

def ComputeGini(g, x, y, notysum, ysum, debug=False):
    assert len(g) == len(y)
    y = [y.get_vector().bit_not(), y]
    u = [GroupPrefixSum(g, yy) for yy in y]
    s = [notysum, ysum]
    w = [ss - uu for ss, uu in zip(s, u)]
    us = sum(u)
    ws = sum(w)
    uqs = u[0] ** 2 + u[1] ** 2
    wqs = w[0] ** 2 + w[1] ** 2
    res_num = ws * uqs + us * wqs
    res_den = us * ws
    if debug:
        print_ln("x: %s", util.reveal(x))
        print_ln("not y and y: %s", util.reveal(y))
        print_ln("u: %s", util.reveal(u))
        print_ln("s: %s", util.reveal(s))
        print_ln("w: %s", util.reveal(w))
        print_ln("us: %s", util.reveal(us))
        print_ln("ws: %s", util.reveal(ws))
        print_ln("uqs: %s", util.reveal(uqs))
        print_ln("wqs: %s", util.reveal(wqs))
        print_ln("res_num: %s", util.reveal(res_num))
        print_ln("res_den: %s", util.reveal(res_den))
    xx = x
    t = get_type(x).Array(len(x))
    t[-1] = MIN_VALUE
    t.assign_vector(xx.get_vector(size=len(x) - 1) + \
                    xx.get_vector(size=len(x) - 1, base=1))
    gg = g
    p = sint.Array(len(x))
    p[-1] = 1
    p.assign_vector(gg.get_vector(base=1, size=len(x) - 1).bit_or(
        xx.get_vector(size=len(x) - 1) == \
        xx.get_vector(size=len(x) - 1, base=1)))
    break_point()
    if debug:
        print_ln('attribute t=%s p=%s', util.reveal(t), util.reveal(p))
    res_num = p[:].if_else(MIN_VALUE, res_num)
    res_den = p[:].if_else(1, res_den)
    t = p[:].if_else(MIN_VALUE, t[:])
    return res_num, res_den, t

MIN_VALUE = -10000

def FormatLayer(h, g, *a, debug=False):
    return CropLayer(h, *FormatLayer_without_crop(g, *a, debug=debug))

def FormatLayer_without_crop(g, *a, debug=False):
    for x in a:
        assert len(x) == len(g)
    v = [g.if_else(aa, 0) for aa in a]
    if debug:
        print_ln('format in %s', util.reveal(a))
        print_ln('format mux %s', util.reveal(v))
    p = SortPerm(g.get_vector().bit_not())
    v = [p.apply(vv) for vv in v]
    if debug:
        print_ln('format sort %s', util.reveal(v))
    return v

def CropLayer(k, *v):
    if max_leaves:
        n = min(2 ** k, max_leaves)
    else:
        n = 2 ** k
    return [vv[:min(n, len(vv))] for vv in v]

def TrainLeafNodes(h, g, y, NID, Label, debug=False):
    assert len(g) == len(y)
    assert len(g) == len(NID)
    return FormatLayer(h, g, NID, Label, debug=debug)

def GroupFirstOne(g, b):
    assert len(g) == len(b)
    s = GroupPrefixSum(g, b)
    return s * b == 1

class TreeTrainer:
    """ Decision tree training by `Hamada et al.`_

    :param x: sample data (by attribute, list or
      :py:obj:`~Compiler.types.Matrix`)
    :param y: binary labels (list or sint vector)
    :param h: height (int)
    :param binary: binary attributes instead of continuous
    :param attr_lengths: attribute description for mixed data
      (list of 0/1 for continuous/binary)
    :param n_threads: number of threads (default: single thread)

    .. _`Hamada et al.`: https://arxiv.org/abs/2112.12906

    """
    def GetInversePermutation(self, perm, n_threads=2):
        res = Array.create_from(self.identity_permutation)
        reveal_sort(perm, res)
        return res

    def ApplyTests(self, x, AID, Threshold):
        if self.debug:
            print_ln("# 1 Atrribute nos while applying tests: %s", util.reveal(AID))
        m = len(x)
        n = len(AID)
        assert len(AID) == len(Threshold)
        for xx in x:
            assert len(xx) == len(AID)
        e = sint.Matrix(m, n)

        @for_range_multithread(self.n_threads, 1, m)
        def _(j):
            e[j][:] = AID[:] == j
        xx = sum(x[j]*e[j] for j in range(m)) 

        if self.debug:
            print_ln("Atrribute nos while applying tests: %s", AID.reveal())
            print_ln("e, n m-length vectors: %s", e.reveal_nested())

        if self.debug:
            print_ln('LHS of ApplyTests = %s', util.reveal(xx))
            print_ln('Threshold %s', util.reveal(Threshold))
        return 2 * xx.get_vector() < Threshold.get_vector()
    
    def TestSelection(self, g, x, y, pis, notysum, ysum, time=False):
        for xx in x:
            assert(len(xx) == len(g))
        assert len(g) == len(y)
        m = len(x)
        n = len(y)
        gg = g
        u, t = [get_type(x).Matrix(m, n) for i in range(2)]
        v = get_type(y).Matrix(m, n)
        s_num = get_type(y).Matrix(m, n)
        s_den = get_type(y).Matrix(m, n)
        a = sint.Array(n)

        notysum_arr = Array.create_from(notysum)
        ysum_arr = Array.create_from(ysum)

        @for_range_multithread(self.n_threads, 1, m)
        def _(j):
            single = not self.n_threads or self.n_threads == 1
            time = self.time and single
            if self.debug_selection:
                print_ln('run %s', j)
            u[j].assign_vector(x[j])
            v[j].assign_vector(y)
            reveal_sort(pis[j], u[j])
            reveal_sort(pis[j], v[j])
            if self.debug:
                print_ln('x[j] = %s', util.reveal(x[j]))
                print_ln('u[j] = %s', util.reveal(u[j]))
            s_num[j][:], s_den[j][:], t[j][:] = ComputeGini(g, u[j], v[j], notysum_arr, ysum_arr, debug=False)

        if self.debug:
            print_ln("Gini Index numerator: %s", s_num.reveal_nested())
            print_ln("Gini Index denominator: %s", s_den.reveal_nested())
            print_ln("Threshold: %s", t.reveal_nested())
        ss_num, ss_den, tt, aa = VectMax((s_num[j][:] for j in range(m)), (s_den[j][:] for j in range(m)), (t[j][:] for j in range(m)), range(m), debug=self.debug)
        if self.debug:
            print_ln("Attributewise max for each sample --> Gini numerator: %s", util.reveal(ss_num))
            print_ln("Attributewise max for each sample --> Gini denominator: %s", util.reveal(ss_den))
            print_ln("Attributewise max for each sample --> Threshold: %s", util.reveal(tt))
            print_ln("Attributewise max for each sample --> Attrib no: %s", util.reveal(aa))

        aaa = get_type(y).Array(n)
        ttt = get_type(x).Array(n)

        GroupMax_num, GroupMax_den, GroupMax_ttt, GroupMax_aaa = GroupMax(g, ss_num, ss_den, tt, aa)

        if self.debug:
            print_ln("Groupwise max n-vector --> Gini numerator: %s", util.reveal(sss_num))
            print_ln("Groupwise max n-vector --> Gini denominator: %s", util.reveal(sss_den))
            print_ln("Groupwise max n-vector --> Threshold: %s", util.reveal(ttt))
            print_ln("Groupwise max n-vector --> Attrib no: %s", util.reveal(aaa))

        f = sint.Array(n)
        f = (self.zeros.get_vector() == notysum).bit_or(self.zeros.get_vector() == ysum)
        aaa_vector, ttt_vector = f.if_else(0, GroupMax_aaa), f.if_else(MIN_VALUE, GroupMax_ttt)

        ttt.assign_vector(ttt_vector)
        aaa.assign_vector(aaa_vector)

        if self.debug:
            print_ln('Final Test Selection attribute nos =%s', util.reveal(aaa))
            print_ln('Final Test Selection thresholds=%s', util.reveal(ttt))
        return aaa, ttt

    def SetupPerm(self, g, x, y):
        m = len(x)
        n = len(y)
        pis = get_type(y).Matrix(m, n)
        @for_range_multithread(self.n_threads, 1, m)
        def _(j):
            @if_e(self.attr_lengths[j])
            def _():
                pis[j][:] = self.GetInversePermutation(GetSortPerm([x[j]], x[j], y,
                                        n_bits=[1], time=time))
            @else_
            def _():
                pis[j][:] = self.GetInversePermutation(GetSortPerm([x[j]], x[j], y,
                                        n_bits=[None],
                                        time=time))
        return pis

    def UpdateState(self, g, x, y, pis, NID, b, k):
        m = len(x)
        n = len(y)
        q = SortPerm(b)
        
        y[:] = q.apply(y)
        if self.debug:
            print_ln("q: %s", q.perm.reveal())
        NID[:] = 2 ** k * b + NID
        NID[:] = q.apply(NID)
        if self.debug:
            print_ln('b_not=%s', b_not.reveal())
        g[:] = GroupFirstOne(g, b.bit_not()) + GroupFirstOne(g, b)
        g[:] = q.apply(g)

        b_arith = sint.Array(n)
        b_arith = Array.create_from(b)
        if self.debug:
            print_ln("b_arith: %s", util.reveal(b_arith))
        
        @for_range_multithread(self.n_threads, 1, m)
        def _(j):
            x[j][:] = q.apply(x[j])
            b_permuted = ApplyPermutation(pis[j], b_arith)
            
            pis[j] = q.apply(pis[j])
            pis[j] = ApplyInversePermutation(pis[j], SortPerm(b_permuted).perm)

            if self.debug:
                tmp2 = sint.Array(n)
                tmp2 = Array.create_from(x[j])
                reveal_sort(pis[j], tmp2)
                print_ln("Sorted x_new: %s", util.reveal(tmp2)) 
        
        return [g, x, y, NID, pis]

    @method_block
    def train_layer(self, k):
        g = self.g
        x = self.x
        y = self.y
        NID = self.NID
        pis = self.pis
        if self.debug:
            print_ln('g=%s', g.reveal())
            print_ln('y=%s', y.reveal())
            print_ln('x=%s', x.reveal_nested())
            print_ln('pis=%s', pis.reveal_nested())
            print_ln('NID=%s', NID.reveal())
        s0 = GroupSum(g, y.get_vector().bit_not())
        s1 = GroupSum(g, y.get_vector())
        if self.debug:
            print_ln('s=%s', s.reveal())
            print_ln('s0=%s', s0.reveal())
            print_ln('s1=%s', s1.reveal())
        a, t = self.TestSelection(g, x, y, pis, s0, s1)
        if self.debug:
            print_ln('Returned from Test Selection attribute nos =%s', util.reveal(a))
            print_ln('Returned from Test Selection thresholds=%s', util.reveal(t))
        b = self.ApplyTests(x, a, t)
        if self.debug:
            print_ln("Attribute nos: %s", util.reveal(a))
            print_ln("Thresholds: %s", util.reveal(t))
            print_ln("Classification results: %s", util.reveal(b))
        p = SortPerm(g.get_vector().bit_not())
        self.nids[k], self.aids[k], self.thresholds[k]= FormatLayer_without_crop(g[:], NID, a, t, debug=self.debug)

        if self.debug:
            print_ln('layer %s:', k)
            for name, data in zip(('NID', 'AID', 'Thr'),
                                  (self.nids[k], self.aids[k],
                                   self.thresholds[k])):
                print_ln(' %s: %s', name, data.reveal())

        @if_e(k < (len(self.nids)-1))
        def _():
            self.g, self.x, self.y, self.NID, self.pis = self.UpdateState(g, x, y, pis, NID, b, k)
        @else_
        def _():
            self.label = Array.create_from(s0 < s1)

    def __init__(self, x, y, h, binary=False, attr_lengths=None,
                 n_threads=None):
        assert not (binary and attr_lengths)
        if binary:
            attr_lengths = [1] * len(x)
        else:
            attr_lengths = attr_lengths or ([0] * len(x))
        for l in attr_lengths:
            assert l in (0, 1)
        self.attr_lengths = Array.create_from(regint(attr_lengths))
        Array.check_indices = False
        Matrix.disable_index_checks()
        for xx in x:
            assert len(xx) == len(y)
        m = len(x)
        n = len(y)
        self.g = sint.Array(n)
        self.g.assign_all(0)
        self.g[0] = 1
        self.NID = sint.Array(n)
        self.NID.assign_all(1)
        self.y = Array.create_from(y)
        self.x = Matrix.create_from(x)
        self.pis = sint.Matrix(m, n)
        self.nids, self.aids = [sint.Matrix(h, n) for i in range(2)]
        self.thresholds = self.x.value_type.Matrix(h, n)
        self.identity_permutation = sint.Array(n) 
        self.label = sintbit.Array(n)
        self.zeros = sint.Array(n)
        self.zeros.assign_all(0)
        self.n_threads = n_threads
        self.debug_selection = False
        self.debug_threading = True
        self.debug_gini = False
        self.debug_init = False
        self.debug_vectmax = False
        self.debug = False
        self.time = False

    def train(self):
        """ Train and return decision tree. """
        n = len(self.y)

        @for_range(n)
        def _(i):
            self.identity_permutation[i] = sint(i)

        if self.debug:
            print_ln("x: %s", x.reveal_nested())
            print_ln("y: %s", y.reveal())
            print_ln("g: %s", g.reveal())
            print_ln("NID: %s", NID.reveal())
        h = len(self.nids)

        self.pis = self.SetupPerm(self.g, self.x, self.y)
        if self.debug:
            tmp = get_type(x[0]).Array(len(x[0]))
            tmp.assign_vector(x[0])
            reveal_sort(pis[0], tmp)
            print_ln('Sorted x[0] = %s', util.reveal(tmp))
            print_ln('Sorting permutations based on attribs: %s', pis.reveal_nested())

        @for_range(h)
        def _(k):
            self.train_layer(k)
        return self.get_tree(h, self.label)

    def get_tree(self, h, Label):
        Layer = [None] * (h + 1)
        for k in range(h):
            Layer[k] = CropLayer(k, self.nids[k], self.aids[k],
                                 self.thresholds[k])
        Layer[h] = TrainLeafNodes(h, self.g[:], self.y[:], self.NID, Label, debug=self.debug)
        return Layer

def DecisionTreeTraining(x, y, h, binary=False):
    return TreeTrainer(x, y, h, binary=binary).train()

def output_decision_tree(layers):
    """ Print decision tree output by :py:class:`TreeTrainer`. """
    print_ln('full model %s', util.reveal(layers))
    for i, layer in enumerate(layers[:-1]):
        print_ln('level %s:', i)
        for j, x in enumerate(('NID', 'AID', 'Thr')):
            print_ln(' %s: %s', x, util.reveal(layer[j]))
    print_ln('leaves:')
    for j, x in enumerate(('NID', 'result')):
        print_ln(' %s: %s', x, util.reveal(layers[-1][j]))


class TreeClassifier:
    """ Tree classification with convenient interface. Uses
    :py:class:`TreeTrainer` internally.

    :param max_depth: the depth of the decision tree
    :param n_threads: number of threads used in training

    """
    def __init__(self, max_depth, n_threads=None):
        self.max_depth = max_depth
        self.n_threads = n_threads

    @staticmethod
    def get_attr_lengths(attr_types):
        if attr_types == None:
            return None
        else:
            return [1 if x == 'b' else 0 for x in attr_types]

    def fit(self, X, y, attr_types=None):
        """ Train tree.

        :param X: sample data with row-wise samples (sint/sfix matrix)
        :param y: binary labels (sint list/array)

        """
        self.tree = TreeTrainer(
            X.transpose(), y, self.max_depth,
            attr_lengths=self.get_attr_lengths(attr_types),
            n_threads=self.n_threads).train()

    def output(self):
        """ Output decision tree. """
        output_decision_tree(self.tree)
