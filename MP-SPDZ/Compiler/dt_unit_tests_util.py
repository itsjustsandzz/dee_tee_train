def SingleGroupSort_plain (x_plain, y_plain):
    n = len(x_plain)
    zipped_x_y = zip (x_plain, y_plain)
    sorted_x_y = sorted(zipped_x_y)
    tuples = zip(*sorted_x_y)
    sorted_x_plain, sorted_y_plain = [ list(tuple) for tuple in tuples ]
    return sorted_x_plain, sorted_y_plain

def GroupWiseSort_plain (g_plain, x_plain, y_plain):
    n = len(y_plain)
    sorted_x_plain = []
    sorted_y_plain = []
    start_ind = 0
    end_ind = 1
    for i in range(n):
        if g_plain[i] == 1:
            start_ind = i
        if g_plain[i+1] == 1:
            end_ind = i + 1
            returned_x_plain, returned_y_plain = SingleGroupSort_plain (x_plain[start_ind:end_ind], y_plain[start_ind:end_ind])
            sorted_x_plain += returned_x_plain
            sorted_y_plain += returned_y_plain
    return sorted_x_plain, sorted_y_plain

def GroupMax_plain (g_plain, p_plain, q_plain, t_plain, a_plain):
    ans_p = []
    ans_q = []
    ans_t = []
    ans_a = []
    for i in range(len(p_plain)):
        if g_plain[i] == 1:
            max_p = -1000000
            max_q = 1
        if (p_plain[i] / q_plain[i]) > (max_p / max_q):
            max_p = p_plain[i]
            max_q = q_plain[i]
            max_t = t_plain[i]
            max_a = a_plain[i]
        ans_p.append(max_p)
        ans_q.append(max_q)
        ans_t.append(max_t)
        ans_a.append(max_a)
    for i in range(len(g_plain)-2, -1, -1):
        if g_plain[i+1] == 0:
            ans_p[i] = ans_p[i+1]      
            ans_q[i] = ans_q[i+1]
            ans_t[i] = ans_t[i+1]
            ans_a[i] = ans_a[i+1]
    return ans_p, ans_q, ans_t, ans_a 

def VectMax_plain (p_plain, q_plain, t_plain, a_plain):
    custom_g = [0]*len(p_plain)
    custom_g[0] = 1
    ans_p, ans_q, ans_t, ans_a = GroupMax_plain (custom_g, p_plain, q_plain, t_plain, a_plain)
    return ans_p[0], ans_q[0], ans_t[0], ans_a[0]

def GroupSum_plain (g_plain, x_plain):
    ans = []
    sum_so_far = 0
    for i in range(len(x_plain)):
        if g_plain[i] == 1:
            sum_so_far = x_plain[i]
        else:
            sum_so_far = sum_so_far + x_plain[i]
        ans.append(sum_so_far)
    for i in range(len(g_plain)-2, -1, -1):
        if g_plain[i+1] == 0:
            ans[i] = ans[i+1]
    return ans

def GroupPrefixSum_plain (g_plain, x_plain):
    ans = []
    sum_so_far = 0
    for i in range(len(x_plain)):
        if g_plain[i] == 1:
            sum_so_far = x_plain[i]
        else:
            sum_so_far = sum_so_far + x_plain[i]
        ans.append(sum_so_far)
    return ans

def ComputeGiniSingleGroup_plain (x_plain, y_plain):
    n = len(x_plain)
    
    tot_y0 = 0
    tot_y1 = 0

    for y_ele in y_plain:
        if y_ele == 0:
            tot_y0 = tot_y0 + 1
        elif y_ele == 1:
            tot_y1 = tot_y1 + 1

    y0 = 0
    y1 = 0
    numerator = [None]*n
    denominator = [None]*n
    threshold = [None]*n
    MIN_VALUE = -10000
    for i in range(n - 1):
        if y_plain[i] == 0:
            y0 = y0 + 1
        else:
            y1 = y1 + 1
        if x_plain[i] == x_plain[i+1]:
            numerator[i]= MIN_VALUE
            denominator[i]= 1
            threshold[i]= MIN_VALUE
        else:
            numerator[i] = (n-i-1)*(y0**2 + y1**2) + (i+1)*( (tot_y0 - y0)**2 + (tot_y1 - y1)**2 )
            denominator[i] = (n-i-1)*(i+1)
            threshold[i]= x_plain[i] + x_plain[i+1]
    numerator[n-1]= MIN_VALUE
    denominator[n-1] = 1
    threshold[n-1] = MIN_VALUE
    return numerator, denominator, threshold

def ComputeGini_plain (g_plain, x_plain, y_plain):
    n = len(x_plain)

    gini_num = []
    gini_den = []
    gini_threshold = []
    start_ind = 0
    end_ind = 1
    for i in range(n):
        if g_plain[i] == 1:
            start_ind = i
        if g_plain[i+1] == 1:
            end_ind = i + 1
            returned_num, returned_den, returned_threshold = ComputeGiniSingleGroup_plain (x_plain[start_ind:end_ind], y_plain[start_ind:end_ind])
            gini_num += returned_num
            gini_den += returned_den
            gini_threshold += returned_threshold

    return gini_num, gini_den, gini_threshold

def GroupFirstOne_plain (g_plain, y_plain):
    res = []
    for i in range(len(y_plain)):
        if g_plain[i] == 1:
            start_ind = i
            end_ind = -1
        if y_plain[i] == 1 and end_ind == -1:
            res.append(1)
            end_ind = i
        else:
            res.append(0)
    return res

def Custom_GT_Fractions_plain (p_plain, q_plain, r_plain, s_plain):
    res = []
    for i in range(len(p_plain)):
        if p_plain[i]/q_plain[i] > r_plain[i]/s_plain[i]:
            res.append(1)
        else:
            res.append(0)
    return res

