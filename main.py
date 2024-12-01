import tkinter as tk
from tkinter import ttk
import random
import sqlite3
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns


class LimaClimaDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Dashboard Climático de Lima")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f4f8')

        # Estilo moderno
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabel', background='#f0f4f8', font=('Arial', 12))
        style.configure('TFrame', background='#f0f4f8')

        # Conexión a base de datos
        self.conn = sqlite3.connect('lima_clima.db')
        self.crear_tabla_registros()

        # Zonas de Lima
        self.zonas = [
            'Centro de Lima',
            'Miraflores',
            'Callao',
            'San Isidro',
            'Barranco'
        ]

        # Configuración de la interfaz
        self.crear_interfaz_principal()

    def crear_tabla_registros(self):
        """Crear tabla para almacenar registros climáticos"""
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS registros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                zona TEXT,
                fecha DATETIME,
                temperatura REAL,
                humedad REAL
            )
        ''')
        self.conn.commit()

    def crear_interfaz_principal(self):
        # Marco principal
        marco_principal = ttk.Frame(self.root, padding="10 10 10 10")
        marco_principal.pack(fill=tk.BOTH, expand=True)

        # Título
        titulo = ttk.Label(
            marco_principal,
            text="Dashboard Climático de Lima",
            font=('Arial', 20, 'bold'),
            foreground='#1a5f7a'
        )
        titulo.pack(pady=10)

        # Marco para datos en tiempo real
        marco_tiempo_real = ttk.Frame(marco_principal)
        marco_tiempo_real.pack(fill=tk.X, pady=10)

        # Datos en tiempo real para cada zona
        for zona in self.zonas:
            self.crear_tarjeta_zona(marco_tiempo_real, zona)

        # Gráfico de histórico
        self.crear_grafico_historico(marco_principal)

        # Botones de acción
        marco_botones = ttk.Frame(marco_principal)
        marco_botones.pack(fill=tk.X, pady=10)

        btn_actualizar = ttk.Button(
            marco_botones,
            text="Actualizar Datos",
            command=self.actualizar_datos
        )
        btn_actualizar.pack(side=tk.LEFT, padx=10)

        btn_alertas = ttk.Button(
            marco_botones,
            text="Ver Alertas",
            command=self.mostrar_alertas
        )
        btn_alertas.pack(side=tk.LEFT, padx=10)

    def crear_tarjeta_zona(self, marco_padre, zona):
        """Crear tarjeta de información para cada zona"""
        tarjeta = ttk.Frame(marco_padre, borderwidth=2, relief=tk.RAISED)
        tarjeta.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        # Simular medición
        temperatura = round(random.uniform(18, 25), 1)
        humedad = round(random.uniform(60, 90), 1)

        # Título de zona
        ttk.Label(
            tarjeta,
            text=zona,
            font=('Arial', 14, 'bold'),
            foreground='#2c3e50'
        ).pack(pady=5)

        # Temperatura
        marco_temp = ttk.Frame(tarjeta)
        marco_temp.pack(fill=tk.X, padx=10)
        ttk.Label(marco_temp, text="🌡️ Temperatura:").pack(side=tk.LEFT)
        ttk.Label(
            marco_temp,
            text=f"{temperatura}°C",
            foreground='#e74c3c'
        ).pack(side=tk.RIGHT)

        # Humedad
        marco_hum = ttk.Frame(tarjeta)
        marco_hum.pack(fill=tk.X, padx=10)
        ttk.Label(marco_hum, text="💧 Humedad:").pack(side=tk.LEFT)
        ttk.Label(
            marco_hum,
            text=f"{humedad}%",
            foreground='#3498db'
        ).pack(side=tk.RIGHT)

        # Registrar en base de datos
        self.registrar_medicion(zona, temperatura, humedad)

    def registrar_medicion(self, zona, temperatura, humedad):
        """Guardar medición en la base de datos"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO registros 
            (zona, fecha, temperatura, humedad) 
            VALUES (?, ?, ?, ?)
        ''', (zona, datetime.now(), temperatura, humedad))
        self.conn.commit()

    def crear_grafico_historico(self, marco_padre):
        """Crear gráfico histórico de temperatura y humedad"""
        # Configurar el estilo de Seaborn para un aspecto más moderno
        sns.set_style("whitegrid")

        # Crear figura de Matplotlib
        figura = plt.Figure(figsize=(10, 4), dpi=100)
        ax = figura.add_subplot(111)

        # Obtener datos históricos
        datos_historicos = self.obtener_datos_historicos()

        # Preparar datos para gráfico
        zonas = list(set(registro[1] for registro in datos_historicos))

        # Graficar temperatura y humedad
        for zona in zonas:
            datos_zona = [
                registro for registro in datos_historicos
                if registro[1] == zona
            ]
            fechas = [datetime.strptime(registro[2], '%Y-%m-%d %H:%M:%S.%f') for registro in datos_zona]
            temperaturas = [registro[3] for registro in datos_zona]

            ax.plot(fechas, temperaturas, label=f'Temp {zona}')

        ax.set_title('Histórico de Temperatura por Zona', fontsize=12)
        ax.set_xlabel('Fecha', fontsize=10)
        ax.set_ylabel('Temperatura (°C)', fontsize=10)
        ax.legend()

        # Incrustar gráfico en Tkinter
        canvas = FigureCanvasTkAgg(figura, master=marco_padre)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.X, padx=10, pady=10)

    def obtener_datos_historicos(self, dias=1):
        """Obtener registros históricos"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM registros 
            WHERE fecha >= datetime('now', ?)
        ''', (f'-{dias} days',))

        return cursor.fetchall()

    def actualizar_datos(self):
        """Actualizar todos los datos y refrescar interfaz"""
        # Limpiar y recrear la interfaz
        for widget in self.root.winfo_children():
            widget.destroy()
        self.crear_interfaz_principal()

    def mostrar_alertas(self):
        """Mostrar ventana de alertas"""
        ventana_alertas = tk.Toplevel(self.root)
        ventana_alertas.title("Alertas Climáticas")
        ventana_alertas.geometry("400x300")

        # Título de alertas
        ttk.Label(
            ventana_alertas,
            text="Alertas Climáticas de Lima",
            font=('Arial', 16, 'bold')
        ).pack(pady=10)

        # Simular algunas alertas
        alertas = [
            "🔥 Temperatura alta en Centro de Lima",
            "💧 Humedad baja en Miraflores",
            "🌡️ Variación significativa en Callao"
        ]

        # Mostrar alertas
        for alerta in alertas:
            ttk.Label(
                ventana_alertas,
                text=alerta,
                foreground='red'
            ).pack(pady=5)

    def __del__(self):
        """Cerrar conexión de base de datos al destruir el objeto"""
        self.conn.close()


# Función principal
def main():
    root = tk.Tk()
    app = LimaClimaDashboard(root)
    root.mainloop()


if __name__ == "__main__":
    main()