# Extractor de Productos Lider con Máximo 2 Sellos "ALTO EN"

Este proyecto proporciona una solución para extraer datos de productos del sitio web de Lider.cl, filtrando aquellos que tienen máximo 2 sellos "ALTO EN" según la Ley 20.606.

## Descripción

La solución consta de tres componentes principales:

1. **Scraper de Lider (`lider_scraper.py`)**: Utiliza Selenium para navegar por el sitio web de Lider.cl, manejar la protección anti-bot, y extraer datos de productos incluyendo información nutricional y sellos "ALTO EN".

2. **Filtrador de Productos (`lider_filter.py`)**: Implementa la lógica para filtrar productos según los criterios de la Ley 20.606, determinando si un producto es líquido o sólido, normalizando nombres de nutrientes, y contando sellos basados en información nutricional.

3. **Script Integrador (`run_lider_scraper.py`)**: Integra ambas soluciones y proporciona opciones de configuración mediante argumentos de línea de comandos.

## Requisitos

- Python 3.6 o superior
- Selenium
- webdriver-manager
- pandas

## Instalación

```bash
pip install selenium webdriver-manager pandas
```

## Uso

### Ejecución básica

```bash
python run_lider_scraper.py
```

### Opciones de configuración

```bash
python run_lider_scraper.py --categories 3 --products 5 --pages 2 --max-sellos 2 --output productos_lider.csv --headless
```

Parámetros disponibles:
- `--categories`: Número de categorías a procesar (default: 3)
- `--products`: Número de productos por categoría a procesar (default: 5)
- `--pages`: Número de páginas por categoría a procesar (default: 2)
- `--max-sellos`: Número máximo de sellos permitidos (default: 2)
- `--output`: Archivo de salida (default: productos_lider_max_2_sellos.csv)
- `--headless`: Ejecutar en modo headless (sin interfaz gráfica)

## Manejo de la protección anti-bot

El sitio web de Lider.cl tiene protección anti-bot (captcha) que dificulta el acceso mediante web scraping tradicional. La solución implementa varias técnicas para manejar esta protección:

1. Configuraciones de Selenium para evitar detección como bot
2. Simulación de comportamiento humano
3. Manejo de captchas cuando aparecen

Sin embargo, en algunos casos puede ser necesaria la intervención manual para resolver captchas.

## Criterios de filtrado según Ley 20.606

Los productos se filtran según los siguientes criterios:

### Límites nutricionales para productos sólidos (por 100g)
- Energía: 275 kcal
- Azúcares: 10 g
- Grasas saturadas: 4 g
- Sodio: 400 mg

### Límites nutricionales para productos líquidos (por 100ml)
- Energía: 70 kcal
- Azúcares: 5 g
- Grasas saturadas: 3 g
- Sodio: 100 mg

Un producto recibe un sello "ALTO EN" por cada nutriente que supere estos límites. La solución filtra productos con máximo 2 sellos.

## Estructura de datos de salida

Los datos se guardan en formato CSV con la siguiente estructura:

- `name`: Nombre del producto
- `brand`: Marca del producto
- `price`: Precio del producto
- `url`: URL del producto
- `sellos_alto_en`: Lista de sellos "ALTO EN"
- `num_sellos`: Número de sellos "ALTO EN"
- `info_nutricional`: Información nutricional del producto
- `alergenos`: Declaración de alérgenos
- `ingredientes`: Lista de ingredientes

## Limitaciones

- La solución depende de la estructura actual del sitio web de Lider.cl. Cambios en el sitio pueden requerir actualizaciones del código.
- La protección anti-bot puede requerir intervención manual en algunos casos.
- La extracción de datos puede ser lenta debido a las pausas necesarias para evitar ser detectado como bot.
- La determinación de si un producto es líquido o sólido se basa en heurísticas que pueden no ser 100% precisas.

## Autor

Manus AI - Abril 2025
