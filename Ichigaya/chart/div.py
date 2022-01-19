from .key import Single, Flick, Direct, Hold


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