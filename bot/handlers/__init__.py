from bot.handlers.start import router as start_router
from bot.handlers.yandex import router as yandex_router
from bot.handlers.data_edit import router as data_edit_router

routers = [start_router, yandex_router, data_edit_router]
