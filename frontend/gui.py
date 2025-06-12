from tkinter import messagebox
import customtkinter as ctk
import os
import shutil
from datetime import datetime
from tkinter import ttk, filedialog

from backend.file_operations import FileOperations
from backend.drive_detector import DriveDetector
from backend.logger import AppLogger

class FileManagerGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.source_path_to_copy = None
        self.destination_selection_mode = False
        self.source_path_to_move = None
        self.confirm_destination_button = None

        self.file_operations = FileOperations()
        self.drive_detector = DriveDetector()
        self.logger = AppLogger()

        self.title("Gerenciador de Arquivos")
        
        # Centralizar a janela na tela
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = 1200
        window_height = 800
        x_cordinate = int((screen_width/2) - (window_width/2))
        y_cordinate = int((screen_height/2) - (window_height/2))
        self.geometry(f"{window_width}x{window_height}+{x_cordinate}+{y_cordinate}")

        # Configurar o tema para escuro
        ctk.set_appearance_mode("Dark")  # Força o tema escuro
        ctk.set_default_color_theme("blue")
        print(f"CTK Appearance Mode: {ctk.get_appearance_mode()}")

        # Definir uma fonte mais bonita (exemplo: 'Segoe UI' para Windows, 'Roboto' ou 'Ubuntu' para Linux)
        # A disponibilidade da fonte pode variar por sistema operacional
        try:
            self.default_font = ctk.CTkFont(family="Segoe UI", size=12) # Tenta Segoe UI
            self.bold_font = ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
            self.logo_font = ctk.CTkFont(family="Segoe UI", size=20, weight="bold")
        except Exception: # Fallback para fonte padrão se a desejada não estiver disponível
            self.default_font = ctk.CTkFont(size=12)
            self.bold_font = ctk.CTkFont(size=14, weight="bold")
            self.logo_font = ctk.CTkFont(size=20, weight="bold")

        # Aplicar fonte aos widgets
        # self.option_add("*Font", self.default_font) # Removido para evitar conflitos com CTkFont

        # Configurar o grid principal
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1) # Coluna para a lista de arquivos

        # Frame da barra lateral para a árvore de diretórios e drives
        self.sidebar_frame = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(1, weight=1) # Permite que a treeview expanda

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Gerenciador", font=self.logo_font)
        self.logo_label.grid(row=0, column=0, padx=20, pady=20)

        # Treeview para a árvore de diretórios
        self.tree = ttk.Treeview(self.sidebar_frame, selectmode="browse")
        self.tree.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # Estilo para a Treeview (para aplicar a fonte)
        style = ttk.Style()
        style.theme_use("clam")  # Garante que o tema padrão do ttk seja usado para estilização
        style.configure("Treeview", font=self.default_font, rowheight=25, background="#2b2b2b", fieldbackground="#2b2b2b", foreground="#ffffff", bordercolor="#444444", borderwidth=1)
        style.map("Treeview", background=[("selected", "#444444")], foreground=[("selected", "#ffffff")])
        style.configure("Treeview.Heading", font=self.bold_font)

        # Scrollbar para a treeview
        self.tree_scrollbar = ctk.CTkScrollbar(self.sidebar_frame, command=self.tree.yview)
        self.tree_scrollbar.grid(row=1, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=self.tree_scrollbar.set)

        # Label para exibir o caminho atual
        self.current_path_label = ctk.CTkLabel(self, text="Caminho Atual: ", font=self.bold_font)
        self.current_path_label.grid(row=0, column=1, padx=20, pady=10, sticky="nw")
        
        self.path_entry = ctk.CTkEntry(self, placeholder_text="Digite o caminho e pressione Enter", font=self.default_font)
        self.path_entry.grid(row=0, column=1, padx=20, pady=(40, 10), sticky="new")
        self.path_entry.bind("<Return>", self.on_path_enter)

        # Frame para a lista de arquivos/pastas (agora com colunas para detalhes)
        self.file_list_frame = ctk.CTkFrame(self)
        self.file_list_frame.grid(row=1, column=1, padx=20, pady=10, sticky="nsew")
        self.file_list_frame.grid_columnconfigure(0, weight=1)
        self.file_list_frame.grid_rowconfigure(0, weight=1)

        # Treeview para a lista de arquivos com detalhes
        self.file_tree = ttk.Treeview(self.file_list_frame, columns=("Tipo", "Tamanho", "Data de Modificação"), show="tree headings") # CORRIGIDO AQUI
        self.file_tree.heading("#0", text="Nome")
        self.file_tree.heading("Tipo", text="Tipo")
        self.file_tree.heading("Tamanho", text="Tamanho")
        self.file_tree.heading("Data de Modificação", text="Data de Modificação")

        self.file_tree.column("#0", width=350, stretch=ctk.NO) # Aumenta a largura da coluna de nome
        self.file_tree.column("Tipo", width=100, stretch=ctk.NO)
        self.file_tree.column("Tamanho", width=100, stretch=ctk.NO)
        self.file_tree.column("Data de Modificação", width=150, stretch=ctk.NO)

        self.file_tree.grid(row=0, column=0, sticky="nsew")
        self.file_tree.bind("<Double-1>", self.on_file_double_click)

        # Scrollbar para a file_tree
        self.file_tree_scrollbar_y = ctk.CTkScrollbar(self.file_list_frame, command=self.file_tree.yview)
        self.file_tree_scrollbar_y.grid(row=0, column=1, sticky="ns")
        self.file_tree.configure(yscrollcommand=self.file_tree_scrollbar_y.set)

        self.file_tree_scrollbar_x = ctk.CTkScrollbar(self.file_list_frame, orientation="horizontal", command=self.file_tree.xview)
        self.file_tree_scrollbar_x.grid(row=1, column=0, sticky="ew")
        self.file_tree.configure(xscrollcommand=self.file_tree_scrollbar_x.set)

        # Botões de operação
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.grid(row=2, column=1, padx=20, pady=10, sticky="ew")
        self.button_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        self.copy_button = ctk.CTkButton(self.button_frame, text="Copiar", command=self.copy_action, font=self.default_font)
        self.copy_button.grid(row=0, column=0, padx=10, pady=10)

        self.move_button = ctk.CTkButton(self.button_frame, text="Mover", command=self.move_action, font=self.default_font)
        self.move_button.grid(row=0, column=1, padx=10, pady=10)

        self.rename_button = ctk.CTkButton(self.button_frame, text="Renomear", command=self.rename_action, font=self.default_font)
        self.rename_button.grid(row=0, column=2, padx=10, pady=10)

        self.delete_button = ctk.CTkButton(self.button_frame, text="Excluir", command=self.delete_action, font=self.default_font)
        self.delete_button.grid(row=0, column=3, padx=10, pady=10)

        self.open_button = ctk.CTkButton(self.button_frame, text="Abrir", command=self.open_action, font=self.default_font)
        self.open_button.grid(row=0, column=4, padx=10, pady=10)

        # Label para mensagens de status
        self.status_label = ctk.CTkLabel(self, text="", text_color="green", font=self.default_font)
        self.status_label.grid(row=3, column=1, padx=20, pady=5, sticky="sw")

        self.populate_sidebar_tree()
        self.load_directory(os.path.expanduser("~")) # Carrega o diretório inicial (home do usuário)

    def display_message(self, message, is_error=False):
        self.status_label.configure(text=message, text_color="red" if is_error else "green")

    def populate_sidebar_tree(self):
        self.tree.delete(*self.tree.get_children()) # Limpa a treeview

        # Seção de Acesso Rápido
        quick_access_node = self.tree.insert("", "end", text="Acesso Rápido", open=True, tags=("header",))
        common_paths = {
            "Área de Trabalho": os.path.join(os.path.expanduser("~"), "Desktop"),
            "Downloads": os.path.join(os.path.expanduser("~"), "Downloads"),
            "Documentos": os.path.join(os.path.expanduser("~"), "Onedrive//Documents"),
            "Imagens": os.path.join(os.path.expanduser("~"), "OneDrive//Pictures"),
            "Músicas": os.path.join(os.path.expanduser("~"), "Music"),
            "Vídeos": os.path.join(os.path.expanduser("~"), "Videos"),
        }
        for name, path in common_paths.items():
            if os.path.exists(path):
                self.tree.insert(quick_access_node, "end", text=name, values=[path], open=False, tags=("folder",))

        # Seção Este Computador
        this_pc_node = self.tree.insert("", "end", text="Este Computador", open=True, tags=("header",))
        drives = self.drive_detector.get_mounted_drives()
        for drive in drives:
            mountpoint = drive["mountpoint"]
            is_removable = drive["is_removable"]
            display_name = f"{mountpoint}"
            if is_removable:
                display_name += " (Removível)"
            
            drive_node = self.tree.insert(this_pc_node, "end", text=display_name, values=[mountpoint], open=False, tags=("drive",))
            self.populate_directory_tree(drive_node, mountpoint)

        # Estilo para os cabeçalhos da Treeview
        self.tree.tag_configure("header", font=self.bold_font)

    def populate_directory_tree(self, parent_node, path):
        try:
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    # Adiciona um placeholder para que o usuário possa expandir
                    self.tree.insert(parent_node, "end", text=item, values=[item_path], open=False, tags=("folder",))
        except PermissionError:
            self.logger.warning(f"Permissão negada para acessar: {path}")
        except Exception as e:
            self.logger.error(f"Erro ao popular árvore de diretórios para {path}: {e}")

    def on_tree_select(self, event):
        selected_item = self.tree.focus()
        if selected_item:
            # Verifica se o item selecionado é um nó de categoria (Acesso Rápido, Este Computador)
            item_tags = self.tree.item(selected_item, "tags")
            if "header" in item_tags:
                return # Não faz nada se for um nó de categoria

            path = self.tree.item(selected_item, "values")[0]
            if os.path.isdir(path):
                self.load_directory(path)
                # Se o nó não foi expandido, preenche-o
                if not self.tree.item(selected_item, "open"):
                    self.tree.delete(*self.tree.get_children(selected_item)) # Limpa placeholders
                    self.populate_directory_tree(selected_item, path)
                    self.tree.item(selected_item, open=True)
                    if self.destination_selection_mode:
                        self.tree.selection_set(selected_item)  # destaca a seleção

    def load_directory(self, path):
        self.current_path = path
        self.current_path_label.configure(text=f"Caminho Atual: {self.current_path}")
        
        # Limpa a file_tree atual
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)

        # Adiciona um item para voltar ao diretório pai
        if self.current_path != os.path.abspath(os.sep):
            self.file_tree.insert("", "end", text="..", values=["Pasta", "", ""], tags=("folder", "parent"))

        # Lista arquivos e pastas com detalhes
        try:
            contents = sorted(os.listdir(path), key=lambda s: s.lower())
            for item in contents:
                item_path = os.path.join(path, item)
                try:
                    if os.path.isdir(item_path):
                        self.file_tree.insert("", "end", text=item, values=["Pasta", "", datetime.fromtimestamp(os.path.getmtime(item_path)).strftime("%d/%m/%Y %H:%M")], tags=("folder",))
                    elif os.path.isfile(item_path):
                        size = os.path.getsize(item_path)
                        mod_time = datetime.fromtimestamp(os.path.getmtime(item_path)).strftime("%d/%m/%Y %H:%M")
                        file_type = "Arquivo"
                        if "." in item:
                            file_type = item.split(".")[-1].upper() + " Arquivo"
                        self.file_tree.insert("", "end", text=item, values=[file_type, self.format_size(size), mod_time], tags=("file",))
                except PermissionError:
                    self.logger.warning(f"Permissão negada para acessar: {item_path}")
                except Exception as e:
                    self.logger.error(f"Erro ao obter detalhes de {item_path}: {e}")
        except PermissionError:
            self.display_message("Permissão negada para acessar este diretório.", is_error=True)
        except Exception as e:
            self.display_message(f"Erro ao carregar diretório: {e}", is_error=True)

    def format_size(self, size_bytes):
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.2f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.2f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"

    def on_file_double_click(self, event):
        selected_item = self.file_tree.focus()
        if selected_item:
            item_text = self.file_tree.item(selected_item, "text")
            if item_text == "..":
                self.go_back()
            else:
                item_path = os.path.join(self.current_path, item_text)
                if os.path.isdir(item_path):
                    self.load_directory(item_path)

    def go_back(self):
        parent_path = os.path.dirname(self.current_path)
        if parent_path != self.current_path: # Evita ir para o diretório raiz infinitamente
            self.load_directory(parent_path)

    def copy_action(self):
        selected_item = self.file_tree.focus()
        if not selected_item:
            self.display_message("Selecione um arquivo ou pasta para copiar.", is_error=True)
            return

        source_name = self.file_tree.item(selected_item, "text")
        source_path = os.path.join(self.current_path, source_name)

        if source_name == "..":
            self.display_message("Não é possível copiar o diretório pai.", is_error=True)
            return

        self.display_message("Selecione o diretório de destino na árvore lateral e clique em 'Confirmar cópia'")
        self.destination_selection_mode = "copy"
        self.source_path_to_copy = source_path

        if not self.confirm_destination_button:
            self.confirm_destination_button = ctk.CTkButton(
                self.sidebar_frame,
                text="Colar neste destino",
                command=self.confirm_copy_destination,
                font=self.default_font
            )
            self.confirm_destination_button.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

    def confirm_copy_destination(self):
        selected_item = self.tree.focus()
        if not selected_item:
            self.display_message("Selecione um destino válido.", is_error=True)
            return

        dest_path = self.tree.item(selected_item, "values")[0]
        if not os.path.isdir(dest_path):
            self.display_message("Destino inválido.", is_error=True)
            return

        filename = os.path.basename(self.source_path_to_copy)
        destination = os.path.join(dest_path, filename)

        success, message = self.file_operations.copy_file(self.source_path_to_copy, destination)
        self.display_message(message, not success)

        # Reset
        self.destination_selection_mode = False
        self.source_path_to_copy = None
        if self.confirm_destination_button:
            self.confirm_destination_button.destroy()
            self.confirm_destination_button = None

        self.load_directory(self.current_path)            

    def move_action(self):
        selected_item = self.file_tree.focus()
        if not selected_item:
            self.display_message("Selecione um arquivo ou pasta para mover.", is_error=True)
            return

        source_name = self.file_tree.item(selected_item, "text")
        source_path = os.path.join(self.current_path, source_name)

        if source_name == "..":
            self.display_message("Não é possível mover o diretório pai.", is_error=True)
            return

        self.display_message("Selecione o diretório de destino na árvore lateral e clique em 'Confirmar destino'")
        self.destination_selection_mode = True
        self.source_path_to_move = source_path

        if not self.confirm_destination_button:
            self.confirm_destination_button = ctk.CTkButton(
                self.sidebar_frame,
                text="Confirmar destino",
                command=self.confirm_move_destination,
                font=self.default_font
            )
            self.confirm_destination_button.grid(row=2, column=0, padx=10, pady=10, sticky="ew") # Sempre recarrega o diretório de origem após mover
    
    def confirm_move_destination(self):
        selected_item = self.tree.focus()
        if not selected_item:
            self.display_message("Selecione um destino válido.", is_error=True)
            return

        dest_path = self.tree.item(selected_item, "values")[0]
        if not os.path.isdir(dest_path):
            self.display_message("Destino inválido.", is_error=True)
            return

        filename = os.path.basename(self.source_path_to_move)
        destination = os.path.join(dest_path, filename)

        success, message = self.file_operations.move_file(self.source_path_to_move, destination)
        self.display_message(message, not success)

        # Reset
        self.destination_selection_mode = False
        self.source_path_to_move = None
        if self.confirm_destination_button:
            self.confirm_destination_button.destroy()
            self.confirm_destination_button = None

        self.load_directory(self.current_path)  # Atualiza pasta atual        

    def rename_action(self):
        selected_item = self.file_tree.focus()
        if not selected_item:
            self.display_message("Selecione um arquivo ou pasta para renomear.", is_error=True)
            return

        current_name = self.file_tree.item(selected_item, "text")
        current_path = os.path.join(self.current_path, current_name)

        if current_name == "..":
            self.display_message("Não é possível renomear o diretório pai.", is_error=True)
            return

        dialog = ctk.CTkInputDialog(text=f"Renomear \"{current_name}\":", title="Renomear")
        new_name = dialog.get_input()

        if new_name and new_name != current_name:
            success, message = self.file_operations.rename_file(current_path, new_name)
            self.display_message(message, not success)
            if success:
                self.load_directory(self.current_path)
        elif new_name == current_name:
            self.display_message("Nenhuma alteração no nome.")
        else:
            self.display_message("Operação de renomear cancelada.")

    def delete_action(self):
        selected_item = self.file_tree.focus()
        if not selected_item:
            self.display_message("Selecione um arquivo ou pasta para excluir.", is_error=True)
            return

        item_name = self.file_tree.item(selected_item, "text")
        item_path = os.path.join(self.current_path, item_name)

        if item_name == "..":
            self.display_message("Não é possível excluir o diretório pai.", is_error=True)
            return

        # Diálogo de confirmação
        response = messagebox.askquestion(
            "Confirmar Exclusão",
            f"Tem certeza que deseja excluir \"{item_name}\"? Esta ação não pode ser desfeita."
        )

        if response == "yes":
            success, message = self.file_operations.delete_file(item_path)
            self.display_message(message, not success)
            if success:
                self.load_directory(self.current_path)
        else:
            self.display_message("Operação de exclusão cancelada.")
    
    def on_path_enter(self, event):
        new_path = self.path_entry.get()
        if os.path.isdir(new_path):
            self.load_directory(new_path)
        else:
            self.display_message("Caminho inválido ou inacessível.", is_error=True)
            
    def open_action(self):
        selected_item = self.file_tree.focus()
        if not selected_item:
            self.display_message("Selecione um arquivo ou pasta para abrir.", is_error=True)
            return

        item_name = self.file_tree.item(selected_item, "text")
        item_path = os.path.join(self.current_path, item_name)

        if item_name == "..":
            self.display_message("Não é possível abrir o diretório pai assim.", is_error=True)
            return

        try:
            os.startfile(item_path)
            self.display_message(f"Abrindo: {item_name}")
        except Exception as e:
            self.display_message(f"Erro ao abrir: {e}", is_error=True)        

if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")  # Força o tema escuro
    ctk.set_default_color_theme("blue")  # Themes: "blue" (default), "green", "dark-blue"

    app = FileManagerGUI()
    app.mainloop()