def OneHotEnc_plain (i, m):
    res = [0]*m
    res[i] = 1
    return res

def PermApply (pi_plain, v_plain):
    n = len(v_plain)
    res = [None]*n
    for i in range(n):
        res[pi_plain[i]] = v_plain[i]
    return res

def PermInv (p_plain):
    inverse = [0] * len(p_plain)
    for i, p_plain_i in enumerate(p_plain):
        inverse[p_plain_i] = i
    return inverse

def GetSortPermSingleGroup_plain (offset, v_plain):
    V = [ (v_plain[i], i) for i in range(len(v_plain)) ]
    V.sort()
    sorted_v_plain, permutation = zip(*V)
    permutation = [permutation[i] + offset for i in range(len(permutation))]
    return permutation

def GetSortPerm_plain (g_plain, v_plain):
    permutation = []
    start_ind = 0
    end_ind = 1
    n = len(v_plain)
    for i in range(n):
        if g_plain[i] == 1:
            start_ind = i
        if g_plain[i+1] == 1:
            end_ind = i + 1
            permutation += GetSortPermSingleGroup_plain (start_ind, v_plain[start_ind:end_ind])
    return permutation

def TestSelection_plain (g_plain, x_plain, y_plain, pis_plain, ones_plain, notysum_plain, ysum_plain):
    m = len(x_plain)
    n = len(y_plain)
    gini_num = []
    gini_den = []
    gini_threshold = []
    for i in range(m):
        sorted_x_plain = PermApply(PermInv(pis_plain[i]), x_plain[i])
        sorted_y_plain = PermApply(PermInv(pis_plain[i]), y_plain)

        num, den, thresh = ComputeGini_plain (g_plain, sorted_x_plain, sorted_y_plain)

        gini_num.append(num)
        gini_den.append(den)
        gini_threshold.append(thresh)

    transposed_gini_num_tuples = list(zip(*gini_num))
    transposed_gini_num = [list(sublist) for sublist in transposed_gini_num_tuples]

    transposed_gini_den_tuples = list(zip(*gini_den))
    transposed_gini_den = [list(sublist) for sublist in transposed_gini_den_tuples]

    transposed_gini_threshold_tuples = list(zip(*gini_threshold))
    transposed_gini_threshold = [list(sublist) for sublist in transposed_gini_threshold_tuples]

    gini_num_attrib_max = []
    gini_den_attrib_max = []
    gini_threshold_attrib_max = []
    gini_attrib_max = []
    for i in range(n):
        num_max, den_max, threshold_max, attrib_max = VectMax_plain (transposed_gini_num[i], transposed_gini_den[i], transposed_gini_threshold[i], list(range(0, m)))

        gini_num_attrib_max.append(num_max)
        gini_den_attrib_max.append(den_max)
        gini_threshold_attrib_max.append(threshold_max)
        gini_attrib_max.append(attrib_max)

    gini_num_max, gini_den_max, gini_threshold_max, gini_a_max = GroupMax_plain (g_plain, gini_num_attrib_max, gini_den_attrib_max, gini_threshold_attrib_max, gini_attrib_max)

    f_plain = []
    aaa_plain = []
    ttt_plain = []
    for i in range(n):
        f_plain.append ((ones_plain[i] == notysum_plain[i]) or (ones_plain[i] == ysum_plain[i]))
        if f_plain[i]:
            aaa_plain.append(0)
            ttt_plain.append(-10000)
        else:
            aaa_plain.append(gini_a_max[i])
            ttt_plain.append(gini_threshold_max[i])
    return aaa_plain, ttt_plain

def ApplyTests_plain (x_plain, AID_plain, Threshold_plain):
    m = len(x_plain)
    n = len(AID_plain)
    res = []
    for i in range(n):
        res.append(int(2*x_plain[AID_plain[i]][i] < Threshold_plain[i]))
    return res

def UpdateState_plain (g_plain, x_plain, y_plain, pis_plain, NID_plain, b_plain, k_plain):
    m = len(x_plain)
    n = len(y_plain)
    q = GetSortPermSingleGroup_plain (0, b_plain)
    q = PermInv(q)
    for j in range(m):
        x_plain[j] = PermApply (q, x_plain[j])
    y_plain = PermApply (q, y_plain)
    b_plain_times_2_k = [ (2**k_plain)*b_plain[i] for i in range(len(b_plain)) ]
    NID_plain = [ NID_plain[i] + b_plain_times_2_k[i] for i in range(len(NID_plain))]
    NID_plain = PermApply (q, NID_plain)
    b_plain_not = [ 1-b_plain[i] for i in range(len(b_plain)) ]
    group_first_b_plain_not = GroupFirstOne_plain (g_plain, b_plain_not)
    group_first_b_plain = GroupFirstOne_plain (g_plain, b_plain)
    g_plain = [group_first_b_plain_not[i] +  group_first_b_plain[i] for i in range(len(b_plain))]
    g_plain = PermApply (q, g_plain)

    pis_plain_inv = []
    for j in range(m):
        pis_plain_inv.append(PermInv(pis_plain[j]))
    
    q_new = []
    for j in range(m):
        q_new.append(PermApply(q, pis_plain_inv[j]))

    num_list = list(range(0, n))
    new_pis = []
    for j in range(m):
        b_copy = PermApply(pis_plain_inv[j], b_plain)
        r = GetSortPermSingleGroup_plain (0, b_copy)
        r = PermInv(r)
        r_copy = PermApply(PermInv(q_new[j]), r)
        new_pis.append(PermApply(r_copy, num_list))
    updated_state = [g_plain, x_plain, y_plain, new_pis, NID_plain]
    return updated_state

