from django.shortcuts import render

def carrito_view(request):
    return render(request, 'pedidos/carrito.html', {'carrito': None})