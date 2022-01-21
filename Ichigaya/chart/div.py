from .key import Single, Flick, Direct, Hold, directionalNote



def div_stateI(keys, simos, rp = False): 
    def set_hand_from_item(item, hand):
        if item[0] == Single: 
            keys["Single"][item[-1]].set_hand(hand)
        elif item[0] == Flick: 
            keys["Flick"][item[-1]].set_hand(hand)
        elif item[0] == Direct: 
            keys["Direct"][item[-1]].set_hand(hand)
        else: 
            keys["Hold"][item[-1]].set_hand(hand)
    for simo in simos: 
        set_hand_from_item(simo.obj1, "Left")
        set_hand_from_item(simo.obj2, "Right")
    if rp: div_result_reporter(keys, "指法分析阶段一进度：")
    return div_result_wrapper(keys)

def div_stateII(keys, rp = False): 
    for h, hold in enumerate(keys["Hold"]): 
        for s, single in enumerate(keys["Single"]): 
            if single.hand is not None: continue
            if single.beat < hold.touch.beat: continue
            if single.beat > hold.release.beat: break
            if single.lane < hold.f_lane(single.beat): 
                keys["Single"][s].set_hand("Left"), keys["Hold"][h].set_hand("Right")
            else: 
                keys["Single"][s].set_hand("Right"), keys["Hold"][h].set_hand("Left")
        
        for s, single in enumerate(keys["Flick"]): 
            if single.hand is not None: continue
            if single.beat < hold.touch.beat: continue
            if single.beat > hold.release.beat: break
            if single.lane < hold.f_lane(single.beat): 
                keys["Flick"][s].set_hand("Left"), keys["Hold"][h].set_hand("Right")
            else: 
                keys["Flick"][s].set_hand("Right"), keys["Hold"][h].set_hand("Left")
        
        for s, single in enumerate(keys["Direct"]): 
            if single.hand is not None: continue
            if single.beat < hold.touch.beat: continue
            if single.beat > hold.release.beat: break
            if single.lane < hold.f_lane(single.beat): 
                keys["Direct"][s].set_hand("Left"), keys["Hold"][h].set_hand("Right")
            else: 
                keys["Direct"][s].set_hand("Right"), keys["Hold"][h].set_hand("Left")
    if rp: div_result_reporter(keys, "指法分析阶段二进度：")
    return div_result_wrapper(keys)



def div_stateIII(keys, rp = False): 
    rest_list = []
    for t, l in keys.items(): 
        for i, k in enumerate(l): 
            if isinstance(k, directionalNote) and k.hand is None: 
                rest_list.append([t, i, k.beat, k.lane, None])
    rest_list = sorted(rest_list, key = lambda rinfo: rinfo[2])

    rest_group = [[rest_list[0]]]
    for r in rest_list[1: ]: 
        if (r[1] - rest_group[-1][-1][1] == 1 or r[0] != "Single" or rest_group[-1][-1][0] != "Single") and r[2] - rest_group[-1][-1][2] < .4: 
            rest_group[-1].append(r)
        else: 
            if len(rest_group[-1]) < 3: 
                rest_group.pop(-1)
            rest_group.append([r])
    
    rest_cross = []
    for g in rest_group: 
        n = 0
        for i in range(len(g) - 2): 
            if abs(g[i][2] + g[i + 2][2] - 2 * g[i + 1][2]) > 1e-3 or (g[i + 2][3] - g[i + 1][3]) * (g[i + 1][3] - g[i][3]) > 1e-5: 
                continue
            if i < n: continue
            j = i + 1
            while j < len(g) - 2: 
                if abs(g[j][2] + g[j + 2][2] - 2 * g[j + 1][2]) > 1e-3 or  (g[j + 2][3] - g[j + 1][3]) * (g[j + 1][3] - g[j][3]) > 1e-5: 
                    break
                j += 1
            rest_cross.append(g[i : j + 2])
            n = j + 2
    
    rest_cross2 = []
    for g in rest_cross: 
        n = 0
        for i in range(len(g) - 2): 
            if (g[i + 2][3] - g[i + 1][3]) * (g[i + 1][3] - g[i][3]) >= 0: 
                continue
            if (g[i + 2][3] - g[i + 1][3]) * (g[i + 1][3] - g[i][3]) == 0 and g[i + 2][3] - g[i][3] != 0 : 
                continue
            if i < n: continue
            c = 1 if g[i + 1][3] >= g[i][3] else 0
            j = i + 2
            while j < len(g) - 1: 
                if (c + j - i) % 2 == 0 and g[j + 1][3] > g[j][3]: 
                    break
                if (c + j - i) % 2 == 1 and g[j + 1][3] < g[j][3]: 
                    break
                j += 1
            rest_cross2.append(g[i : j + 1])
            n = j + 1
    
    for g in rest_cross2: 
        if g[1][3] > g[0][3]: 
            keys[g[0][0]][g[0][1]].set_hand("Left")
        else:
            keys[g[0][0]][g[0][1]].set_hand("Right")
            g[0][-1] = "Right"
        for i in range(1, len(g)): 
            keys[g[i][0]][g[i][1]].set_hand("Right" if keys[g[i - 1][0]][g[i - 1][1]].hand == "Left" else "Left")

    if rp: div_result_reporter(keys, "指法分析阶段三进度：")
    return div_result_wrapper(keys)

