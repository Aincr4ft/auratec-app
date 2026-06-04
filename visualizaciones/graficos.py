import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import customtkinter as ctk

def crear_grafico_ventas(parent, datos_ventas):
    """Crea un gráfico de líneas para las ventas de los últimos 7 días."""
    fig, ax = plt.subplots(figsize=(5, 3), dpi=100)
    fig.patch.set_facecolor('#2b2b2b')
    ax.set_facecolor('#2b2b2b')
    
    dias = [d['dia'] for d in datos_ventas]
    totales = [d['total'] for d in datos_ventas]
    
    ax.plot(dias, totales, marker='o', color='#1f538d', linewidth=2, markersize=6)
    ax.fill_between(dias, totales, color='#1f538d', alpha=0.2)
    
    ax.set_title("Ventas últimos 7 días", color='white', fontsize=10, pad=10)
    ax.tick_params(axis='x', colors='white', labelsize=8)
    ax.tick_params(axis='y', colors='white', labelsize=8)
    for spine in ax.spines.values():
        spine.set_color('#444')
    
    plt.tight_layout()
    
    canvas = FigureCanvasTkAgg(fig, master=parent)
    return canvas.get_tk_widget()

def crear_grafico_categorias(parent, datos_cat):
    """Crea un gráfico de barras para las ventas por categoría."""
    fig, ax = plt.subplots(figsize=(5, 3), dpi=100)
    fig.patch.set_facecolor('#2b2b2b')
    ax.set_facecolor('#2b2b2b')
    
    categorias = [c['categoria'] for c in datos_cat]
    totales = [c['total'] for c in datos_cat]
    
    colores = ['#16a085', '#2980b9', '#8e44ad', '#d35400', '#c0392b']
    ax.bar(categorias, totales, color=colores[:len(categorias)])
    
    ax.set_title("Ventas por Categoría", color='white', fontsize=10, pad=10)
    ax.tick_params(axis='x', colors='white', labelsize=8, rotation=15)
    ax.tick_params(axis='y', colors='white', labelsize=8)
    for spine in ax.spines.values():
        spine.set_color('#444')
    
    plt.tight_layout()
    
    canvas = FigureCanvasTkAgg(fig, master=parent)
    return canvas.get_tk_widget()
