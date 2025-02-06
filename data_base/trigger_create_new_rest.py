import logging
from sqlalchemy import event
from yandex.yandex_primary_collection import ya_prim_coll

from data_base.data_main import Restaurant

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@event.listens_for(Restaurant, 'after_insert')
def trigger_ya_prim_coll(mapper, connection, target):
    """
    Вызывается после добавления нового ресторана в базу данных.
    """
    rest_link = target.yandex_link  # Предположим, что ссылка хранится в поле yandex_link
    logger.info(f"Новый ресторан добавлен. Запуск ya_prim_coll для {rest_link}")

    # Запуск ya_prim_coll в фоновом режиме
    from threading import Thread
    thread = Thread(target=ya_prim_coll, args=(rest_link,))
    thread.start()
