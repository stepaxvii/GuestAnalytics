
def get_star_rating(rating):
    """Функция для генерации звездного рейтинга."""

    full_stars = "★★★★★"
    empty_stars = "☆☆☆☆☆"

    # Количество полных звёзд
    full_star_count = int(rating)

    # Разница между 5 и количеством полных звёзд
    empty_star_count = 5 - full_star_count

    # Формируем рейтинг: полные звезды и пустые звезды
    return full_stars[:full_star_count] + empty_stars[:empty_star_count]
