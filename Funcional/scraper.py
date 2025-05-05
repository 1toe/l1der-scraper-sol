import asyncio
from firecrawl import FirecrawlApp
from bs4 import BeautifulSoup
import json
import os
import re

async def extract_nutritional_info():
    api_key = "fc-7775914fc23745c38c34d5d509b85793"
    category_url = "https://www.lider.cl/supermercado/category/Frutas_y_Verduras/Verduras?page=1&hitsPerPage=24"
    output_file = "lider_nutritional_info.json"
    product_urls_file = "product_urls.txt" # File to save product URLs
    results = []

    app = FirecrawlApp(api_key=api_key)

    # Usar enlaces de ejemplo para pruebas
    product_links = [
        "https://www.lider.cl/supermercado/product/sku/3763/multi-marca-champinones-blanco-bandeja-200-g",
        "https://www.lider.cl/supermercado/product/sku/327604/multi-marca-tomate-larga-vida-granel-500-g-2-a-3-un-aprox",
        "https://www.lider.cl/supermercado/product/sku/325702/multi-marca-tomate-larga-vida-malla-1-kg",
        "https://www.lider.cl/supermercado/product/sku/327806/multi-marca-zanahoria-bolsa-1-kg"
    ]
    print(f"Using {len(product_links)} product links for extraction.")

    # Save product URLs for reference
    with open(product_urls_file, 'w') as f:
        for url in product_links:
            f.write(url + '\n')
    print(f"Product URLs saved to {product_urls_file}")

    # Define schema for extraction
    product_schema = {
        "type": "object",
        "properties": {
            "product_name": {"type": "string", "description": "Name of the product"},
            "brand": {"type": "string", "description": "Brand of the product"},
            "price": {"type": "string", "description": "Price of the product"},
            "quantity": {"type": "string", "description": "Quantity or weight of product"},
            "image_url": {"type": "string", "description": "URL of main product image"},
            "nutritional_table": {
                "type": "object",
                "properties": {
                    "serving_size": {"type": "string"},
                    "servings_per_container": {"type": "string"},
                    "energy_per_100g": {"type": "string"},
                    "energy_per_serving": {"type": "string"},
                    "protein_per_100g": {"type": "string"},
                    "protein_per_serving": {"type": "string"},
                    "total_fat_per_100g": {"type": "string"},
                    "total_fat_per_serving": {"type": "string"},
                    "carbs_per_100g": {"type": "string"},
                    "carbs_per_serving": {"type": "string"},
                    "sugar_per_100g": {"type": "string"},
                    "sugar_per_serving": {"type": "string"},
                    "fiber_per_100g": {"type": "string"},
                    "fiber_per_serving": {"type": "string"},
                    "sodium_per_100g": {"type": "string"},
                    "sodium_per_serving": {"type": "string"}
                }
            },
            "raw_nutritional_html": {"type": "string", "description": "Raw HTML of the nutritional information table"}
        }
    }

    # Extract info for each product
    for i, url in enumerate(product_links):
        print(f"Extracting info from: {url} ({i+1}/{len(product_links)})")
        try:
            # Usar el agente FIRE-1 para navegación más compleja
            extraction_result = app.extract(
                [url], 
                prompt="""
                Extract the following information from this product page:
                1. Product name
                2. Brand
                3. Price
                4. Quantity/Weight
                5. Image URL
                6. Complete nutritional information table inside the div with data-testid="ok-to-shop"
                
                For the nutritional table, extract:
                - Serving size
                - Servings per container
                - Values for both per 100g and per serving for:
                  * Energy (kcal)
                  * Protein (g)
                  * Total fat (g)
                  * Carbohydrates (g)
                  * Sugar (g)
                  * Fiber (g)
                  * Sodium (mg)
                
                Also return the raw HTML of the nutritional information table.
                """,
                schema=product_schema,
                agent={"model": "FIRE-1"} # Use advanced agent for complex navigation
            )
            
            if extraction_result and hasattr(extraction_result, 'data'):
                # Si hay datos, los añadimos al resultado
                product_data = {
                    'product_url': url,
                    'product_info': extraction_result.data
                }
                
                # Guardar por separado la tabla nutricional en HTML para mantener compatibilidad
                if 'raw_nutritional_html' in extraction_result.data:
                    product_data['nutritional_table_html'] = extraction_result.data['raw_nutritional_html']
                else:
                    product_data['nutritional_table_html'] = "Not available"
                    
                results.append(product_data)
                print(f"Successfully extracted data for {url}")
            else:
                print(f"Extraction failed for {url}. Response: {extraction_result}")
                # Intentar con un prompt más simple como fallback
                simple_result = app.extract(
                    [url],
                    prompt="""
                    Find the nutritional information on this product page and return it. 
                    The nutritional table is inside a div with data-testid="ok-to-shop".
                    Return the name of the product and the raw HTML of the nutritional table.
                    """
                )
                
                if simple_result and hasattr(simple_result, 'data'):
                    results.append({
                        'product_url': url,
                        'product_name': simple_result.data.get('product_name', 'Unknown name'),
                        'nutritional_table_html': simple_result.data.get('raw_html', 'Not found in fallback')
                    })
                else:
                    results.append({
                        'product_url': url, 
                        'nutritional_table_html': 'Extraction failed (No data returned)'
                    })

        except Exception as e:
            print(f"Error extracting {url}: {e}")
            results.append({'product_url': url, 'nutritional_table_html': f'Error: {str(e)}'})
            
        # Add a small delay to avoid overwhelming the API
        await asyncio.sleep(1)

    # Save results to JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    print(f"Extraction complete. Results saved to {output_file}")

# Run the async function
asyncio.run(extract_nutritional_info())


