#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Lider Product Filter

Este script implementa la lógica de filtrado para productos con máximo 2 sellos "ALTO EN"
según la Ley 20.606, utilizando los datos extraídos del sitio web de Lider.cl.

Fecha: Abril 2025
"""

import json
import pandas as pd
import re

class ProductFilter:
    """Clase para filtrar productos según criterios de la Ley 20.606"""
    
    def __init__(self):
        """Inicializa el filtrador de productos"""
        # Límites nutricionales para productos sólidos (por 100g)
        self.limites_solidos = {
            'energia': 275,  # kcal
            'azucares': 10,  # g
            'grasas_saturadas': 4,  # g
            'sodio': 400  # mg
        }
        
        # Límites nutricionales para productos líquidos (por 100ml)
        self.limites_liquidos = {
            'energia': 70,  # kcal
            'azucares': 5,  # g
            'grasas_saturadas': 3,  # g
            'sodio': 100  # mg
        }
        
        # Mapeo de nombres de nutrientes para normalización
        self.nutrient_mapping = {
            'energia': ['energía', 'energia', 'energy', 'kcal', 'calorías', 'calorias'],
            'azucares': ['azúcares', 'azucares', 'azúcares totales', 'azucares totales', 'sugar', 'sugars'],
            'grasas_saturadas': ['grasas saturadas', 'saturated fat', 'saturated fats', 'grasa saturada'],
            'sodio': ['sodio', 'sodium', 'sal', 'salt']
        }
    
    def _normalize_nutrient_name(self, name):
        """
        Normaliza el nombre de un nutriente
        
        Args:
            name (str): Nombre del nutriente
        
        Returns:
            str: Nombre normalizado del nutriente
        """
        name_lower = name.lower()
        
        for key, variants in self.nutrient_mapping.items():
            if any(variant in name_lower for variant in variants):
                return key
        
        return name_lower
    
    def _extract_numeric_value(self, value_str):
        """
        Extrae el valor numérico de una cadena
        
        Args:
            value_str (str): Cadena con valor numérico
        
        Returns:
            float: Valor numérico extraído
        """
        if isinstance(value_str, (int, float)):
            return float(value_str)
        
        # Eliminar caracteres no numéricos excepto punto decimal
        value_str = re.sub(r'[^\d.]', '', str(value_str))
        
        try:
            return float(value_str) if value_str else 0.0
        except ValueError:
            return 0.0
    
    def _is_liquid_product(self, product_name, product_category=None):
        """
        Determina si un producto es líquido basado en su nombre y categoría
        
        Args:
            product_name (str): Nombre del producto
            product_category (str, optional): Categoría del producto
        
        Returns:
            bool: True si es líquido, False si es sólido
        """
        liquid_keywords = [
            'bebida', 'jugo', 'leche', 'yogurt', 'yoghurt', 'agua', 'refresco',
            'aceite', 'vino', 'cerveza', 'licor', 'líquido', 'liquido', 'ml',
            'litro', 'l.', 'lt', 'drink', 'milk', 'oil', 'wine', 'beer'
        ]
        
        liquid_categories = [
            'bebidas', 'lacteos', 'lácteos', 'aceites', 'vinos', 'cervezas',
            'licores', 'jugos', 'aguas'
        ]
        
        # Verificar por palabras clave en el nombre
        product_name_lower = product_name.lower()
        if any(keyword in product_name_lower for keyword in liquid_keywords):
            return True
        
        # Verificar por categoría
        if product_category:
            product_category_lower = product_category.lower()
            if any(category in product_category_lower for category in liquid_categories):
                return True
        
        # Verificar si el nombre contiene indicación de volumen (ml, l)
        if re.search(r'\d+\s*(?:ml|l\b|lt\b)', product_name_lower):
            return True
        
        return False
    
    def _count_sellos_by_nutrition(self, info_nutricional, is_liquid):
        """
        Cuenta el número de sellos "ALTO EN" basado en la información nutricional
        
        Args:
            info_nutricional (dict): Información nutricional del producto
            is_liquid (bool): Indica si el producto es líquido
        
        Returns:
            dict: Diccionario con los sellos encontrados y su conteo
        """
        sellos = []
        limites = self.limites_liquidos if is_liquid else self.limites_solidos
        
        # Normalizar nombres de nutrientes
        normalized_info = {}
        for nutrient, value in info_nutricional.items():
            normalized_name = self._normalize_nutrient_name(nutrient)
            normalized_value = self._extract_numeric_value(value)
            normalized_info[normalized_name] = normalized_value
        
        # Verificar cada nutriente crítico
        if 'energia' in normalized_info and normalized_info['energia'] > limites['energia']:
            sellos.append('ALTO EN CALORÍAS')
        
        if 'azucares' in normalized_info and normalized_info['azucares'] > limites['azucares']:
            sellos.append('ALTO EN AZÚCARES')
        
        if 'grasas_saturadas' in normalized_info and normalized_info['grasas_saturadas'] > limites['grasas_saturadas']:
            sellos.append('ALTO EN GRASAS SATURADAS')
        
        if 'sodio' in normalized_info and normalized_info['sodio'] > limites['sodio']:
            sellos.append('ALTO EN SODIO')
        
        return {
            'sellos': sellos,
            'num_sellos': len(sellos)
        }
    
    def filter_products(self, products, max_sellos=2):
        """
        Filtra productos según el número de sellos "ALTO EN"
        
        Args:
            products (list): Lista de productos
            max_sellos (int): Número máximo de sellos permitidos
        
        Returns:
            list: Lista de productos filtrados
        """
        filtered_products = []
        
        for product in products:
            # Si ya tiene información de sellos
            if 'sellos_alto_en' in product and isinstance(product['sellos_alto_en'], list):
                num_sellos = len(product['sellos_alto_en'])
            
            # Si tiene información nutricional pero no sellos explícitos
            elif 'info_nutricional' in product and product['info_nutricional']:
                info_nutricional = product['info_nutricional']
                
                # Convertir de string a dict si es necesario
                if isinstance(info_nutricional, str):
                    try:
                        info_nutricional = json.loads(info_nutricional)
                    except:
                        info_nutricional = {}
                
                # Determinar si es líquido o sólido
                is_liquid = self._is_liquid_product(product['name'], product.get('category', ''))
                
                # Contar sellos basado en información nutricional
                sellos_info = self._count_sellos_by_nutrition(info_nutricional, is_liquid)
                
                # Actualizar información de sellos en el producto
                product['sellos_alto_en'] = sellos_info['sellos']
                product['num_sellos'] = sellos_info['num_sellos']
                num_sellos = sellos_info['num_sellos']
            
            # Si no hay información suficiente
            else:
                # Si no hay información explícita de sellos ni nutricional, no podemos determinar
                if 'num_sellos' in product:
                    num_sellos = product['num_sellos']
                else:
                    # No podemos determinar, asumimos que no cumple
                    continue
            
            # Filtrar por número máximo de sellos
            if num_sellos <= max_sellos:
                filtered_products.append(product)
        
        return filtered_products
    
    def load_from_csv(self, filename):
        """
        Carga productos desde un archivo CSV
        
        Args:
            filename (str): Nombre del archivo CSV
        
        Returns:
            list: Lista de productos
        """
        try:
            df = pd.read_csv(filename, encoding='utf-8-sig')
            
            # Convertir DataFrame a lista de diccionarios
            products = df.to_dict('records')
            
            # Convertir columnas de string a listas y diccionarios
            for product in products:
                for key, value in product.items():
                    if isinstance(value, str) and (value.startswith('[') or value.startswith('{')):
                        try:
                            product[key] = json.loads(value)
                        except:
                            pass
            
            return products
            
        except Exception as e:
            print(f"Error al cargar datos desde CSV: {str(e)}")
            return []
    
    def save_to_csv(self, products, filename):
        """
        Guarda productos en un archivo CSV
        
        Args:
            products (list): Lista de productos
            filename (str): Nombre del archivo CSV
        
        Returns:
            bool: True si se guardó correctamente, False en caso contrario
        """
        try:
            # Convertir a DataFrame
            df = pd.DataFrame(products)
            
            # Convertir columnas de listas y diccionarios a formato string
            for col in df.columns:
                if df[col].apply(lambda x: isinstance(x, (list, dict))).any():
                    df[col] = df[col].apply(lambda x: json.dumps(x, ensure_ascii=False) if isinstance(x, (list, dict)) else x)
            
            # Guardar a CSV
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            
            print(f"Datos guardados correctamente en {filename}")
            return True
            
        except Exception as e:
            print(f"Error al guardar datos en CSV: {str(e)}")
            return False


def main():
    """Función principal"""
    # Inicializar el filtrador
    filtrador = ProductFilter()
    
    try:
        # Cargar productos desde CSV (si existe)
        input_file = "productos_lider.csv"
        products = filtrador.load_from_csv(input_file)
        
        if not products:
            print(f"No se pudieron cargar productos desde {input_file}")
            return
        
        print(f"Se cargaron {len(products)} productos")
        
        # Filtrar productos con máximo 2 sellos "ALTO EN"
        filtered_products = filtrador.filter_products(products, max_sellos=2)
        
        print(f"Se encontraron {len(filtered_products)} productos con máximo 2 sellos 'ALTO EN'")
        
        # Guardar productos filtrados en CSV
        output_file = "productos_lider_max_2_sellos_filtrados.csv"
        filtrador.save_to_csv(filtered_products, output_file)
        
    except Exception as e:
        print(f"Error en la ejecución principal: {str(e)}")


if __name__ == "__main__":
    main()
