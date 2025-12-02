#  ____  _           _ _            _ _
# / ___|(_)_ __ ___ (_) | __ _ _ __(_) |_ _   _
# \___ \| | '_ ` _ \| | |/ _` | '__| | __| | | |
#  ___) | | | | | | | | | (_| | |  | | |_| |_| |
# |____/|_|_| |_| |_|_|_|\__,_|_|  |_|\__|\__, |
#                                         |___/
#

import typing
import difflib


def str_sim(a: typing.Optional[str], b: typing.Optional[str]) -> float:
    """
    字符串相似度 [0, 1]
    - 优先保证空值安全
    - 用 SequenceMatcher 比较（和 diff 一样）
    """

    if not a or not b:
        return 0.0

    return difflib.SequenceMatcher(None, a, b).ratio()


def iou(box1: typing.Optional[list], box2: typing.Optional[list]) -> float:
    """
    计算两个 bounds 的 IoU:
    bounds = [left, top, right, bottom]
    """

    if not box1 or not box2:
        return 0.0

    left1, top1, right1, bottom1 = box1
    left2, top2, right2, bottom2 = box2

    inter_left   = max(left1, left2)
    inter_top    = max(top1, top2)
    inter_right  = min(right1, right2)
    inter_bottom = min(bottom1, bottom2)

    inter_width  = max(0, inter_right - inter_left)
    inter_height = max(0, inter_bottom - inter_top)
    intersection = inter_width * inter_height

    area1 = abs((right1 - left1) * (bottom1 - top1))
    area2 = abs((right2 - left2) * (bottom2 - top2))

    if area1 <= 0 or area2 <= 0:
        return 0.0

    union = area1 + area2 - intersection

    return intersection / union if union > 0 else 0.0


if __name__ == '__main__':
    pass


