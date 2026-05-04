"""
间隔重复算法 (SM-2 适配版，三档评分)

评级:
  - familiar  (熟悉)   → EF 微增，间隔正常增长
  - unsure    (不熟悉) → EF 略降，间隔微增
  - forgot    (忘记了) → EF 大幅降，间隔重置为 1 天

SM-2 公式:
  EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
  其中 q 是 0-5 的评分

将三档映射到 SM-2 q 值:
  familiar → q = 5  (完美)
  unsure   → q = 3  (困难)
  forgot   → q = 0  (失败)
"""

from datetime import datetime, timedelta

MIN_EF = 1.3
MAX_EF = 3.0
INITIAL_INTERVAL = 1  # 天


def sm2_q(rating: str) -> int:
    mapping = {
        'familiar': 5,
        'unsure': 3,
        'forgot': 0,
    }
    return mapping.get(rating, 3)


def calculate(ease_factor: float, interval_days: int, rating: str):
    q = sm2_q(rating)

    # 计算新的 EF
    new_ef = ease_factor + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
    new_ef = max(MIN_EF, min(MAX_EF, new_ef))

    # 计算新间隔
    if q < 3:
        # 忘记了 → 重置为 1 天
        new_interval = 1
    elif q == 3:
        # 不熟悉 → 间隔不变或微增
        if interval_days == 0:
            new_interval = 1
        elif interval_days == 1:
            new_interval = 2
        else:
            new_interval = max(1, int(interval_days * 1.2))
    else:
        # 熟悉 → 正常 SM-2 间隔增长
        if interval_days == 0:
            new_interval = 1
        elif interval_days == 1:
            new_interval = 3
        else:
            new_interval = int(interval_days * new_ef)

    next_review = datetime.now() + timedelta(days=new_interval)

    return {
        'ease_factor': round(new_ef, 2),
        'interval_days': new_interval,
        'next_review_at': next_review,
    }
