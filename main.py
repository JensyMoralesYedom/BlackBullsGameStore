import tkinter as tk
from tkinter import messagebox

class TiendaJuegos:
    def __init__(self, root):
        self.root = root
        self.root.title("GameStore - Plataforma Digital")
        self.root.geometry("950x600")
        self.root.configure(bg="#0b0f19") # Fondo oscuro principal
        self.root.resizable(False, False)
        
        self.color_acento = "#7c3aed" # Púrpura neón
        self.color_panel = "#1e293b"
        self.color_texto = "#f8fafc"
        
        self.mostrar_login()

    def limpiar_ventana(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def crear_entrada_elegante(self, master, texto_label, es_clave=False):
        frame = tk.Frame(master, bg=self.color_panel)
        frame.pack(fill="x", padx=40, pady=(10, 15))
        
        lbl = tk.Label(frame, text=texto_label, font=("Segoe UI", 10), bg=self.color_panel, fg="#94a3b8", anchor="w")
        lbl.pack(fill="x")
        
        entrada = tk.Entry(frame, font=("Segoe UI", 12), bg=self.color_panel, fg=self.color_texto, 
                           insertbackground=self.color_texto, bd=0, show="*" if es_clave else "")
        entrada.pack(fill="x", pady=(5, 0))
        
        linea = tk.Frame(frame, bg="#475569", height=2)
        linea.pack(fill="x")
        
        # Efecto hover en la línea inferior
        entrada.bind("<FocusIn>", lambda e: linea.configure(bg=self.color_acento))
        entrada.bind("<FocusOut>", lambda e: linea.configure(bg="#475569"))
        
        return entrada

    def mostrar_login(self):
        self.limpiar_ventana()
        
        # Tarjeta central
        frame_login = tk.Frame(self.root, bg=self.color_panel)
        frame_login.place(relx=0.5, rely=0.5, anchor="center", width=380, height=520)
        
        # Título arriba
        lbl_titulo = tk.Label(frame_login, text="GAMESTORE", font=("Segoe UI Black", 24), bg=self.color_panel, fg=self.color_texto)
        lbl_titulo.pack(pady=(30, 10))
        
        # Imagen debajo del título
        try:
            self.logo_login = tk.PhotoImage(file="logo_tienda.png")
            lbl_img = tk.Label(frame_login, image=self.logo_login, bg=self.color_panel)
            lbl_img.pack(pady=(0, 20))
        except Exception:
            espaciador = tk.Frame(frame_login, bg=self.color_panel, height=80)
            espaciador.pack(pady=(0, 20))
        
        self.crear_entrada_elegante(frame_login, "NOMBRE DE USUARIO")
        self.crear_entrada_elegante(frame_login, "CONTRASEÑA", es_clave=True)
        
        btn_ingresar = tk.Button(frame_login, text="INICIAR SESIÓN", font=("Segoe UI", 11, "bold"), 
                                 bg=self.color_acento, fg="white", bd=0, cursor="hand2",
                                 activebackground="#5b21b6", activeforeground="white", command=self.mostrar_menu)
        btn_ingresar.pack(fill="x", padx=40, pady=(20, 0), ipady=8)

    def mostrar_menu(self):
        self.limpiar_ventana()
        
        # Barra lateral
        sidebar = tk.Frame(self.root, bg="#0f172a", width=230)
        sidebar.pack(side="left", fill="y")
        
        # Título arriba en el menú
        lbl_logo_texto = tk.Label(sidebar, text="GAMESTORE", font=("Segoe UI Black", 16), bg="#0f172a", fg=self.color_acento)
        lbl_logo_texto.pack(pady=(25, 10))
        
        # Imagen debajo del título en el menú
        try:
            self.logo_menu = tk.PhotoImage(file="menu_tienda.png")
            lbl_img_menu = tk.Label(sidebar, image=self.logo_menu, bg="#0f172a")
            lbl_img_menu.pack(pady=(0, 20))
        except Exception:
            pass
            
        opciones = [
            ("Descubrir", self.mostrar_mensaje_construccion),
            ("Tienda", self.mostrar_mensaje_construccion),
            ("Biblioteca", self.mostrar_mensaje_construccion),
            ("Comunidad", self.mostrar_mensaje_construccion),
            ("Ajustes", self.mostrar_mensaje_construccion)
        ]
        
        for texto, comando in opciones:
            btn = tk.Button(sidebar, text=f"   {texto}", font=("Segoe UI", 11), bg="#0f172a", fg="#cbd5e1", 
                            bd=0, anchor="w", cursor="hand2", activebackground="#1e293b", activeforeground="white", 
                            command=comando)
            btn.pack(fill="x", pady=5, padx=10, ipady=8)
            
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg="#1e293b", fg="white"))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(bg="#0f172a", fg="#cbd5e1"))
        
        btn_salir = tk.Button(sidebar, text="Cerrar sesión", font=("Segoe UI", 10, "bold"), bg="#1e293b", fg="#ef4444", 
                              bd=0, cursor="hand2", activebackground="#7f1d1d", activeforeground="white", 
                              command=self.mostrar_login)
        btn_salir.pack(side="bottom", fill="x", pady=20, padx=20, ipady=8)
        
        # Contenido Principal (Simulación de Dashboard)
        contenido = tk.Frame(self.root, bg=self.root["bg"])
        contenido.pack(side="right", fill="both", expand=True)
        
        header = tk.Frame(contenido, bg=self.root["bg"], height=60)
        header.pack(fill="x", padx=30, pady=20)
        
        lbl_bienvenida = tk.Label(header, text="Destacados de hoy", font=("Segoe UI", 22, "bold"), bg=self.root["bg"], fg=self.color_texto)
        lbl_bienvenida.pack(side="left")
        
        banner = tk.Frame(contenido, bg=self.color_panel, bd=0)
        banner.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        
        lbl_banner_tag = tk.Label(banner, text="NUEVO LANZAMIENTO", font=("Segoe UI", 10, "bold"), bg=self.color_panel, fg=self.color_acento)
        lbl_banner_tag.pack(anchor="w", padx=40, pady=(40, 5))
        
        lbl_banner_titulo = tk.Label(banner, text="Cyberpunk Adventures", font=("Segoe UI Black", 28), bg=self.color_panel, fg=self.color_texto)
        lbl_banner_titulo.pack(anchor="w", padx=35)
        
        lbl_banner_desc = tk.Label(banner, text="Explora un mundo abierto lleno de neón, misiones \ny gráficos de última generación. Disponible ahora.", 
                                   font=("Segoe UI", 12), bg=self.color_panel, fg="#94a3b8", justify="left")
        lbl_banner_desc.pack(anchor="w", padx=40, pady=15)
        
        btn_comprar = tk.Button(banner, text="COMPRAR AHORA", font=("Segoe UI", 11, "bold"), bg=self.color_acento, fg="white", 
                                bd=0, cursor="hand2", activebackground="#5b21b6", activeforeground="white", command=self.mostrar_mensaje_construccion)
        btn_comprar.pack(anchor="w", padx=40, pady=10, ipady=8, ipadx=20)

    def mostrar_mensaje_construccion(self):
        messagebox.showinfo("Información del Sistema", "Este módulo se encuentra en construcción.")

if __name__ == "__main__":
    root = tk.Tk()
    app = TiendaJuegos(root)
    root.mainloop()