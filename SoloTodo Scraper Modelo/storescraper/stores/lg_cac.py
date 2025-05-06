from .lg_v5 import LgV5
from ..categories import (
    TELEVISION,
    PROJECTOR,
    STEREO_SYSTEM,
    OPTICAL_DISK_PLAYER,
    CELL,
    HEADPHONES,
    REFRIGERATOR,
    STOVE,
    OVEN,
    ACCESORIES,
    DISH_WASHER,
    WASHING_MACHINE,
    VACUUM_CLEANER,
    SPLIT_AIR_CONDITIONER,
    MONITOR,
)


class LgCac(LgV5):
    region_code = "cac"

    @classmethod
    def _category_paths(cls):
        return [
            # Todos los Televisores
            ("CT20188038", TELEVISION, True),
            ("CT20188038", TELEVISION, False),
            # Lifestyle Screens
            ("CT40018527", TELEVISION, True),
            ("CT40018527", TELEVISION, False),
            # Proyectores
            ("CT20188025", PROJECTOR, True),
            ("CT20188025", PROJECTOR, False),
            # Equipos de sonido
            ("CT40018517", STEREO_SYSTEM, True),
            ("CT40018517", STEREO_SYSTEM, False),
            # Video
            ("CT20188055", OPTICAL_DISK_PLAYER, True),
            ("CT20188055", OPTICAL_DISK_PLAYER, False),
            # Teléfonos Celulares
            ("CT20188032", CELL, True),
            ("CT20188032", CELL, False),
            # Audífonos
            ("CT40011643", HEADPHONES, True),
            ("CT40011643", HEADPHONES, False),
            # Refrigeradora
            ("CT20188021", REFRIGERATOR, True),
            ("CT20188021", REFRIGERATOR, False),
            # Estufa
            ("CT30015260", STOVE, True),
            ("CT30015260", STOVE, False),
            # Microondas
            ("CT20188009", OVEN, True),
            ("CT20188009", OVEN, False),
            # Campanas (consideradas como accesorios)
            ("CT32021842", ACCESORIES, True),
            # Lavaplatos
            ("CT30015420", DISH_WASHER, True),
            # Lavadoras y secadoras
            ("CT20188014", WASHING_MACHINE, True),
            ("CT20188014", WASHING_MACHINE, False),
            # Styler
            ("CT32015142", WASHING_MACHINE, True),
            # Aspiradoras
            ("CT20188013", VACUUM_CLEANER, True),
            ("CT20188013", VACUUM_CLEANER, False),
            # Aire acondicionado residencial
            ("CT30014140", SPLIT_AIR_CONDITIONER, True),
            ("CT30014140", SPLIT_AIR_CONDITIONER, False),
            # Deshumidificador
            # ('CT32021782', 'AirConditioner', True),
            # Monitores
            ("CT20188028", MONITOR, True),
            ("CT20188028", MONITOR, False),
            # Dispositivos ópticos
            ("CT20188024", MONITOR, True),
            ("CT20188024", MONITOR, False),
            # LG Studio
            ("CT32021962", STOVE, True),
        ]
