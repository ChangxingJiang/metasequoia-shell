def update_dict(dict_1: dict, dict_2: dict) -> dict:
    """返回 dict_1.update(dict_2) 的结果，但保持 dict_1 不变"""
    dict_1_copy = dict_1.copy()
    dict_1_copy.update(dict_2)
    return dict_1_copy
