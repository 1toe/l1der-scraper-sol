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
from lider_scraper import LiderScraper
from lider_filter import ProductFilter

def parse_arguments():
    """Parsea los argumentos de línea de comandos"""
    parser = argparse.ArgumentParser(description='Scraper de productos de Lider.cl')
    parser.add_argument('--categories', type=int, default=3, 
                        help='Número de categorías a procesar (default: 3)')
    parser.add_argument('--products', type=int, default=5, 
                        help='Número de productos por categoría a procesar (default: 5)')
    parser.add_argument('--pages', type=int, default=2, 
                        help='Número de páginas por categoría a procesar (default: 2)')
    parser.add_argument('--max-sellos', type=int, default=2, 
                        help='Número máximo de sellos permitidos (default: 2)')
    parser.add_argument('--output', type=str, default='productos_lider_max_2_sellos.csv', 
                        help='Archivo de salida (default: productos_lider_max_2_sellos.csv)')
    parser.add_argument('--headless', action='store_true', 
                        help='Ejecutar en modo headless (sin interfaz gráfica)')
    return parser.parse_args()

def main():
    """Función principal"""
    # Parsear argumentos
    args = parse_arguments()
    
    print("=== Iniciando scraper de productos de Lider.cl ===")
    print(f"Configuración:")
    print(f"- Categorías a procesar: {args.categories}")
    print(f"- Productos por categoría: {args.products}")
    print(f"- Páginas por categoría: {args.pages}")
    print(f"- Máximo de sellos permitidos: {args.max_sellos}")
    print(f"- Archivo de salida: {args.output}")
    print(f"- Modo headless: {args.headless}")
    
    # Inicializar el scraper
    scraper = LiderScraper(headless=args.headless)
    
    try:
        # Obtener categorías
        print("\n=== Obteniendo categorías ===")
        categories = scraper.get_categories()
        
        if not categories:
            print("No se pudieron obtener las categorías. Utilizando categorías predefinidas.")
            # Categorías predefinidas en caso de que falle la obtención automática
            categories = [
                {'name': 'Despensa', 'url': 'https://www.lider.cl/supermercado/category/Despensa'},
                {'name': 'Lácteos y Huevos', 'url': 'https://www.lider.cl/supermercado/category/Lácteos-y-Huevos'},
                {'name': 'Frutas y Verduras', 'url': 'https://www.lider.cl/supermercado/category/Frutas-y-Verduras'},
                {'name': 'Carnes', 'url': 'https://www.lider.cl/supermercado/category/Carnes'},
                {'name': 'Congelados', 'url': 'https://www.lider.cl/supermercado/category/Congelados'}
            ]
        
        # Limitar a las categorías especificadas
        test_categories = categories[:args.categories]
        print(f"Se procesarán {len(test_categories)} categorías:")
        for i, cat in enumerate(test_categories):
            print(f"{i+1}. {cat['name']}")
        
        all_products = []
        detailed_products = []
        
        # Obtener productos de cada categoría
        for i, category in enumerate(test_categories):
            print(f"\n=== Procesando categoría {i+1}/{len(test_categories)}: {category['name']} ===")
            category_products = scraper.get_products_from_category(category['url'], max_pages=args.pages)
            all_products.extend(category_products)
            
            # Limitar a los productos especificados por categoría
            test_products = category_products[:args.products]
            print(f"Se obtuvieron {len(category_products)} productos, procesando {len(test_products)}")
            
            # Obtener detalles de cada producto
            for j, product in enumerate(test_products):
                print(f"Producto {j+1}/{len(test_products)}: {product['name']}")
                product_details = scraper.get_product_details(product['url'])
                if product_details:
                    detailed_products.append(product_details)
                    print(f"  - Sellos: {product_details.get('num_sellos', 'N/A')}")
                else:
                    print("  - No se pudieron obtener detalles")
                
                # Pequeña pausa para evitar sobrecarga
                time.sleep(1)
        
        # Filtrar productos con máximo N sellos "ALTO EN"
        print(f"\n=== Filtrando productos con máximo {args.max_sellos} sellos 'ALTO EN' ===")
        filtered_products = scraper.filter_products_by_sellos(detailed_products, max_sellos=args.max_sellos)
        
        # Guardar productos filtrados en CSV
        print(f"\n=== Guardando {len(filtered_products)} productos filtrados en {args.output} ===")
        scraper.save_to_csv(filtered_products, args.output)
        
        # Aplicar filtro adicional con la clase ProductFilter
        print("\n=== Aplicando filtro adicional basado en información nutricional ===")
        filtrador = ProductFilter()
        refined_products = filtrador.filter_products(filtered_products, max_sellos=args.max_sellos)
        
        # Guardar productos refinados en CSV
        refined_output = f"refined_{args.output}"
        print(f"=== Guardando {len(refined_products)} productos refinados en {refined_output} ===")
        filtrador.save_to_csv(refined_products, refined_output)
        
        print(f"\n=== Resumen ===")
        print(f"- Total de productos encontrados: {len(all_products)}")
        print(f"- Productos con detalles obtenidos: {len(detailed_products)}")
        print(f"- Productos con máximo {args.max_sellos} sellos (filtro básico): {len(filtered_products)}")
        print(f"- Productos con máximo {args.max_sellos} sellos (filtro refinado): {len(refined_products)}")
        print(f"\nArchivos generados:")
        print(f"- {args.output}")
        print(f"- {refined_output}")
        
    except KeyboardInterrupt:
        print("\n\nOperación interrumpida por el usuario")
    except Exception as e:
        print(f"\n\nError en la ejecución principal: {str(e)}")
    
    finally:
        # Cerrar el navegador
        print("\n=== Cerrando navegador ===")
        scraper.close()
        print("Proceso completado.")


if __name__ == "__main__":
    main()
