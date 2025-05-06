from django.db import models


class Inventario(models.Model):
    marca = models.CharField(max_length=100)
    nombre = models.CharField(max_length=100)
    precio = models.CharField(max_length=100)
    fecha = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.marca} - {self.nombre}"


class ProductoInformacionNutricional(models.Model):
    producto = models.ForeignKey(Inventario, on_delete=models.CASCADE, related_name='informacion_nutricional')
    descripcion = models.CharField(max_length=255)
    pais_origen = models.CharField(max_length=100)
    caracteristicas = models.TextField(null=True, blank=True)
    sellos_alto_en = models.TextField(null=True, blank=True)
    ingredientes = models.TextField(null=True, blank=True)
    trazas = models.TextField(null=True, blank=True)
    porcion = models.CharField(max_length=100, null=True, blank=True)
    porciones_envase = models.IntegerField(null=True, blank=True)
    energia_100g = models.FloatField(null=True, blank=True)
    energia_porcion = models.FloatField(null=True, blank=True)
    proteinas_100g = models.FloatField(null=True, blank=True)
    proteinas_porcion = models.FloatField(null=True, blank=True)
    grasas_totales_100g = models.FloatField(null=True, blank=True)
    grasas_totales_porcion = models.FloatField(null=True, blank=True)
    grasas_saturadas_100g = models.FloatField(null=True, blank=True)
    grasas_saturadas_porcion = models.FloatField(null=True, blank=True)
    grasas_mono_100g = models.FloatField(null=True, blank=True)
    grasas_mono_porcion = models.FloatField(null=True, blank=True)
    grasas_poli_100g = models.FloatField(null=True, blank=True)
    grasas_poli_porcion = models.FloatField(null=True, blank=True)
    grasas_trans_100g = models.FloatField(null=True, blank=True)
    grasas_trans_porcion = models.FloatField(null=True, blank=True)
    colesterol_100g = models.FloatField(null=True, blank=True)
    colesterol_porcion = models.FloatField(null=True, blank=True)
    carbohidratos_100g = models.FloatField(null=True, blank=True)
    carbohidratos_porcion = models.FloatField(null=True, blank=True)
    azucares_100g = models.FloatField(null=True, blank=True)
    azucares_porcion = models.FloatField(null=True, blank=True)
    fibra_100g = models.FloatField(null=True, blank=True)
    fibra_porcion = models.FloatField(null=True, blank=True)
    sodio_100g = models.FloatField(null=True, blank=True)
    sodio_porcion = models.FloatField(null=True, blank=True)
    fecha_actualizacion = models.DateField(auto_now_add=True)
    ean = models.CharField(max_length=20, null=True, blank=True)
    
    def __str__(self):
        return f"Info Nutricional: {self.producto.nombre}"
