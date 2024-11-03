def process_url(original_url):
    if original_url.startswith("https://2gis.ru/"):
        question_mark_index = original_url.find("?")
        
        if question_mark_index != -1:
            return original_url[:question_mark_index] + "/tab/reviews"

        return original_url + "/tab/reviews"
    
    elif original_url.startswith("https://yandex.ru/maps/"):
        question_mark_index = original_url.find("?")
        
        if question_mark_index != -1:
            return original_url[:question_mark_index] + "reviews"

        return original_url + "reviews"
    
    return None
