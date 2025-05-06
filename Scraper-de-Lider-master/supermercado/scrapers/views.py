from django.shortcuts import render
from django.http import HttpResponse
from bs4 import BeautifulSoup
from .models import *


def index(request):
    import requests
    template_name='inicio.html'
    session = requests.Session()
    url = 'https://www.lider.cl/supermercado/'
    content = session.get(url, verify=False).content
    soup = BeautifulSoup(content, "html.parser")
    datos_bruto = soup.find_all('div',{'class':'product-item-box'})
    lista=[]
    for ite in datos_bruto:
        dato=[]
        auxStr=str(ite.find_all('div',{'class':'product-brand'}))
        dato.append(auxStr.replace('[<div class="product-brand">', '').replace('</div>]',''))
        auxStr=str(ite.find_all('div',{'class':'title'}))
        dato.append(auxStr.replace('[<div class="title">', '').replace('</div>]',''))
        auxStr=str(ite.find_all('div',{'class':'sale-price'}))
        dato.append(auxStr.replace('[<div class="sale-price">', '').replace('</div>]',''))
        fila=[dato[0],dato[1],dato[2]]
        lista.append(fila)
    objetosBD=Inventario.objects.all()
    for l in lista:
        band=0
        for objDB in objetosBD:
            if l[0] == objDB.marca and l[1] == objDB.nombre and l[2] != objDB.precio:
                nuevo=Inventario.objects.create(
                    marca=l[0],
                    nombre=l[1],
                    precio=l[2],
                )
                band=1
                nuevo.save()
            if l[0] == objDB.marca and l[1] == objDB.nombre:
                band=1
        if band==0:
            nuevo=Inventario.objects.create(
                marca=l[0],
                nombre=l[1],
                precio=l[2],
            )
            band=0
            nuevo.save()
    objetosBD=Inventario.objects.all()
    contexto={
        'conte': objetosBD,
    }
    return render(request, template_name, contexto)