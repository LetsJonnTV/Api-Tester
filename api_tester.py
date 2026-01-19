"""
API Tester Tool - Ein umfangreiches API-Testing-Tool
Erstellt mit Python, Tkinter und ttkbootstrap
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledFrame
import requests
import json
import time
import threading
from datetime import datetime
import os
import base64
from urllib.parse import urlencode
import xml.dom.minidom as minidom


class HeaderManager(ttkb.Toplevel):
    """Fenster zur Verwaltung von HTTP-Headers"""

    def __init__(self, parent, headers_dict):
        super().__init__(parent)
        self.title("Header Manager")
        self.geometry("600x400")
        self.headers_dict = headers_dict
        self.result = None

        self.create_widgets()
        self.load_headers()

        self.transient(parent)
        self.grab_set()

    def create_widgets(self):
        # Toolbar
        toolbar = ttkb.Frame(self)
        toolbar.pack(fill=X, padx=10, pady=5)

        ttkb.Button(toolbar, text="➕ Header hinzufügen", command=self.add_header, bootstyle="success-outline").pack(
            side=LEFT
        )
        ttkb.Button(
            toolbar, text="🗑️ Ausgewählte löschen", command=self.delete_selected, bootstyle="danger-outline"
        ).pack(side=LEFT, padx=5)

        # Treeview für Headers
        columns = ("enabled", "key", "value")
        self.tree = ttkb.Treeview(self, columns=columns, show="headings", height=12)
        self.tree.heading("enabled", text="✓")
        self.tree.heading("key", text="Header Name")
        self.tree.heading("value", text="Header Value")

        self.tree.column("enabled", width=40, anchor=CENTER)
        self.tree.column("key", width=200)
        self.tree.column("value", width=300)

        self.tree.pack(fill=BOTH, expand=True, padx=10, pady=5)
        self.tree.bind("<Double-1>", self.edit_header)

        # Buttons
        btn_frame = ttkb.Frame(self)
        btn_frame.pack(fill=X, padx=10, pady=10)

        ttkb.Button(btn_frame, text="Speichern", command=self.save_headers, bootstyle="success").pack(side=RIGHT)
        ttkb.Button(btn_frame, text="Abbrechen", command=self.destroy, bootstyle="secondary").pack(side=RIGHT, padx=5)

    def load_headers(self):
        for key, value in self.headers_dict.items():
            self.tree.insert("", END, values=("✓", key, value))

    def add_header(self):
        self.tree.insert("", END, values=("✓", "New-Header", "value"))

    def delete_selected(self):
        selected = self.tree.selection()
        for item in selected:
            self.tree.delete(item)

    def edit_header(self, event):
        item = self.tree.selection()
        if not item:
            return

        col = self.tree.identify_column(event.x)
        if col == "#1":  # Toggle enabled
            values = list(self.tree.item(item[0])["values"])
            values[0] = "" if values[0] == "✓" else "✓"
            self.tree.item(item[0], values=values)
        else:
            # Edit dialog
            EditDialog(self, self.tree, item[0], col)

    def save_headers(self):
        self.result = {}
        for item in self.tree.get_children():
            values = self.tree.item(item)["values"]
            if values[0] == "✓":
                self.result[values[1]] = values[2]
        self.destroy()


class EditDialog(ttkb.Toplevel):
    """Dialog zum Bearbeiten eines Wertes"""

    def __init__(self, parent, tree, item, col):
        super().__init__(parent)
        self.tree = tree
        self.item = item
        self.col_idx = int(col.replace("#", "")) - 1

        self.title("Wert bearbeiten")
        self.geometry("400x100")

        current_value = tree.item(item)["values"][self.col_idx]

        ttkb.Label(self, text="Neuer Wert:").pack(pady=5)
        self.entry = ttkb.Entry(self, width=50)
        self.entry.insert(0, current_value)
        self.entry.pack(pady=5)
        self.entry.focus_set()

        ttkb.Button(self, text="OK", command=self.save).pack(pady=5)
        self.entry.bind("<Return>", lambda e: self.save())

        self.transient(parent)
        self.grab_set()

    def save(self):
        values = list(self.tree.item(self.item)["values"])
        values[self.col_idx] = self.entry.get()
        self.tree.item(self.item, values=values)
        self.destroy()


class EnvironmentManager(ttkb.Toplevel):
    """Fenster zur Verwaltung von Umgebungsvariablen"""

    def __init__(self, parent, env_vars):
        super().__init__(parent)
        self.title("Environment Variables")
        self.geometry("600x400")
        self.env_vars = env_vars
        self.result = None

        self.create_widgets()
        self.load_vars()

        self.transient(parent)
        self.grab_set()

    def create_widgets(self):
        info_label = ttkb.Label(self, text="Verwende {{variable_name}} in URLs, Headers oder Body")
        info_label.pack(pady=5)

        toolbar = ttkb.Frame(self)
        toolbar.pack(fill=X, padx=10, pady=5)

        ttkb.Button(toolbar, text="➕ Variable hinzufügen", command=self.add_var, bootstyle="success-outline").pack(
            side=LEFT
        )
        ttkb.Button(toolbar, text="🗑️ Löschen", command=self.delete_selected, bootstyle="danger-outline").pack(
            side=LEFT, padx=5
        )

        columns = ("name", "value")
        self.tree = ttkb.Treeview(self, columns=columns, show="headings", height=12)
        self.tree.heading("name", text="Variable Name")
        self.tree.heading("value", text="Value")

        self.tree.column("name", width=200)
        self.tree.column("value", width=350)

        self.tree.pack(fill=BOTH, expand=True, padx=10, pady=5)
        self.tree.bind("<Double-1>", self.edit_var)

        btn_frame = ttkb.Frame(self)
        btn_frame.pack(fill=X, padx=10, pady=10)

        ttkb.Button(btn_frame, text="Speichern", command=self.save_vars, bootstyle="success").pack(side=RIGHT)
        ttkb.Button(btn_frame, text="Abbrechen", command=self.destroy, bootstyle="secondary").pack(side=RIGHT, padx=5)

    def load_vars(self):
        for name, value in self.env_vars.items():
            self.tree.insert("", END, values=(name, value))

    def add_var(self):
        self.tree.insert("", END, values=("NEW_VAR", "value"))

    def delete_selected(self):
        selected = self.tree.selection()
        for item in selected:
            self.tree.delete(item)

    def edit_var(self, event):
        item = self.tree.selection()
        if not item:
            return
        col = self.tree.identify_column(event.x)
        EditDialog(self, self.tree, item[0], col)

    def save_vars(self):
        self.result = {}
        for item in self.tree.get_children():
            values = self.tree.item(item)["values"]
            self.result[values[0]] = values[1]
        self.destroy()


class APITester(ttkb.Window):
    """Haupt-Anwendungsfenster"""

    def __init__(self):
        super().__init__(themename="darkly")

        self.title("🚀 API Tester Pro")
        self.geometry("1400x900")

        # Daten
        self.history = []
        self.collections = {}
        self.current_response = None
        self.headers = {"Content-Type": "application/json", "Accept": "application/json"}
        self.env_vars = {"base_url": "https://api.example.com", "api_key": "your-api-key"}
        self.auth_type = "none"
        self.auth_data = {}

        self.create_menu()
        self.create_widgets()
        self.load_saved_data()

    def create_menu(self):
        """Erstellt das Hauptmenü"""
        menubar = tk.Menu(self)

        # Datei-Menü
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Neuer Request", command=self.new_request, accelerator="Ctrl+N")
        file_menu.add_command(label="Request importieren", command=self.import_request)
        file_menu.add_command(label="Request exportieren", command=self.export_request)
        file_menu.add_separator()
        file_menu.add_command(label="Collection importieren", command=self.import_collection)
        file_menu.add_command(label="Collection exportieren", command=self.export_collection)
        file_menu.add_separator()
        file_menu.add_command(label="Beenden", command=self.quit)
        menubar.add_cascade(label="Datei", menu=file_menu)

        # Bearbeiten-Menü
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Headers verwalten", command=self.manage_headers)
        edit_menu.add_command(label="Environment Variables", command=self.manage_env_vars)
        edit_menu.add_separator()
        edit_menu.add_command(label="History löschen", command=self.clear_history)
        menubar.add_cascade(label="Bearbeiten", menu=edit_menu)

        # Tools-Menü
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="JSON Formatter", command=self.format_json)
        tools_menu.add_command(label="Base64 Encoder/Decoder", command=self.base64_tool)
        tools_menu.add_command(label="URL Encoder/Decoder", command=self.url_encode_tool)
        menubar.add_cascade(label="Tools", menu=tools_menu)

        # Themes-Menü
        themes_menu = tk.Menu(menubar, tearoff=0)
        for theme in [
            "darkly",
            "cyborg",
            "vapor",
            "solar",
            "superhero",
            "flatly",
            "journal",
            "litera",
            "minty",
            "pulse",
        ]:
            themes_menu.add_command(label=theme.capitalize(), command=lambda t=theme: self.change_theme(t))
        menubar.add_cascade(label="Themes", menu=themes_menu)

        # Hilfe-Menü
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Über", command=self.show_about)
        help_menu.add_command(label="Tastenkürzel", command=self.show_shortcuts)
        menubar.add_cascade(label="Hilfe", menu=help_menu)

        self.config(menu=menubar)

        # Keyboard shortcuts
        self.bind("<Control-n>", lambda e: self.new_request())
        self.bind("<Control-Return>", lambda e: self.send_request())
        self.bind("<F5>", lambda e: self.send_request())

    def create_widgets(self):
        """Erstellt alle Widgets"""

        # Hauptcontainer mit PanedWindow
        main_paned = ttkb.Panedwindow(self, orient=HORIZONTAL)
        main_paned.pack(fill=BOTH, expand=True, padx=5, pady=5)

        # Linke Sidebar (Collections & History)
        self.create_sidebar(main_paned)

        # Rechter Bereich (Request & Response)
        right_frame = ttkb.Frame(main_paned)
        main_paned.add(right_frame, weight=4)

        # Request-Bereich oben
        self.create_request_area(right_frame)

        # Response-Bereich unten
        self.create_response_area(right_frame)

    def create_sidebar(self, parent):
        """Erstellt die linke Sidebar"""
        sidebar = ttkb.Frame(parent, width=280)
        parent.add(sidebar, weight=1)

        # Notebook für Collections und History
        self.sidebar_notebook = ttkb.Notebook(sidebar)
        self.sidebar_notebook.pack(fill=BOTH, expand=True)

        # Collections Tab
        collections_frame = ttkb.Frame(self.sidebar_notebook)
        self.sidebar_notebook.add(collections_frame, text="📁 Collections")

        # Collection Toolbar
        coll_toolbar = ttkb.Frame(collections_frame)
        coll_toolbar.pack(fill=X, pady=5)

        ttkb.Button(coll_toolbar, text="➕", width=3, command=self.new_collection, bootstyle="success-outline").pack(
            side=LEFT, padx=2
        )
        ttkb.Button(coll_toolbar, text="📁", width=3, command=self.new_folder, bootstyle="info-outline").pack(
            side=LEFT, padx=2
        )
        ttkb.Button(
            coll_toolbar, text="💾", width=3, command=self.save_request_to_collection, bootstyle="warning-outline"
        ).pack(side=LEFT, padx=2)
        ttkb.Button(
            coll_toolbar, text="🗑️", width=3, command=self.delete_collection_item, bootstyle="danger-outline"
        ).pack(side=LEFT, padx=2)

        # Collections Treeview
        self.collections_tree = ttkb.Treeview(collections_frame, show="tree", height=15)
        self.collections_tree.pack(fill=BOTH, expand=True, padx=5, pady=5)
        self.collections_tree.bind("<Double-1>", self.load_from_collection)

        # Collection Context Menu
        self.collection_menu = tk.Menu(self, tearoff=0)
        self.collection_menu.add_command(label="📄 Load Request", command=self.load_from_collection)
        self.collection_menu.add_command(label="💾 Save Current Request Here", command=self.save_request_to_selected)
        self.collection_menu.add_separator()
        self.collection_menu.add_command(label="✏️ Rename", command=self.rename_collection_item)
        self.collection_menu.add_command(label="🗑️ Delete", command=self.delete_collection_item)
        self.collections_tree.bind("<Button-3>", self.show_collection_menu)

        # History Tab
        history_frame = ttkb.Frame(self.sidebar_notebook)
        self.sidebar_notebook.add(history_frame, text="📜 History")

        # History Suche
        search_frame = ttkb.Frame(history_frame)
        search_frame.pack(fill=X, padx=5, pady=5)

        self.history_search = ttkb.Entry(search_frame)
        self.history_search.pack(fill=X)
        self.history_search.bind("<KeyRelease>", self.filter_history)

        # History Liste
        self.history_listbox = tk.Listbox(
            history_frame, height=20, bg="#2b3e50", fg="white", selectbackground="#375a7f", font=("Consolas", 9)
        )
        self.history_listbox.pack(fill=BOTH, expand=True, padx=5, pady=5)
        self.history_listbox.bind("<Double-1>", self.load_from_history)

        # History Context Menu
        self.history_menu = tk.Menu(self, tearoff=0)
        self.history_menu.add_command(label="Load Request", command=self.load_selected_history)
        self.history_menu.add_command(label="Save to Collection", command=self.save_history_to_collection)
        self.history_menu.add_separator()
        self.history_menu.add_command(label="Delete", command=self.delete_history_item)
        self.history_listbox.bind("<Button-3>", self.show_history_menu)

    def create_request_area(self, parent):
        """Erstellt den Request-Bereich"""
        request_frame = ttkb.Labelframe(parent, text="📤 Request", padding=10)
        request_frame.pack(fill=X, padx=5, pady=5)

        # URL-Zeile
        url_frame = ttkb.Frame(request_frame)
        url_frame.pack(fill=X, pady=5)

        # HTTP Methode
        self.method_var = tk.StringVar(value="GET")
        self.method_combo = ttkb.Combobox(
            url_frame,
            textvariable=self.method_var,
            values=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"],
            width=10,
            state="readonly",
        )
        self.method_combo.pack(side=LEFT, padx=(0, 5))
        self.method_combo.bind("<<ComboboxSelected>>", self.on_method_change)

        # URL Eingabe
        self.url_entry = ttkb.Entry(url_frame, font=("Consolas", 11))
        self.url_entry.pack(side=LEFT, fill=X, expand=True, padx=5)
        self.url_entry.insert(0, "https://jsonplaceholder.typicode.com/posts")

        # Send Button
        self.send_btn = ttkb.Button(url_frame, text="🚀 Send", command=self.send_request, bootstyle="success", width=12)
        self.send_btn.pack(side=RIGHT, padx=(5, 0))

        # Request Notebook (Params, Headers, Body, Auth)
        self.request_notebook = ttkb.Notebook(request_frame)
        self.request_notebook.pack(fill=BOTH, expand=True, pady=10)

        # Query Parameters Tab
        params_frame = ttkb.Frame(self.request_notebook)
        self.request_notebook.add(params_frame, text="📝 Params")
        self.create_params_tab(params_frame)

        # Headers Tab
        headers_frame = ttkb.Frame(self.request_notebook)
        self.request_notebook.add(headers_frame, text="📋 Headers")
        self.create_headers_tab(headers_frame)

        # Body Tab
        body_frame = ttkb.Frame(self.request_notebook)
        self.request_notebook.add(body_frame, text="📦 Body")
        self.create_body_tab(body_frame)

        # Auth Tab
        auth_frame = ttkb.Frame(self.request_notebook)
        self.request_notebook.add(auth_frame, text="🔐 Auth")
        self.create_auth_tab(auth_frame)

        # Pre-Request Script Tab
        script_frame = ttkb.Frame(self.request_notebook)
        self.request_notebook.add(script_frame, text="📜 Pre-Request")
        self.create_script_tab(script_frame)

    def create_params_tab(self, parent):
        """Query Parameters Tab"""
        toolbar = ttkb.Frame(parent)
        toolbar.pack(fill=X, pady=5)

        ttkb.Button(toolbar, text="➕ Add Parameter", command=self.add_param, bootstyle="success-outline").pack(
            side=LEFT
        )

        columns = ("enabled", "key", "value", "description")
        self.params_tree = ttkb.Treeview(parent, columns=columns, show="headings", height=5)
        self.params_tree.heading("enabled", text="✓")
        self.params_tree.heading("key", text="Key")
        self.params_tree.heading("value", text="Value")
        self.params_tree.heading("description", text="Description")

        self.params_tree.column("enabled", width=40, anchor=CENTER)
        self.params_tree.column("key", width=150)
        self.params_tree.column("value", width=200)
        self.params_tree.column("description", width=150)

        self.params_tree.pack(fill=BOTH, expand=True, pady=5)
        self.params_tree.bind("<Double-1>", self.edit_param)

    def create_headers_tab(self, parent):
        """Headers Tab"""
        toolbar = ttkb.Frame(parent)
        toolbar.pack(fill=X, pady=5)

        ttkb.Button(toolbar, text="➕ Add Header", command=self.add_header, bootstyle="success-outline").pack(side=LEFT)
        ttkb.Button(toolbar, text="🔧 Common Headers", command=self.show_common_headers, bootstyle="info-outline").pack(
            side=LEFT, padx=5
        )

        columns = ("enabled", "key", "value")
        self.headers_tree = ttkb.Treeview(parent, columns=columns, show="headings", height=5)
        self.headers_tree.heading("enabled", text="✓")
        self.headers_tree.heading("key", text="Header")
        self.headers_tree.heading("value", text="Value")

        self.headers_tree.column("enabled", width=40, anchor=CENTER)
        self.headers_tree.column("key", width=200)
        self.headers_tree.column("value", width=300)

        self.headers_tree.pack(fill=BOTH, expand=True, pady=5)
        self.headers_tree.bind("<Double-1>", self.edit_header_tree)

        # Default Headers laden
        self.refresh_headers_tree()

    def create_body_tab(self, parent):
        """Body Tab"""
        # Body Type Selection
        type_frame = ttkb.Frame(parent)
        type_frame.pack(fill=X, pady=5)

        self.body_type = tk.StringVar(value="none")

        ttkb.Radiobutton(
            type_frame, text="none", variable=self.body_type, value="none", command=self.on_body_type_change
        ).pack(side=LEFT, padx=5)
        ttkb.Radiobutton(
            type_frame, text="raw (JSON)", variable=self.body_type, value="json", command=self.on_body_type_change
        ).pack(side=LEFT, padx=5)
        ttkb.Radiobutton(
            type_frame, text="form-data", variable=self.body_type, value="form-data", command=self.on_body_type_change
        ).pack(side=LEFT, padx=5)
        ttkb.Radiobutton(
            type_frame,
            text="x-www-form-urlencoded",
            variable=self.body_type,
            value="urlencoded",
            command=self.on_body_type_change,
        ).pack(side=LEFT, padx=5)
        ttkb.Radiobutton(
            type_frame, text="raw (XML)", variable=self.body_type, value="xml", command=self.on_body_type_change
        ).pack(side=LEFT, padx=5)
        ttkb.Radiobutton(
            type_frame, text="GraphQL", variable=self.body_type, value="graphql", command=self.on_body_type_change
        ).pack(side=LEFT, padx=5)

        # Body Content Container
        self.body_container = ttkb.Frame(parent)
        self.body_container.pack(fill=BOTH, expand=True, pady=5)

        # Raw Body Text
        self.body_text = scrolledtext.ScrolledText(
            self.body_container, font=("Consolas", 10), height=8, wrap=tk.WORD, bg="#1a1a2e", fg="#00ff00"
        )
        self.body_text.pack(fill=BOTH, expand=True)

        # Form Data Tree (initially hidden)
        self.form_tree_frame = ttkb.Frame(self.body_container)

        columns = ("enabled", "key", "value", "type")
        self.form_tree = ttkb.Treeview(self.form_tree_frame, columns=columns, show="headings", height=5)
        self.form_tree.heading("enabled", text="✓")
        self.form_tree.heading("key", text="Key")
        self.form_tree.heading("value", text="Value")
        self.form_tree.heading("type", text="Type")

        self.form_tree.column("enabled", width=40, anchor=CENTER)
        self.form_tree.column("key", width=150)
        self.form_tree.column("value", width=250)
        self.form_tree.column("type", width=80)

        ttkb.Button(self.form_tree_frame, text="➕ Add Field", command=self.add_form_field).pack(anchor=W, pady=5)
        self.form_tree.pack(fill=BOTH, expand=True)

    def create_auth_tab(self, parent):
        """Authentication Tab"""
        auth_type_frame = ttkb.Frame(parent)
        auth_type_frame.pack(fill=X, pady=10)

        ttkb.Label(auth_type_frame, text="Auth Type:").pack(side=LEFT, padx=5)

        self.auth_type_var = tk.StringVar(value="none")
        auth_types = ["none", "Basic Auth", "Bearer Token", "API Key", "OAuth 2.0"]

        self.auth_combo = ttkb.Combobox(
            auth_type_frame, textvariable=self.auth_type_var, values=auth_types, state="readonly", width=20
        )
        self.auth_combo.pack(side=LEFT, padx=5)
        self.auth_combo.bind("<<ComboboxSelected>>", self.on_auth_type_change)

        # Auth Config Container
        self.auth_config_frame = ttkb.Frame(parent)
        self.auth_config_frame.pack(fill=BOTH, expand=True, pady=10)

        # Basic Auth Frame
        self.basic_auth_frame = ttkb.Frame(self.auth_config_frame)
        ttkb.Label(self.basic_auth_frame, text="Username:").grid(row=0, column=0, padx=5, pady=5, sticky=W)
        self.auth_username = ttkb.Entry(self.basic_auth_frame, width=40)
        self.auth_username.grid(row=0, column=1, padx=5, pady=5)

        ttkb.Label(self.basic_auth_frame, text="Password:").grid(row=1, column=0, padx=5, pady=5, sticky=W)
        self.auth_password = ttkb.Entry(self.basic_auth_frame, width=40, show="*")
        self.auth_password.grid(row=1, column=1, padx=5, pady=5)

        # Bearer Token Frame
        self.bearer_frame = ttkb.Frame(self.auth_config_frame)
        ttkb.Label(self.bearer_frame, text="Token:").grid(row=0, column=0, padx=5, pady=5, sticky=W)
        self.bearer_token = ttkb.Entry(self.bearer_frame, width=60)
        self.bearer_token.grid(row=0, column=1, padx=5, pady=5)

        # API Key Frame
        self.apikey_frame = ttkb.Frame(self.auth_config_frame)
        ttkb.Label(self.apikey_frame, text="Key:").grid(row=0, column=0, padx=5, pady=5, sticky=W)
        self.api_key_name = ttkb.Entry(self.apikey_frame, width=30)
        self.api_key_name.grid(row=0, column=1, padx=5, pady=5)
        self.api_key_name.insert(0, "X-API-Key")

        ttkb.Label(self.apikey_frame, text="Value:").grid(row=1, column=0, padx=5, pady=5, sticky=W)
        self.api_key_value = ttkb.Entry(self.apikey_frame, width=40)
        self.api_key_value.grid(row=1, column=1, padx=5, pady=5)

        ttkb.Label(self.apikey_frame, text="Add to:").grid(row=2, column=0, padx=5, pady=5, sticky=W)
        self.api_key_location = ttkb.Combobox(
            self.apikey_frame, values=["Header", "Query Params"], state="readonly", width=20
        )
        self.api_key_location.grid(row=2, column=1, padx=5, pady=5, sticky=W)
        self.api_key_location.current(0)

    def create_script_tab(self, parent):
        """Pre-Request Script Tab"""
        info = ttkb.Label(parent, text="Pre-Request Script (JavaScript-ähnliche Syntax - zur Demo)")
        info.pack(pady=5)

        self.script_text = scrolledtext.ScrolledText(
            parent, font=("Consolas", 10), height=8, bg="#1a1a2e", fg="#00ff00"
        )
        self.script_text.pack(fill=BOTH, expand=True, pady=5)
        self.script_text.insert(
            "1.0", "// Beispiel Pre-Request Script\n// pm.variables.set('timestamp', Date.now());\n"
        )

    def create_response_area(self, parent):
        """Erstellt den Response-Bereich"""
        response_frame = ttkb.Labelframe(parent, text="📥 Response", padding=10)
        response_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)

        # Status Bar
        status_frame = ttkb.Frame(response_frame)
        status_frame.pack(fill=X, pady=5)

        self.status_label = ttkb.Label(status_frame, text="Status: --", font=("Consolas", 10))
        self.status_label.pack(side=LEFT, padx=10)

        self.time_label = ttkb.Label(status_frame, text="Time: --", font=("Consolas", 10))
        self.time_label.pack(side=LEFT, padx=10)

        self.size_label = ttkb.Label(status_frame, text="Size: --", font=("Consolas", 10))
        self.size_label.pack(side=LEFT, padx=10)

        # Response Notebook
        self.response_notebook = ttkb.Notebook(response_frame)
        self.response_notebook.pack(fill=BOTH, expand=True)

        # Body Tab
        body_resp_frame = ttkb.Frame(self.response_notebook)
        self.response_notebook.add(body_resp_frame, text="📄 Body")

        # Response Format Selection
        format_frame = ttkb.Frame(body_resp_frame)
        format_frame.pack(fill=X, pady=5)

        self.response_format = tk.StringVar(value="pretty")
        ttkb.Radiobutton(
            format_frame, text="Pretty", variable=self.response_format, value="pretty", command=self.format_response
        ).pack(side=LEFT, padx=5)
        ttkb.Radiobutton(
            format_frame, text="Raw", variable=self.response_format, value="raw", command=self.format_response
        ).pack(side=LEFT, padx=5)
        ttkb.Radiobutton(
            format_frame, text="Preview", variable=self.response_format, value="preview", command=self.format_response
        ).pack(side=LEFT, padx=5)

        ttkb.Button(format_frame, text="📋 Copy", command=self.copy_response, bootstyle="info-outline").pack(
            side=RIGHT, padx=5
        )
        ttkb.Button(format_frame, text="💾 Save", command=self.save_response, bootstyle="success-outline").pack(
            side=RIGHT, padx=5
        )
        ttkb.Button(format_frame, text="🔍 Search", command=self.search_response, bootstyle="secondary-outline").pack(
            side=RIGHT, padx=5
        )

        self.response_text = scrolledtext.ScrolledText(
            body_resp_frame, font=("Consolas", 10), height=15, wrap=tk.WORD, bg="#1a1a2e", fg="#00ff00"
        )
        self.response_text.pack(fill=BOTH, expand=True, pady=5)

        # Headers Tab
        headers_resp_frame = ttkb.Frame(self.response_notebook)
        self.response_notebook.add(headers_resp_frame, text="📋 Headers")

        self.response_headers_text = scrolledtext.ScrolledText(
            headers_resp_frame, font=("Consolas", 10), height=15, wrap=tk.WORD, bg="#1a1a2e", fg="#e0e0e0"
        )
        self.response_headers_text.pack(fill=BOTH, expand=True, pady=5)

        # Cookies Tab
        cookies_frame = ttkb.Frame(self.response_notebook)
        self.response_notebook.add(cookies_frame, text="🍪 Cookies")

        self.cookies_text = scrolledtext.ScrolledText(
            cookies_frame, font=("Consolas", 10), height=15, wrap=tk.WORD, bg="#1a1a2e", fg="#e0e0e0"
        )
        self.cookies_text.pack(fill=BOTH, expand=True, pady=5)

        # Test Results Tab
        tests_frame = ttkb.Frame(self.response_notebook)
        self.response_notebook.add(tests_frame, text="✅ Tests")

        self.tests_text = scrolledtext.ScrolledText(
            tests_frame, font=("Consolas", 10), height=15, wrap=tk.WORD, bg="#1a1a2e", fg="#e0e0e0"
        )
        self.tests_text.pack(fill=BOTH, expand=True, pady=5)

    # ========================
    # Event Handlers & Methods
    # ========================

    def send_request(self):
        """Sendet den HTTP Request"""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Warnung", "Bitte URL eingeben!")
            return

        # Environment Variables ersetzen
        url = self.replace_env_vars(url)

        # Query Parameters hinzufügen
        params = self.get_query_params()
        if params:
            url = f"{url}?{urlencode(params)}"

        method = self.method_var.get()
        headers = self.get_request_headers()
        body = self.get_request_body()
        auth = self.get_auth()

        # UI Update
        self.send_btn.config(state="disabled", text="⏳ Sending...")
        self.status_label.config(text="Status: Sending...", bootstyle="warning")

        # Request in Thread ausführen
        thread = threading.Thread(target=self._execute_request, args=(method, url, headers, body, auth))
        thread.daemon = True
        thread.start()

    def _execute_request(self, method, url, headers, body, auth):
        """Führt den Request aus (in separatem Thread)"""
        start_time = time.time()

        try:
            kwargs = {"headers": headers, "timeout": 30, "verify": True}

            if auth:
                kwargs["auth"] = auth

            if body and method in ["POST", "PUT", "PATCH"]:
                body_type = self.body_type.get()
                if body_type == "json":
                    kwargs["json"] = json.loads(body) if isinstance(body, str) else body
                elif body_type in ["form-data", "urlencoded"]:
                    kwargs["data"] = body
                else:
                    kwargs["data"] = body

            response = requests.request(method, url, **kwargs)
            elapsed_time = time.time() - start_time

            self.current_response = response

            # UI Update im Main Thread
            self.after(0, lambda: self._update_response_ui(response, elapsed_time))

            # History speichern
            self.after(0, lambda: self._add_to_history(method, url, response.status_code, elapsed_time))

        except requests.exceptions.Timeout:
            self.after(0, lambda: self._show_error("Timeout - Server antwortet nicht"))
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Verbindungsfehler: {str(e)}"
            self.after(0, lambda msg=error_msg: self._show_error(msg))
        except json.JSONDecodeError as e:
            error_msg = f"JSON Parse Error: {str(e)}"
            self.after(0, lambda msg=error_msg: self._show_error(msg))
        except Exception as e:
            error_msg = f"Fehler: {str(e)}"
            self.after(0, lambda msg=error_msg: self._show_error(msg))
        finally:
            self.after(0, lambda: self.send_btn.config(state="normal", text="🚀 Send"))

    def _update_response_ui(self, response, elapsed_time):
        """Aktualisiert die Response-Anzeige"""
        # Status
        status_code = response.status_code
        status_text = f"Status: {status_code} {response.reason}"

        if status_code < 300:
            bootstyle = "success"
        elif status_code < 400:
            bootstyle = "info"
        elif status_code < 500:
            bootstyle = "warning"
        else:
            bootstyle = "danger"

        self.status_label.config(text=status_text, bootstyle=bootstyle)

        # Time
        self.time_label.config(text=f"Time: {elapsed_time * 1000:.0f}ms")

        # Size
        size = len(response.content)
        if size < 1024:
            size_str = f"{size} B"
        elif size < 1024 * 1024:
            size_str = f"{size / 1024:.2f} KB"
        else:
            size_str = f"{size / (1024 * 1024):.2f} MB"
        self.size_label.config(text=f"Size: {size_str}")

        # Response Body
        self.response_text.delete("1.0", tk.END)
        try:
            content_type = response.headers.get("Content-Type", "")
            if "json" in content_type:
                formatted = json.dumps(response.json(), indent=2, ensure_ascii=False)
                self.response_text.insert("1.0", formatted)
            elif "xml" in content_type:
                try:
                    dom = minidom.parseString(response.text)
                    formatted = dom.toprettyxml(indent="  ")
                    self.response_text.insert("1.0", formatted)
                except:
                    self.response_text.insert("1.0", response.text)
            else:
                self.response_text.insert("1.0", response.text)
        except:
            self.response_text.insert("1.0", response.text)

        # Response Headers
        self.response_headers_text.delete("1.0", tk.END)
        headers_str = "\n".join([f"{k}: {v}" for k, v in response.headers.items()])
        self.response_headers_text.insert("1.0", headers_str)

        # Cookies
        self.cookies_text.delete("1.0", tk.END)
        cookies_str = "\n".join([f"{k}: {v}" for k, v in response.cookies.items()])
        self.cookies_text.insert("1.0", cookies_str if cookies_str else "No cookies")

        # Automatische Tests
        self._run_automatic_tests(response, elapsed_time)

    def _run_automatic_tests(self, response, elapsed_time):
        """Führt automatische Tests durch"""
        self.tests_text.delete("1.0", tk.END)

        tests = []

        # Status Code Test
        if response.status_code < 400:
            tests.append("✅ Status Code is successful")
        else:
            tests.append(f"❌ Status Code {response.status_code} indicates error")

        # Response Time Test
        if elapsed_time < 1:
            tests.append(f"✅ Response time ({elapsed_time * 1000:.0f}ms) is acceptable")
        else:
            tests.append(f"⚠️ Response time ({elapsed_time * 1000:.0f}ms) is slow")

        # Content Type Test
        content_type = response.headers.get("Content-Type", "")
        if content_type:
            tests.append(f"✅ Content-Type header present: {content_type}")
        else:
            tests.append("⚠️ No Content-Type header")

        # JSON Validity Test
        if "json" in content_type:
            try:
                response.json()
                tests.append("✅ Response is valid JSON")
            except:
                tests.append("❌ Response is not valid JSON")

        self.tests_text.insert("1.0", "\n".join(tests))

    def _show_error(self, message):
        """Zeigt Fehlermeldung an"""
        self.status_label.config(text=f"Status: Error", bootstyle="danger")
        self.response_text.delete("1.0", tk.END)
        self.response_text.insert("1.0", f"Error: {message}")

    def _add_to_history(self, method, url, status_code, elapsed_time):
        """Fügt Request zur History hinzu"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = {"timestamp": timestamp, "method": method, "url": url, "status": status_code, "time": elapsed_time}
        self.history.insert(0, entry)

        # History UI aktualisieren
        display = f"[{timestamp}] {method} {url[:50]}... → {status_code}"
        self.history_listbox.insert(0, display)

        # Max 100 Einträge
        if len(self.history) > 100:
            self.history.pop()
            self.history_listbox.delete(100)

    def get_query_params(self):
        """Holt Query Parameters aus dem Tree"""
        params = {}
        for item in self.params_tree.get_children():
            values = self.params_tree.item(item)["values"]
            if values[0] == "✓" and values[1]:
                params[values[1]] = self.replace_env_vars(str(values[2]))
        return params

    def get_request_headers(self):
        """Holt Headers aus dem Tree"""
        headers = {}
        for item in self.headers_tree.get_children():
            values = self.headers_tree.item(item)["values"]
            if values[0] == "✓":
                headers[values[1]] = self.replace_env_vars(str(values[2]))
        return headers

    def get_request_body(self):
        """Holt den Request Body"""
        body_type = self.body_type.get()

        if body_type == "none":
            return None
        elif body_type in ["json", "xml", "graphql"]:
            return self.replace_env_vars(self.body_text.get("1.0", tk.END).strip())
        elif body_type in ["form-data", "urlencoded"]:
            data = {}
            for item in self.form_tree.get_children():
                values = self.form_tree.item(item)["values"]
                if values[0] == "✓":
                    data[values[1]] = self.replace_env_vars(str(values[2]))
            return data
        return None

    def get_auth(self):
        """Holt Authentication Daten"""
        auth_type = self.auth_type_var.get()

        if auth_type == "Basic Auth":
            username = self.auth_username.get()
            password = self.auth_password.get()
            return (username, password)
        elif auth_type == "Bearer Token":
            token = self.bearer_token.get()
            # Bearer Token wird in Headers gesetzt
            return None
        elif auth_type == "API Key":
            # API Key wird in Headers/Params gesetzt
            return None
        return None

    def replace_env_vars(self, text):
        """Ersetzt Environment Variables in Text"""
        for var, value in self.env_vars.items():
            text = text.replace(f"{{{{{var}}}}}", str(value))
        return text

    def refresh_headers_tree(self):
        """Aktualisiert Headers Tree"""
        for item in self.headers_tree.get_children():
            self.headers_tree.delete(item)
        for key, value in self.headers.items():
            self.headers_tree.insert("", END, values=("✓", key, value))

    def on_method_change(self, event=None):
        """Handler für Methoden-Änderung"""
        method = self.method_var.get()
        if method in ["POST", "PUT", "PATCH"]:
            if self.body_type.get() == "none":
                self.body_type.set("json")
                self.on_body_type_change()

    def on_body_type_change(self):
        """Handler für Body-Type-Änderung"""
        body_type = self.body_type.get()

        # Alle Body-Widgets verstecken
        self.body_text.pack_forget()
        self.form_tree_frame.pack_forget()

        if body_type in ["none"]:
            pass
        elif body_type in ["json", "xml", "graphql"]:
            self.body_text.pack(fill=BOTH, expand=True)
            if body_type == "json" and not self.body_text.get("1.0", tk.END).strip():
                self.body_text.insert("1.0", '{\n  "key": "value"\n}')
            elif body_type == "graphql" and not self.body_text.get("1.0", tk.END).strip():
                self.body_text.insert("1.0", "query {\n  users {\n    id\n    name\n  }\n}")
        else:
            self.form_tree_frame.pack(fill=BOTH, expand=True)

    def on_auth_type_change(self, event=None):
        """Handler für Auth-Type-Änderung"""
        auth_type = self.auth_type_var.get()

        # Alle Auth-Frames verstecken
        self.basic_auth_frame.pack_forget()
        self.bearer_frame.pack_forget()
        self.apikey_frame.pack_forget()

        if auth_type == "Basic Auth":
            self.basic_auth_frame.pack(anchor=W)
        elif auth_type == "Bearer Token":
            self.bearer_frame.pack(anchor=W)
        elif auth_type == "API Key":
            self.apikey_frame.pack(anchor=W)

    # ========================
    # UI Helper Methods
    # ========================

    def add_param(self):
        self.params_tree.insert("", END, values=("✓", "key", "value", ""))

    def edit_param(self, event):
        item = self.params_tree.selection()
        if item:
            col = self.params_tree.identify_column(event.x)
            if col == "#1":
                values = list(self.params_tree.item(item[0])["values"])
                values[0] = "" if values[0] == "✓" else "✓"
                self.params_tree.item(item[0], values=values)
            else:
                EditDialog(self, self.params_tree, item[0], col)

    def add_header(self):
        self.headers_tree.insert("", END, values=("✓", "Header-Name", "value"))

    def edit_header_tree(self, event):
        item = self.headers_tree.selection()
        if item:
            col = self.headers_tree.identify_column(event.x)
            if col == "#1":
                values = list(self.headers_tree.item(item[0])["values"])
                values[0] = "" if values[0] == "✓" else "✓"
                self.headers_tree.item(item[0], values=values)
            else:
                EditDialog(self, self.headers_tree, item[0], col)

    def add_form_field(self):
        self.form_tree.insert("", END, values=("✓", "key", "value", "text"))

    def show_common_headers(self):
        """Zeigt Common Headers Dialog"""
        common = {
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "User-Agent": "API-Tester/1.0",
        }

        dialog = ttkb.Toplevel(self)
        dialog.title("Common Headers")
        dialog.geometry("400x300")

        for header, value in common.items():
            frame = ttkb.Frame(dialog)
            frame.pack(fill=X, padx=10, pady=2)
            ttkb.Button(
                frame,
                text="Add",
                width=5,
                command=lambda h=header, v=value: self._add_common_header(h, v, dialog),
                bootstyle="success-outline",
            ).pack(side=LEFT)
            ttkb.Label(frame, text=f"{header}: {value}").pack(side=LEFT, padx=10)

    def _add_common_header(self, header, value, dialog):
        self.headers_tree.insert("", END, values=("✓", header, value))

    def filter_history(self, event=None):
        """Filtert History nach Suchbegriff"""
        search = self.history_search.get().lower()
        self.history_listbox.delete(0, tk.END)

        for entry in self.history:
            display = f"[{entry['timestamp']}] {entry['method']} {entry['url'][:50]}... → {entry['status']}"
            if search in display.lower():
                self.history_listbox.insert(tk.END, display)

    def load_from_history(self, event=None):
        """Lädt Request aus History"""
        selection = self.history_listbox.curselection()
        if not selection:
            return

        # Finde entsprechenden History-Eintrag
        idx = selection[0]
        if idx < len(self.history):
            entry = self.history[idx]
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, entry["url"])
            self.method_var.set(entry["method"])

    def show_history_menu(self, event):
        """Zeigt Context Menu für History"""
        try:
            self.history_listbox.selection_clear(0, tk.END)
            self.history_listbox.selection_set(self.history_listbox.nearest(event.y))
            self.history_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.history_menu.grab_release()

    def load_selected_history(self):
        self.load_from_history()

    def save_history_to_collection(self):
        """Speichert History-Eintrag in Collection"""
        selection = self.history_listbox.curselection()
        if not selection:
            return

        # Lade zuerst den History-Eintrag
        self.load_from_history()
        # Dann zeige Save-Dialog
        self._show_save_to_collection_dialog()

    def delete_history_item(self):
        """Löscht History-Eintrag"""
        selection = self.history_listbox.curselection()
        if selection:
            idx = selection[0]
            self.history_listbox.delete(idx)
            if idx < len(self.history):
                self.history.pop(idx)

    def format_response(self):
        """Formatiert Response basierend auf Auswahl"""
        if not self.current_response:
            return

        fmt = self.response_format.get()
        self.response_text.delete("1.0", tk.END)

        if fmt == "pretty":
            try:
                formatted = json.dumps(self.current_response.json(), indent=2, ensure_ascii=False)
                self.response_text.insert("1.0", formatted)
            except:
                self.response_text.insert("1.0", self.current_response.text)
        elif fmt == "raw":
            self.response_text.insert("1.0", self.current_response.text)
        else:
            self.response_text.insert("1.0", self.current_response.text)

    def copy_response(self):
        """Kopiert Response in Zwischenablage"""
        content = self.response_text.get("1.0", tk.END)
        self.clipboard_clear()
        self.clipboard_append(content)
        messagebox.showinfo("Info", "Response in Zwischenablage kopiert!")

    def save_response(self):
        """Speichert Response als Datei"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json", filetypes=[("JSON", "*.json"), ("Text", "*.txt"), ("All", "*.*")]
        )
        if filename:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(self.response_text.get("1.0", tk.END))
            messagebox.showinfo("Info", f"Response gespeichert: {filename}")

    def search_response(self):
        """Sucht in Response"""
        search_dialog = ttkb.Toplevel(self)
        search_dialog.title("Suchen")
        search_dialog.geometry("300x100")

        ttkb.Label(search_dialog, text="Suchen:").pack(pady=5)
        search_entry = ttkb.Entry(search_dialog, width=40)
        search_entry.pack(pady=5)

        def do_search():
            term = search_entry.get()
            content = self.response_text.get("1.0", tk.END)

            # Tags zurücksetzen
            self.response_text.tag_remove("highlight", "1.0", tk.END)

            if term:
                start = "1.0"
                while True:
                    pos = self.response_text.search(term, start, stopindex=tk.END)
                    if not pos:
                        break
                    end = f"{pos}+{len(term)}c"
                    self.response_text.tag_add("highlight", pos, end)
                    start = end

                self.response_text.tag_config("highlight", background="yellow", foreground="black")

        ttkb.Button(search_dialog, text="Suchen", command=do_search).pack(pady=5)

    # ========================
    # Menu Actions
    # ========================

    def new_request(self):
        """Neuer Request"""
        self.url_entry.delete(0, tk.END)
        self.method_var.set("GET")
        self.body_text.delete("1.0", tk.END)
        self.response_text.delete("1.0", tk.END)
        self.response_headers_text.delete("1.0", tk.END)
        self.status_label.config(text="Status: --")
        self.time_label.config(text="Time: --")
        self.size_label.config(text="Size: --")

    def import_request(self):
        """Importiert Request aus Datei"""
        filename = filedialog.askopenfilename(filetypes=[("JSON", "*.json"), ("All", "*.*")])
        if filename:
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    data = json.load(f)

                self.url_entry.delete(0, tk.END)
                self.url_entry.insert(0, data.get("url", ""))
                self.method_var.set(data.get("method", "GET"))

                if "body" in data:
                    self.body_text.delete("1.0", tk.END)
                    self.body_text.insert("1.0", json.dumps(data["body"], indent=2))
                    self.body_type.set("json")
                    self.on_body_type_change()

                if "headers" in data:
                    self.headers = data["headers"]
                    self.refresh_headers_tree()

                messagebox.showinfo("Info", "Request importiert!")
            except Exception as e:
                messagebox.showerror("Fehler", f"Import fehlgeschlagen: {e}")

    def export_request(self):
        """Exportiert aktuellen Request"""
        data = {
            "url": self.url_entry.get(),
            "method": self.method_var.get(),
            "headers": self.get_request_headers(),
            "body": self.get_request_body(),
        }

        filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if filename:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            messagebox.showinfo("Info", f"Request exportiert: {filename}")

    def import_collection(self):
        """Importiert Collection (Postman-Format)"""
        filename = filedialog.askopenfilename(filetypes=[("JSON", "*.json"), ("All", "*.*")])
        if filename:
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    collection = json.load(f)

                # Postman Collection Format
                name = collection.get("info", {}).get("name", "Imported")
                items = collection.get("item", [])

                node = self.collections_tree.insert("", END, text=f"📁 {name}")

                for item in items:
                    item_name = item.get("name", "Request")
                    self.collections_tree.insert(node, END, text=f"📄 {item_name}")

                self.collections[name] = collection
                messagebox.showinfo("Info", f"Collection '{name}' importiert!")
            except Exception as e:
                messagebox.showerror("Fehler", f"Import fehlgeschlagen: {e}")

    def export_collection(self):
        """Exportiert Collection"""
        # TODO: Implementieren
        messagebox.showinfo("Info", "Collection-Export wird hinzugefügt")

    def new_collection(self):
        """Erstellt neue Collection"""
        name = tk.simpledialog.askstring("Neue Collection", "Name der Collection:")
        if name:
            node_id = self.collections_tree.insert("", END, text=f"📁 {name}")
            self.collections[node_id] = {"name": name, "type": "collection", "items": {}}

    def new_folder(self):
        """Erstellt neuen Ordner in Collection"""
        selected = self.collections_tree.selection()
        if selected:
            name = tk.simpledialog.askstring("Neuer Ordner", "Name des Ordners:")
            if name:
                node_id = self.collections_tree.insert(selected[0], END, text=f"📂 {name}")
                self.collections[node_id] = {"name": name, "type": "folder", "items": {}}
        else:
            messagebox.showwarning("Warnung", "Bitte zuerst eine Collection auswählen!")

    def get_current_request_data(self):
        """Holt alle aktuellen Request-Daten"""
        return {
            "url": self.url_entry.get(),
            "method": self.method_var.get(),
            "headers": self.get_request_headers(),
            "body": self.get_request_body(),
            "body_type": self.body_type.get(),
            "params": self.get_query_params(),
            "auth_type": self.auth_type_var.get(),
            "auth_data": {
                "username": self.auth_username.get() if hasattr(self, "auth_username") else "",
                "password": self.auth_password.get() if hasattr(self, "auth_password") else "",
                "bearer_token": self.bearer_token.get() if hasattr(self, "bearer_token") else "",
                "api_key_name": self.api_key_name.get() if hasattr(self, "api_key_name") else "",
                "api_key_value": self.api_key_value.get() if hasattr(self, "api_key_value") else "",
            },
        }

    def save_request_to_collection(self):
        """Speichert aktuellen Request in ausgewählte Collection/Folder"""
        selected = self.collections_tree.selection()
        if not selected:
            # Zeige Dialog um Collection auszuwählen
            self._show_save_to_collection_dialog()
            return
        self._save_request_to_node(selected[0])

    def save_request_to_selected(self):
        """Speichert Request in den ausgewählten Node"""
        selected = self.collections_tree.selection()
        if selected:
            self._save_request_to_node(selected[0])

    def _show_save_to_collection_dialog(self):
        """Zeigt Dialog zum Speichern in Collection"""
        dialog = ttkb.Toplevel(self)
        dialog.title("Save to Collection")
        dialog.geometry("400x300")
        dialog.transient(self)
        dialog.grab_set()

        ttkb.Label(dialog, text="Request Name:").pack(pady=5)
        name_entry = ttkb.Entry(dialog, width=40)
        name_entry.pack(pady=5)
        name_entry.insert(0, f"{self.method_var.get()} {self.url_entry.get()[:30]}")

        ttkb.Label(dialog, text="Wähle Collection oder Ordner:").pack(pady=5)

        # Treeview für Collection-Auswahl
        tree = ttkb.Treeview(dialog, show="tree", height=8)
        tree.pack(fill=BOTH, expand=True, padx=10, pady=5)

        # Kopiere Collection-Struktur
        def copy_tree(source_tree, target_tree, source_item="", target_item=""):
            for child in source_tree.get_children(source_item):
                text = source_tree.item(child)["text"]
                # Nur Collections und Ordner, keine Requests
                if "📁" in text or "📂" in text:
                    new_item = target_tree.insert(target_item, END, text=text)
                    target_tree.item(new_item, tags=(child,))  # Original ID als Tag
                    copy_tree(source_tree, target_tree, child, new_item)

        copy_tree(self.collections_tree, tree)

        def save():
            selection = tree.selection()
            request_name = name_entry.get().strip()
            if not request_name:
                messagebox.showwarning("Warnung", "Bitte Request-Name eingeben!")
                return
            if not selection:
                messagebox.showwarning("Warnung", "Bitte Collection oder Ordner auswählen!")
                return

            # Finde Original Node ID
            tags = tree.item(selection[0])["tags"]
            if tags:
                original_id = tags[0]
                self._save_request_to_node(original_id, request_name)
                dialog.destroy()

        ttkb.Button(dialog, text="💾 Speichern", command=save, bootstyle="success").pack(pady=10)

    def _save_request_to_node(self, node_id, custom_name=None):
        """Speichert Request in einen bestimmten Node"""
        request_data = self.get_current_request_data()

        # Request Name
        if custom_name:
            name = custom_name
        else:
            name = tk.simpledialog.askstring(
                "Request Name",
                "Name für den Request:",
                initialvalue=f"{request_data['method']} {request_data['url'][:30]}",
            )
        if not name:
            return

        # Request zum Tree hinzufügen
        method = request_data["method"]
        method_colors = {"GET": "🟢", "POST": "🟡", "PUT": "🟠", "PATCH": "🟣", "DELETE": "🔴"}
        color = method_colors.get(method, "⚪")

        request_node = self.collections_tree.insert(node_id, END, text=f"{color} {method} {name}")

        # Request-Daten speichern
        self.collections[request_node] = {"name": name, "type": "request", "data": request_data}

        messagebox.showinfo("Erfolg", f"Request '{name}' gespeichert!")

    def load_from_collection(self, event=None):
        """Lädt Request aus Collection"""
        selected = self.collections_tree.selection()
        if not selected:
            return

        node_id = selected[0]
        if node_id not in self.collections:
            return

        item = self.collections[node_id]
        if item.get("type") != "request":
            return

        data = item.get("data", {})

        # URL laden
        self.url_entry.delete(0, tk.END)
        self.url_entry.insert(0, data.get("url", ""))

        # Method setzen
        self.method_var.set(data.get("method", "GET"))

        # Body Type setzen
        self.body_type.set(data.get("body_type", "none"))
        self.on_body_type_change()

        # Body laden
        body = data.get("body", "")
        if body and isinstance(body, (dict, list)):
            body = json.dumps(body, indent=2)
        self.body_text.delete("1.0", tk.END)
        if body:
            self.body_text.insert("1.0", str(body))

        # Headers laden
        headers = data.get("headers", {})
        for item in self.headers_tree.get_children():
            self.headers_tree.delete(item)
        for key, value in headers.items():
            self.headers_tree.insert("", END, values=("✓", key, value))

        # Parameters laden
        params = data.get("params", {})
        for item in self.params_tree.get_children():
            self.params_tree.delete(item)
        for key, value in params.items():
            self.params_tree.insert("", END, values=("✓", key, value, ""))

        # Auth laden
        auth_type = data.get("auth_type", "none")
        self.auth_type_var.set(auth_type)
        self.on_auth_type_change()

        auth_data = data.get("auth_data", {})
        if auth_data.get("username"):
            self.auth_username.delete(0, tk.END)
            self.auth_username.insert(0, auth_data["username"])
        if auth_data.get("password"):
            self.auth_password.delete(0, tk.END)
            self.auth_password.insert(0, auth_data["password"])
        if auth_data.get("bearer_token"):
            self.bearer_token.delete(0, tk.END)
            self.bearer_token.insert(0, auth_data["bearer_token"])

        messagebox.showinfo("Geladen", f"Request geladen!")

    def show_collection_menu(self, event):
        """Zeigt Context Menu für Collections"""
        item = self.collections_tree.identify_row(event.y)
        if item:
            self.collections_tree.selection_set(item)
            self.collection_menu.tk_popup(event.x_root, event.y_root)

    def delete_collection_item(self):
        """Löscht ausgewähltes Element aus Collection"""
        selected = self.collections_tree.selection()
        if not selected:
            messagebox.showwarning("Warnung", "Bitte Element auswählen!")
            return

        if messagebox.askyesno("Bestätigung", "Element wirklich löschen?"):
            node_id = selected[0]

            # Rekursiv alle Kind-Elemente aus collections dict entfernen
            def remove_recursive(nid):
                for child in self.collections_tree.get_children(nid):
                    remove_recursive(child)
                if nid in self.collections:
                    del self.collections[nid]

            remove_recursive(node_id)
            self.collections_tree.delete(node_id)

    def rename_collection_item(self):
        """Benennt Element um"""
        selected = self.collections_tree.selection()
        if not selected:
            return

        node_id = selected[0]
        current_text = self.collections_tree.item(node_id)["text"]

        # Icon extrahieren
        icon = current_text[:2] if current_text else ""
        current_name = current_text[2:].strip() if len(current_text) > 2 else current_text

        new_name = tk.simpledialog.askstring("Umbenennen", "Neuer Name:", initialvalue=current_name)
        if new_name:
            self.collections_tree.item(node_id, text=f"{icon} {new_name}")
            if node_id in self.collections:
                self.collections[node_id]["name"] = new_name

    def manage_headers(self):
        """Öffnet Header Manager"""
        dialog = HeaderManager(self, self.headers)
        self.wait_window(dialog)
        if dialog.result:
            self.headers = dialog.result
            self.refresh_headers_tree()

    def manage_env_vars(self):
        """Öffnet Environment Manager"""
        dialog = EnvironmentManager(self, self.env_vars)
        self.wait_window(dialog)
        if dialog.result:
            self.env_vars = dialog.result

    def clear_history(self):
        """Löscht gesamte History"""
        if messagebox.askyesno("Bestätigung", "Gesamte History löschen?"):
            self.history.clear()
            self.history_listbox.delete(0, tk.END)

    def format_json(self):
        """JSON Formatter Tool"""
        dialog = ttkb.Toplevel(self)
        dialog.title("JSON Formatter")
        dialog.geometry("600x500")

        ttkb.Label(dialog, text="JSON Input:").pack(pady=5)
        input_text = scrolledtext.ScrolledText(dialog, height=10, font=("Consolas", 10))
        input_text.pack(fill=X, padx=10, pady=5)

        def format_it():
            try:
                data = json.loads(input_text.get("1.0", tk.END))
                formatted = json.dumps(data, indent=2, ensure_ascii=False)
                output_text.delete("1.0", tk.END)
                output_text.insert("1.0", formatted)
            except Exception as e:
                output_text.delete("1.0", tk.END)
                output_text.insert("1.0", f"Error: {e}")

        def minify_it():
            try:
                data = json.loads(input_text.get("1.0", tk.END))
                minified = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
                output_text.delete("1.0", tk.END)
                output_text.insert("1.0", minified)
            except Exception as e:
                output_text.delete("1.0", tk.END)
                output_text.insert("1.0", f"Error: {e}")

        btn_frame = ttkb.Frame(dialog)
        btn_frame.pack(pady=5)
        ttkb.Button(btn_frame, text="Format", command=format_it, bootstyle="success").pack(side=LEFT, padx=5)
        ttkb.Button(btn_frame, text="Minify", command=minify_it, bootstyle="info").pack(side=LEFT, padx=5)

        ttkb.Label(dialog, text="Output:").pack(pady=5)
        output_text = scrolledtext.ScrolledText(dialog, height=10, font=("Consolas", 10))
        output_text.pack(fill=X, padx=10, pady=5)

    def base64_tool(self):
        """Base64 Encoder/Decoder"""
        dialog = ttkb.Toplevel(self)
        dialog.title("Base64 Encoder/Decoder")
        dialog.geometry("500x400")

        ttkb.Label(dialog, text="Input:").pack(pady=5)
        input_text = scrolledtext.ScrolledText(dialog, height=6, font=("Consolas", 10))
        input_text.pack(fill=X, padx=10, pady=5)

        def encode():
            text = input_text.get("1.0", tk.END).strip()
            encoded = base64.b64encode(text.encode()).decode()
            output_text.delete("1.0", tk.END)
            output_text.insert("1.0", encoded)

        def decode():
            text = input_text.get("1.0", tk.END).strip()
            try:
                decoded = base64.b64decode(text).decode()
                output_text.delete("1.0", tk.END)
                output_text.insert("1.0", decoded)
            except Exception as e:
                output_text.delete("1.0", tk.END)
                output_text.insert("1.0", f"Error: {e}")

        btn_frame = ttkb.Frame(dialog)
        btn_frame.pack(pady=5)
        ttkb.Button(btn_frame, text="Encode", command=encode, bootstyle="success").pack(side=LEFT, padx=5)
        ttkb.Button(btn_frame, text="Decode", command=decode, bootstyle="info").pack(side=LEFT, padx=5)

        ttkb.Label(dialog, text="Output:").pack(pady=5)
        output_text = scrolledtext.ScrolledText(dialog, height=6, font=("Consolas", 10))
        output_text.pack(fill=X, padx=10, pady=5)

    def url_encode_tool(self):
        """URL Encoder/Decoder"""
        from urllib.parse import quote, unquote

        dialog = ttkb.Toplevel(self)
        dialog.title("URL Encoder/Decoder")
        dialog.geometry("500x400")

        ttkb.Label(dialog, text="Input:").pack(pady=5)
        input_text = scrolledtext.ScrolledText(dialog, height=6, font=("Consolas", 10))
        input_text.pack(fill=X, padx=10, pady=5)

        def encode():
            text = input_text.get("1.0", tk.END).strip()
            encoded = quote(text)
            output_text.delete("1.0", tk.END)
            output_text.insert("1.0", encoded)

        def decode():
            text = input_text.get("1.0", tk.END).strip()
            decoded = unquote(text)
            output_text.delete("1.0", tk.END)
            output_text.insert("1.0", decoded)

        btn_frame = ttkb.Frame(dialog)
        btn_frame.pack(pady=5)
        ttkb.Button(btn_frame, text="Encode", command=encode, bootstyle="success").pack(side=LEFT, padx=5)
        ttkb.Button(btn_frame, text="Decode", command=decode, bootstyle="info").pack(side=LEFT, padx=5)

        ttkb.Label(dialog, text="Output:").pack(pady=5)
        output_text = scrolledtext.ScrolledText(dialog, height=6, font=("Consolas", 10))
        output_text.pack(fill=X, padx=10, pady=5)

    def change_theme(self, theme):
        """Ändert das Theme"""
        self.style.theme_use(theme)

    def show_about(self):
        """Zeigt About Dialog"""
        messagebox.showinfo(
            "Über API Tester Pro",
            "API Tester Pro v1.0\n\n"
            "Ein umfangreiches API-Testing-Tool\n"
            "Erstellt mit Python, Tkinter und ttkbootstrap\n\n"
            "Features:\n"
            "• HTTP Methods: GET, POST, PUT, PATCH, DELETE\n"
            "• Headers & Query Parameters\n"
            "• Multiple Body Types (JSON, Form, XML, GraphQL)\n"
            "• Authentication (Basic, Bearer, API Key)\n"
            "• Request History & Collections\n"
            "• Environment Variables\n"
            "• Response Formatting\n"
            "• Built-in Tools (JSON, Base64, URL)\n"
            "• Multiple Themes",
        )

    def show_shortcuts(self):
        """Zeigt Tastenkürzel"""
        messagebox.showinfo(
            "Tastenkürzel", "Ctrl+N: Neuer Request\nCtrl+Enter / F5: Request senden\nCtrl+S: Response speichern"
        )

    def load_saved_data(self):
        """Lädt gespeicherte Daten"""
        config_file = os.path.join(os.path.dirname(__file__), "api_tester_config.json")
        if os.path.exists(config_file):
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.env_vars = data.get("env_vars", self.env_vars)
                    self.headers = data.get("headers", self.headers)
                    self.refresh_headers_tree()
            except:
                pass

    def save_data(self):
        """Speichert Daten"""
        config_file = os.path.join(os.path.dirname(__file__), "api_tester_config.json")
        data = {"env_vars": self.env_vars, "headers": self.headers}
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def destroy(self):
        """Cleanup beim Beenden"""
        self.save_data()
        super().destroy()


if __name__ == "__main__":
    import tkinter.simpledialog

    app = APITester()
    app.mainloop()
