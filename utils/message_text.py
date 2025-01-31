
def get_star_rating(rating):
    """Функция для генерации звездного рейтинга с дополнительными символами."""

    full_stars = "★★★★★"
    empty_stars = "☆☆☆☆☆"

    # Количество полных звёзд
    full_star_count = int(rating)

    # Разница между 5 и количеством полных звёзд
    empty_star_count = 5 - full_star_count

    # Формируем рейтинг: полные звезды и пустые звезды
    star_rating = full_stars[:full_star_count] + empty_stars[:empty_star_count]

    # Добавляем дополнительные символы в зависимости от рейтинга
    if full_star_count == 3:
        star_rating = " 🚩" + star_rating
    elif full_star_count < 3:
        star_rating = "🚨" + star_rating + "🚨"

    return star_rating