def div_stateIV(keys, rp = False): 
    for s, single in enumerate(keys["Single"]): 
        if single.lane == 0: 
            keys["Single"][s].set_hand("Left")
            continue
        if single.lane == 6: 
            keys["Single"][s].set_hand("Right")
            continue

    for s, single in enumerate(keys["Flick"]): 
        if single.lane == 0: 
            keys["Flick"][s].set_hand("Left")
            continue
        if single.lane == 6: 
            keys["Flick"][s].set_hand("Right")
            continue

    for s, single in enumerate(keys["Direct"]): 
        if single.lane == 0: 
            keys["Direct"][s].set_hand("Left")
            continue
        if single.lane == 6: 
            keys["Direct"][s].set_hand("Right")
            continue
    for h, hold in enumerate(keys["Hold"]): 
        if hold.touch.hand is not None: continue
        if min([s.lane for s in [hold.touch] + hold.slides + [hold.release]]) == 0:
            if max([s.lane for s in [hold.touch] + hold.slides + [hold.release]]) == 6: 
                continue
            else:
                keys["Hold"][h].set_hand("Left")
        if max([s.lane for s in [hold.touch] + hold.slides + [hold.release]]) == 6:
            keys["Hold"][h].set_hand("Right")
    if rp: div_result_reporter(keys, "指法分析阶段四进度：")
    return div_result_wrapper(keys)





def div_stateV(keys, rp = False): 

    fx = lambda b: (60 * b ** 2 - 1.75) * (- b ** 2 / 4 + 1) / (100 * b ** 4 + 1)
    c_l = lambda b, l, h: min(max((fx(b if h else -b) - l), -1), 1)
    c_b = lambda b: max(1 - b * 4 if b > 0 else 4 * b + 1, 0)
    cost = lambda b, l, h: c_l(b, l, h) * c_b(b)



    def single_cost(s, b, l, h = None): 
        assert isinstance(s, directionalNote)
        if h is None: 
            assert s.hand is not None
            h = s.hand
        if abs(s.beat - b) > 1: 
            return 0
        return cost(b - s.beat, l - s.lane, h == "Left")

    def hold_cost(h: Hold, b, l, hand = None): 
        return single_cost(h.touch, b, l, hand) + single_cost(h.release, b, l, hand)
    


    rest_list = []
    for t, l in keys.items(): 
        for i, k in enumerate(l): 
            if (k.hand if isinstance(k, directionalNote) else k.touch.hand) is None: 
                rest_list.append([t, i, 0, 0, None, None])

    for rinfo in rest_list: 
        rnote = keys[rinfo[0]][rinfo[1]] 
        rnote = rnote if isinstance(rnote, directionalNote) else rnote.touch
        for fnote in keys["Single"] + keys["Hold"] + keys["Flick"] + keys["Direct"]: 
            if (fnote.hand if isinstance(fnote, directionalNote) else fnote.touch.hand) is None: continue
            rinfo[2] += single_cost(fnote, rnote.beat, rnote.lane) if isinstance(fnote, directionalNote) else hold_cost(fnote, rnote.beat, rnote.lane)
        rinfo[2] += (3 - rnote.lane) * .01

    for rinfo in rest_list: 
        rnote = keys[rinfo[0]][rinfo[1]]
        rinfo[5] = "Left" if  rinfo[2] + rinfo[3] > 0 else "Right"
    


    flag = True
    c = 0
    while flag and c <= 100: 

        for i, rinfo in enumerate(rest_list): 
            rinfo[3] = 0
            rnote = keys[rinfo[0]][rinfo[1]] 
            rnote = rnote if isinstance(rnote, directionalNote) else rnote.touch
            for j, _rinfo in enumerate(rest_list): 
                if i == j: continue
                _rnote = keys[_rinfo[0]][_rinfo[1]]
                rinfo[3] += single_cost(_rnote, rnote.beat, rnote.lane, _rinfo[5]) if isinstance(_rnote, directionalNote) else hold_cost(_rnote, rnote.beat, rnote.lane, _rinfo[5])

        flag = False
        for rinfo in rest_list: 
            rnote = keys[rinfo[0]][rinfo[1]] 
            rnote = rnote if isinstance(rnote, directionalNote) else rnote.touch
            rinfo[4] = "Left" if  rinfo[2] + rinfo[3] > 0 else "Right"
            if rinfo[4] != rinfo[5]: 
                rinfo[5] = rinfo[4]
                flag = True
        
        c += 1
    
    if rp: print("在%i轮迭代后，指法分析阶段五完成。" %(c))
    for rinfo in rest_list: 
        keys[rinfo[0]][rinfo[1]].set_hand(rinfo[-1])
    return div_result_wrapper(keys)





