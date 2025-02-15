from .start import router as start_router
from .yandex import router as yandex_router
from .data_edit import router as data_edit_router

routers = [start_router, yandex_router, data_edit_router]
