#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para ejecutar el scraper de Lider con manejo de errores mejorado
y opciones de configuración.

Este script ejecuta el scraper de productos de Lider.cl con opciones
para controlar el número de categorías y productos a procesar.
"""

import os
import sys
import time
import argparse
import random
from lider_scraper import LiderScraper
from lider_filter import ProductFilter

def parse_arguments():
    """Parsea los argumentos de línea de comandos"""
    parser = argparse.ArgumentParser(description='Scraper de productos de Lider.cl con bypass de captcha')
    parser.add_argument('--categories', type=int, default=2, 
                        help='Número máximo de categorías a procesar (default: 2)')
    parser.add_argument('--pages', type=int, default=1, 
                        help='Número máximo de páginas por categoría a procesar (default: 1)')
    parser.add_argument('--max-sellos', type=int, default=2, 
                        help='Número máximo de sellos permitidos (default: 2)')
    parser.add_argument('--output', type=str, default='productos_lider_filtrados.xlsx', 
                        help='Archivo Excel de salida para productos filtrados (default: productos_lider_filtrados.xlsx)')
    parser.add_argument('--headless', action='store_true', 
                        help='Ejecutar en modo headless (sin interfaz gráfica)')
    # Argumentos de login (opcional)
    parser.add_argument('--login', action='store_true', help='Intentar iniciar sesión antes de scrapear')
    parser.add_argument('--email', type=str, default=None, help='Email para iniciar sesión')
    parser.add_argument('--password', type=str, default=None, help='Contraseña para iniciar sesión')
    return parser.parse_args()

def main():
    """Función principal"""
    # Parsear argumentos
    args = parse_arguments()
    
    print("=== Iniciando scraper de productos de Lider.cl ===")
    print(f"Configuración:")
    print(f"- Máximo de categorías a procesar: {args.categories}")
    print(f"- Máximo de páginas por categoría: {args.pages}")
    print(f"- Máximo de sellos permitidos: {args.max_sellos}")
    print(f"- Archivo de salida: {args.output}")
    print(f"- Modo headless: {args.headless}")
    print(f"- Intentar login: {args.login}")
    
    # Validar credenciales si se usa login
    if args.login and (not args.email or not args.password):
        print("Error: Se requiere --email y --password si se usa --login.")
        sys.exit(1)

    # Inicializar el scraper
    scraper = LiderScraper(headless=args.headless)
    all_detailed_products = []
    
    try:
        # Iniciar sesión si se especifica
        if args.login:
            print("\n=== Intentando iniciar sesión ===")
            if not scraper.login(args.email, args.password):
                print("Fallo en el inicio de sesión. El scraping continuará sin sesión iniciada, pero podría fallar.")
                # Decidir si continuar o salir
                # sys.exit(1) # Descomentar para salir si el login falla
            else:
                print("Inicio de sesión exitoso.")
            time.sleep(random.uniform(2, 4))

        # Obtener categorías
        print("\n=== Obteniendo categorías ===")
        categories = scraper.get_categories()
        
        if not categories:
            print("No se pudieron obtener las categorías. Terminando script.")
            sys.exit(1)
        
        # Limitar a las categorías especificadas
        categories_to_scrape = categories[:args.categories]
        print(f"Se procesarán hasta {len(categories_to_scrape)} categorías:")
        for i, cat in enumerate(categories_to_scrape):
            print(f"{i+1}. {cat['name']}")
        
        # Obtener productos y detalles de cada categoría
        for i, category in enumerate(categories_to_scrape):
            print(f"\n=== Procesando categoría {i+1}/{len(categories_to_scrape)}: {category['name']} ({category['url']}) ===")
            # Obtener productos básicos (nombre, url, etc.)
            category_products_basic = scraper.get_products_from_category(category['url'], max_pages=args.pages)
            
            if not category_products_basic:
                print("No se encontraron productos en esta categoría o hubo un error.")
                continue

            print(f"Se obtuvieron {len(category_products_basic)} productos básicos. Obteniendo detalles...")
            
            # Obtener detalles de cada producto
            for j, product_basic in enumerate(category_products_basic):
                print(f"  Detalle producto {j+1}/{len(category_products_basic)}: {product_basic.get('name', 'N/A')}")
                try:
                    product_details = scraper.get_product_details(product_basic['url'])
                    # Combinar info básica con detalles obtenidos
                    # Damos prioridad a los detalles obtenidos de la página del producto
                    full_details = {**product_basic, **product_details} 
                    all_detailed_products.append(full_details)
                    print(f"    - Sellos: {full_details.get('sellos_count', 'N/A')}")
                except Exception as detail_err:
                    print(f"    - Error al obtener detalles para {product_basic.get('name', 'N/A')}: {detail_err}")
                
                # Pausa entre solicitudes de detalles
                time.sleep(random.uniform(1.5, 3.5))
        
        print(f"\n=== Total de productos con detalles obtenidos: {len(all_detailed_products)} ===")

        # Filtrar productos con máximo N sellos "ALTO EN" usando la clase LiderScraper
        # (Esta función ahora está en LiderScraper y usa 'sellos_count')
        print(f"\n=== Filtrando productos con máximo {args.max_sellos} sellos 'ALTO EN' (usando LiderScraper.filter_products) ===")
        filtered_products = scraper.filter_products(all_detailed_products) # Usa el método de LiderScraper
        
        # Guardar productos filtrados en Excel usando la clase LiderScraper
        print(f"\n=== Guardando {len(filtered_products)} productos filtrados en {args.output} (usando LiderScraper.save_to_excel) ===")
        scraper.save_to_excel(filtered_products, args.output)
        
        # Opcional: Aplicar filtro adicional con la clase ProductFilter si se desea
        # Esto puede ser redundante si LiderScraper.filter_products ya hizo el trabajo
        # print("\n=== Aplicando filtro adicional basado en información nutricional (usando ProductFilter) ===")
        # filtrador = ProductFilter()
        # refined_products = filtrador.filter_products(filtered_products, max_sellos=args.max_sellos)
        # refined_output = f"refined_{args.output.replace('.xlsx', '.csv')}" # Guardar como CSV
        # print(f"=== Guardando {len(refined_products)} productos refinados en {refined_output} (usando ProductFilter.save_to_csv) ===")
        # filtrador.save_to_csv(refined_products, refined_output)
        
        print(f"\n=== Resumen Final ===")
        print(f"- Total de productos con detalles obtenidos: {len(all_detailed_products)}")
        print(f"- Productos con máximo {args.max_sellos} sellos (filtrados): {len(filtered_products)}")
        print(f"\nArchivo generado:")
        print(f"- {args.output}")
        # if 'refined_output' in locals(): print(f"- {refined_output}")
        
    except KeyboardInterrupt:
        print("\n\nOperación interrumpida por el usuario")
    except Exception as e:
        import traceback
        print(f"\n\nError en la ejecución principal: {str(e)}")
        print(traceback.format_exc())
        # Guardar captura de pantalla en caso de error inesperado
        try:
            error_screenshot = "error_main_execution.png"
            scraper.driver.save_screenshot(error_screenshot)
            print(f"Captura de pantalla guardada en {error_screenshot}")
        except Exception as screen_err:
            print(f"No se pudo guardar la captura de pantalla: {screen_err}")
    
    finally:
        # Cerrar el navegador
        print("\n=== Cerrando navegador ===")
        scraper.close()
        print("Proceso completado.")


if __name__ == "__main__":
    main()

