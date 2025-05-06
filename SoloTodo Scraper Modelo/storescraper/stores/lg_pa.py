from .lg_v6 import LgV6
from ..categories import (
    TELEVISION,
    MONITOR,
    STEREO_SYSTEM,
    PROJECTOR,
    REFRIGERATOR,
    STOVE,
    OVEN,
    ACCESORIES,
    DISH_WASHER,
    WASHING_MACHINE,
    VACUUM_CLEANER,
    SPLIT_AIR_CONDITIONER,
)


class LgPa(LgV6):
    region_code = "PA"

    @classmethod
    def _category_paths(cls):
        return [
            # Todos los TVs y Barras de Sonido
            ("CT52006973", TELEVISION),
            # Todas las Lifestyle Screens
            ("CT52006974", MONITOR),
            # Todos los Equipos de Sonido
            ("CT52006975", STEREO_SYSTEM),
            # Proyectores
            ("CT52006976", PROJECTOR),
            # Todas las Refrigeradoras
            ("CT52006978", REFRIGERATOR),
            # Estufa (Cocinas)
            ("CT52007012", STOVE),
            # Microonas
            ("CT52007013", OVEN),
            # Campanas
            ("CT52007014", ACCESORIES),
            # Lavaplatos
            ("CT52006980", DISH_WASHER),
            # Todas las lavadoras y secadoras
            ("CT52006981", WASHING_MACHINE),
            # Aspiradoras
            ("CT52006982", VACUUM_CLEANER),
            # Todas las Soluciones de Cuidado del Aire
            ("CT52006983", SPLIT_AIR_CONDITIONER),
            # Aire Acondicionado Split Inverter
            ("CT52007022", SPLIT_AIR_CONDITIONER),
            # Aire Acondicionado Portátil
            ("CT52007023", SPLIT_AIR_CONDITIONER),
            # Todos los Monitores
            ("CT52006985", MONITOR),
            # Todos los Medical Display
            ("CT52007043", ACCESORIES),
            # Information Display
            ("CT52007045", ACCESORIES),
            # Accesorios para TV
            ("CT52007855", ACCESORIES),
            # Accesorios para Audio y Video
            ("CT52007856", ACCESORIES),
            # Accesorios para Refrigeradora
            ("CT52007857", ACCESORIES),
            # Accesorios para Lavadora y Secadora
            ("CT52007858", ACCESORIES),
            # Accesorios para Cocina
            ("CT52007859", ACCESORIES),
            # Accesorios para Aire Acondicionado
            ("CT52007860", ACCESORIES),
        ]
