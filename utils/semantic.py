"""
Модуль фич и вспомогательных функций для скмантического анализа.
"""


def make_count_insights(review_block: dict) -> int:
    """
    Функция для подсчёта необходимого количества инсайтов,
    исходя из количества отзывов.
    """
    count_reviews = len(review_block)

    if count_reviews > 20:
        insights = 10
    elif 10 <= count_reviews <= 20:
        insights = 5
    elif 5 <= count_reviews < 10:
        insights = 3
    elif 1 < count_reviews < 5:
        insights = 2
    elif count_reviews == 1:
        insights = 1
    else:
        insights = 0

    return insights
