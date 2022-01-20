import numpy as np

# north-west angle
def nwa(c, a, b):
    d = np.zeros(c.shape)
    is_base = np.zeros(c.shape, dtype=bool)
    i, j = 0, 0
    n = c.shape[0]
    m = c.shape[1]
    a_tmp = np.copy(a)
    b_tmp = np.copy(b)
    while i< n and j < m:
        is_base[i, j] = True
        if a_tmp[i] > b_tmp[j]:
            d[i, j] = b_tmp[j]
            a_tmp[i] -= b_tmp[j]
            j += 1
        else:
            d[i, j] = a_tmp[i]
            b_tmp[j] -= a_tmp[i]
            i += 1
    return d, is_base

def find_beta(base, is_base, k_list, alpha, beta):
    for k in k_list:
        beta[is_base[k]] = base[k, is_base[k]] - alpha[k]
        k_list_next = [k for k, j in enumerate(is_base[k]) if j]
        is_base[k] = False
        if k_list_next:
            alpha, beta, is_base = find_alpha(base, is_base, k_list_next, alpha, beta)
    return alpha, beta, is_base

def find_alpha(base, is_base, k_list, alpha, beta):
    for k in k_list:
        alpha[is_base[:,k]] = base[is_base[:,k], k] - beta[k]
        k_list_next = [k for k, j in enumerate(is_base[:, k]) if j]
        is_base[:, k] = False
        if k_list_next:
            alpha, beta, is_base = find_beta(base, is_base, k_list_next, alpha, beta)
    return alpha, beta, is_base


def traffic(c, d, is_base):
    alpha = np.zeros(c.shape[0])
    beta = np.zeros(c.shape[1])
    k = 0
    while np.count_nonzero(is_base) < (c.shape[0]+c.shape[1]-1):
        x, y = false_var_place_search(is_base)
        d[x, y] = 0.0000001
        is_base[x, y] = True
    alpha, beta, _ = find_beta(c, np.copy(is_base), [k], alpha, beta)
    d_ = np.where(abs(d - 0)<0.0000000001, alpha[:, np.newaxis]+beta[np.newaxis, :], d)
    pivot = d_ - c > 0
    pivot[is_base] = False
    cycles = []
    measures = []
    for i in range(c.shape[0]):
        for j in range(c.shape[1]):
            if pivot[i,j]:
                cycles += cycle_search([(i, j)], is_base)

    for p in range(len(cycles)):
        x = [i for (i, j) in cycles[p]]
        y = [j for (i, j) in cycles[p]]
        m = min(d[x[1::2], y[1::2]])
        me = (c[x[0], y[0]] - d_[x[0], y[0]])*m
        measures.append(me)
    cycles_ = []
    if cycles:
        cycles_ = cycle_intersect(cycles, measures)
    for i in cycles_:
        d, is_base = use_cycle(i, d, is_base)
    return d, is_base, pivot


def use_cycle(cycle, d, is_base):
    x = [i for (i, j) in cycle]
    y = [j for (i, j) in cycle]
    m = min(d[x[1::2], y[1::2]])
    d[x[1::2], y[1::2]] -= m
    d[x[0::2], y[0::2]] += m
    is_base[x[0], y[0]] = True
    is_base = np.where(d== 0, False, True)
    return d, is_base


def false_var_place_search(is_base):
    # find first base
    x, y = np.where(is_base)
    bases = zip(list(x), list(y))
    # find reachable bases
    reachable = find_reach([(x[0], y[0])], x[0], y[0], is_base)
    non_reach = [i for i in bases if i not in reachable]
    if non_reach:
        return 0, non_reach[0][1]
    else:
        for i in range(is_base.shape[0]):
            if not is_base[i].any():
                return i, 0
        for j in range(is_base.shape[1]):
            if not is_base[:, j].any():
                return 0, j
        


def cycle_intersect(cycles, measures):
    inter = np.zeros((len(cycles), len(cycles)+1))
    for i in range(len(cycles)):
        for j in range(len(cycles)):
            if [value for value in cycles[i] if value in cycles[j]]:
                inter[i, j] = 0
            else:
                inter[i, j] = measures[i] + measures[j]
        inter[i, len(cycles)] = measures[i]
    i, j = np.where(inter == np.min(inter))
    if j[0] == len(cycles):
        return [cycles[i[0]]]
    else:
        return [cycles[i[0]], cycles[j[0]]]



def find_reach(reach_list, x, y, is_base):
    
    new_reach_list = [(x, i) for (i, b) in enumerate(is_base[x]) if b and (x, i) not in reach_list]
    new_reach_list += [(j, y) for (j, b) in enumerate(is_base[:, y]) if b and (j, y) not in reach_list]
    reach_list += new_reach_list
    for (i, j) in new_reach_list:
        reach_list += find_reach(reach_list, i, j, is_base)
    return reach_list


def cycle_search(path, is_base):
    start_x = path[-1][0]
    start_y = path[-1][1]
    bases = []
    bases = []
   
    if len(path) > 2:
        if path[0][0] == start_x:
            return [path]
        elif path[0][1] == start_y:
            return [path]
 

    if len(path) > 1:
        if path[-2][0] == path[-1][0]:
            for i in range(is_base.shape[0]):
                if is_base[i, start_y]:
                    bases.append((i, start_y))
        elif path[-2][1] == path[-1][1]:
            for j in range(is_base.shape[1]):
                if is_base[start_x, j]:
                    bases.append((start_x, j))
        bases = [(i, j) for (i, j) in bases 
                if (i, j) not in path]
    else:
        for i in range(is_base.shape[0]):
            if is_base[i, start_y]:
                bases.append((i, start_y))


    alternatives = []
    for b in bases:
        path.append(b)
        alt = cycle_search(path.copy(), is_base)
        path.pop()
        if alt:
            alternatives += alt
    return alternatives