div_states = [div_stateI, div_stateII, div_stateIII, div_stateIV, div_stateV]

def div(keys, simos, states = range(1, 6), rp = False): 
    for s in states: 
        if s == 1: 
            keys = div_result_setter(keys, 
                div_states[0](keys, simos, rp))
        else: 
            keys = div_result_setter(keys, 
                div_states[s - 1](keys, rp))
    return div_result_wrapper(keys)






def div_result_wrapper(keys): 
    return {
        "Single": [s.hand for s in keys["Single"]], 
        "Flick": [f.hand for f in keys["Flick"]], 
        "Direct": [d.hand for d in keys["Direct"]], 
        "Hold": [h.touch.hand for h in keys["Hold"]]}

def div_result_setter(keys, wrp): 
    for i in range(len(keys["Single"])): 
        keys["Single"][i].set_hand(wrp["Single"][i])
    for i in range(len(keys["Flick"])): 
        keys["Flick"][i].set_hand(wrp["Flick"][i])
    for i in range(len(keys["Direct"])): 
        keys["Direct"][i].set_hand(wrp["Direct"][i])
    for i in range(len(keys["Hold"])): 
        keys["Hold"][i].set_hand(wrp["Hold"][i])
    return keys

def div_result_reporter(keys, tag): 
    s = sum(1 for k in keys["Single"] if k.hand is not None)
    f = sum(1 for k in keys["Flick"] if k.hand is not None)
    d = sum(1 for k in keys["Direct"] if k.hand is not None)
    h = sum(1 for k in keys["Hold"] if k.touch.hand is not None)
    a = sum(len(c) for c in keys.values())
    print(tag)
    print("总完成率：%.2f%%\t（%i/%i）" %(
        (s + f + d + h) / a * 100, s + f + d + h, a))
    if len(keys["Single"]) > 0: 
        print("单键：\t%.2f%%\t（%i/%i）" %(
            s / len(keys["Single"]) * 100, s, len(keys["Single"])))
    if len(keys["Flick"]) > 0: 
        print("滑键：\t%.2f%%\t（%i/%i）" %(
            f / len(keys["Flick"]) * 100, f, len(keys["Flick"])))
    if len(keys["Direct"]) > 0: 
        print("方向键：\t%.2f%%\t（%i/%i）" %(
            d / len(keys["Direct"]) * 100, d, len(keys["Direct"])))
    if len(keys["Hold"]) > 0: 
        print("长键：\t%.2f%%\t（%i/%i）" %(
            h / len(keys["Hold"]) * 100, h, len(keys["Hold"])))