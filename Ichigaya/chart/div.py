from .key import Single, Flick, Direct, Hold, directionalNote


def div_stateI(keys, simos): 

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
    

    s = sum(1 for k in keys["Single"] if k.hand is not None)
    f = sum(1 for k in keys["Flick"] if k.hand is not None)
    d = sum(1 for k in keys["Direct"] if k.hand is not None)
    h = sum(1 for k in keys["Hold"] if k.touch.hand is not None)
    a = sum(len(c) for c in keys.values())
    print("指法分析阶段一进度：")
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

    return {
        "Single": [s.hand for s in keys["Single"]], 
        "Flick": [f.hand for f in keys["Flick"]], 
        "Direct": [d.hand for d in keys["Direct"]], 
        "Hold": [h.touch.hand for h in keys["Hold"]]}





def div_stateII(keys): 

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
    
    print("在%i轮迭代后，指法分析阶段二完成。" %(c))
    return [(rinfo[0], rinfo[1], rinfo[-1]) for rinfo in rest_list]