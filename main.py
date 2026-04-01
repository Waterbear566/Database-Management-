"""
Student Database Management Studio
Professional DBMS Interface inspired by SQL Server Management Studio
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from database import StudentDatabase
from sql_parser import SQLParser
import json
import os
from datetime import datetime


class DBManagementStudio:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Database Management Studio")
        self.root.geometry("1600x900")
        self.root.state('zoomed')  # Maximize window
        
        # Color scheme - Professional dark theme
        self.colors = {
            'bg_dark': '#1e1e1e',
            'bg_medium': '#252526',
            'bg_light': '#2d2d30',
            'fg_normal': '#cccccc',
            'fg_bright': '#ffffff',
            'accent': '#007acc',
            'success': '#4ec9b0',
            'error': '#f48771',
            'warning': '#dcdcaa',
            'border': '#3e3e42'
        }
        
        # Configure root
        self.root.configure(bg=self.colors['bg_dark'])
        
        # Initialize database and SQL parser
        self.db = StudentDatabase()
        self.sql_parser = SQLParser(self.db)
        self.current_file = None
        
        # Create UI
        self.create_menu_bar()
        self.create_main_layout()
        
        # Load sample data
        self.db.load_sample_data()
        self.refresh_all()
    
    def create_menu_bar(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root, bg=self.colors['bg_medium'], fg=self.colors['fg_normal'])
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['bg_medium'], fg=self.colors['fg_normal'])
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Database", command=self.new_database, accelerator="Ctrl+N")
        file_menu.add_command(label="Open Database...", command=self.open_database, accelerator="Ctrl+O")
        file_menu.add_command(label="Save Database", command=self.save_database, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self.save_database_as)
        file_menu.add_separator()
        file_menu.add_command(label="Export to JSON...", command=self.export_to_json)
        file_menu.add_command(label="Import from JSON...", command=self.import_from_json)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['bg_medium'], fg=self.colors['fg_normal'])
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Clear All Data", command=self.clear_all_data)
        edit_menu.add_command(label="Load Sample Data", command=self.load_sample_data)
        
        # Query menu
        query_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['bg_medium'], fg=self.colors['fg_normal'])
        menubar.add_cascade(label="Query", menu=query_menu)
        query_menu.add_command(label="Execute Query", command=self.execute_query, accelerator="F5")
        query_menu.add_command(label="Clear Query", command=self.clear_query)
        query_menu.add_separator()
        query_menu.add_command(label="SELECT Template", command=lambda: self.insert_template("SELECT"))
        query_menu.add_command(label="INSERT Template", command=lambda: self.insert_template("INSERT"))
        query_menu.add_command(label="UPDATE Template", command=lambda: self.insert_template("UPDATE"))
        query_menu.add_command(label="DELETE Template", command=lambda: self.insert_template("DELETE"))
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['bg_medium'], fg=self.colors['fg_normal'])
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Refresh All", command=self.refresh_all, accelerator="F5")
        view_menu.add_command(label="Show B-Tree Index", command=self.show_btree_window)
        view_menu.add_command(label="Show Statistics", command=self.show_statistics)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['bg_medium'], fg=self.colors['fg_normal'])
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="SQL Command Reference", command=self.show_sql_help)
        help_menu.add_command(label="About", command=self.show_about)
        
        # Keyboard shortcuts
        self.root.bind('<Control-n>', lambda e: self.new_database())
        self.root.bind('<Control-o>', lambda e: self.open_database())
        self.root.bind('<Control-s>', lambda e: self.save_database())
        self.root.bind('<F5>', lambda e: self.execute_query())
    
    def create_main_layout(self):
        """Create main layout with panels"""
        # Main container
        main_container = tk.PanedWindow(
            self.root,
            orient=tk.HORIZONTAL,
            bg=self.colors['bg_dark'],
            sashwidth=3,
            sashrelief=tk.RAISED
        )
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Object Explorer
        self.create_object_explorer(main_container)
        
        # Right panel - Main workspace
        right_panel = tk.PanedWindow(
            main_container,
            orient=tk.VERTICAL,
            bg=self.colors['bg_dark'],
            sashwidth=3,
            sashrelief=tk.RAISED
        )
        main_container.add(right_panel, width=1200)
        
        # Top right - Query editor and navigation
        self.create_query_editor(right_panel)
        
        # Bottom right - Results and messages
        self.create_results_panel(right_panel)
    
    def create_object_explorer(self, parent):
        """Create object explorer panel (left side)"""
        explorer_frame = tk.Frame(parent, bg=self.colors['bg_medium'], width=300)
        
        # Title
        title_label = tk.Label(
            explorer_frame,
            text="📁 Object Explorer",
            font=("Segoe UI", 11, "bold"),
            bg=self.colors['bg_medium'],
            fg=self.colors['fg_bright'],
            anchor='w',
            padx=10,
            pady=8
        )
        title_label.pack(fill=tk.X)
        
        # Separator
        tk.Frame(explorer_frame, height=1, bg=self.colors['border']).pack(fill=tk.X)
        
        # Tree view
        tree_frame = tk.Frame(explorer_frame, bg=self.colors['bg_medium'])
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create treeview
        self.object_tree = ttk.Treeview(tree_frame, show='tree')
        self.object_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar
        tree_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.object_tree.yview)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.object_tree.configure(yscrollcommand=tree_scroll.set)
        
        # Populate tree
        self.populate_object_tree()
        
        # Database info panel
        info_frame = tk.LabelFrame(
            explorer_frame,
            text="Database Info",
            bg=self.colors['bg_light'],
            fg=self.colors['fg_normal'],
            font=("Segoe UI", 9)
        )
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.db_info_label = tk.Label(
            info_frame,
            text="Status: Ready\nRecords: 0\nIndexes: 2",
            bg=self.colors['bg_light'],
            fg=self.colors['fg_normal'],
            font=("Consolas", 9),
            justify=tk.LEFT,
            anchor='w',
            padx=10,
            pady=5
        )
        self.db_info_label.pack(fill=tk.X)
        
        parent.add(explorer_frame, width=300)
    
    def create_query_editor(self, parent):
        """Create query editor panel"""
        editor_container = tk.Frame(parent, bg=self.colors['bg_medium'])
        
        # Navigation tabs
        nav_frame = tk.Frame(editor_container, bg=self.colors['bg_medium'], height=40)
        nav_frame.pack(fill=tk.X)
        nav_frame.pack_propagate(False)
        
        # Tab buttons
        self.nav_buttons = {}
        tabs = [
            ("📝 SQL Query", "query"),
            ("📊 Data View", "data"),
            ("🌳 Index View", "index"),
            ("📖 SQL Guide", "guide")
        ]
        
        btn_frame = tk.Frame(nav_frame, bg=self.colors['bg_medium'])
        btn_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        for text, tab_id in tabs:
            btn = tk.Button(
                btn_frame,
                text=text,
                command=lambda t=tab_id: self.switch_tab(t),
                bg=self.colors['bg_light'],
                fg=self.colors['fg_normal'],
                activebackground=self.colors['accent'],
                activeforeground=self.colors['fg_bright'],
                relief=tk.FLAT,
                font=("Segoe UI", 9),
                padx=15,
                pady=5,
                cursor='hand2'
            )
            btn.pack(side=tk.LEFT, padx=2)
            self.nav_buttons[tab_id] = btn
        
        # Separator
        tk.Frame(editor_container, height=2, bg=self.colors['border']).pack(fill=tk.X)
        
        # Tab content container
        self.tab_container = tk.Frame(editor_container, bg=self.colors['bg_dark'])
        self.tab_container.pack(fill=tk.BOTH, expand=True)
        
        # Create all tabs
        self.create_query_tab()
        self.create_data_tab()
        self.create_index_tab()
        self.create_guide_tab()
        
        # Show query tab by default
        self.switch_tab('query')
        
        parent.add(editor_container, height=450)
    
    def create_query_tab(self):
        """Create SQL query editor tab"""
        self.query_frame = tk.Frame(self.tab_container, bg=self.colors['bg_dark'])
        
        # Toolbar
        toolbar = tk.Frame(self.query_frame, bg=self.colors['bg_medium'], height=35)
        toolbar.pack(fill=tk.X)
        toolbar.pack_propagate(False)
        
        tk.Button(
            toolbar,
            text="▶ Execute (F5)",
            command=self.execute_query,
            bg=self.colors['success'],
            fg=self.colors['bg_dark'],
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        tk.Button(
            toolbar,
            text="🗑 Clear",
            command=self.clear_query,
            bg=self.colors['bg_light'],
            fg=self.colors['fg_normal'],
            font=("Segoe UI", 9),
            relief=tk.FLAT,
            padx=10,
            pady=5,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=2, pady=5)
        
        tk.Button(
            toolbar,
            text="💾 Save Query",
            command=self.save_query,
            bg=self.colors['bg_light'],
            fg=self.colors['fg_normal'],
            font=("Segoe UI", 9),
            relief=tk.FLAT,
            padx=10,
            pady=5,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=2, pady=5)
        
        # Query editor
        editor_frame = tk.Frame(self.query_frame, bg=self.colors['bg_dark'])
        editor_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Line numbers (optional)
        line_num_frame = tk.Frame(editor_frame, bg=self.colors['bg_light'], width=40)
        line_num_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        self.line_numbers = tk.Text(
            line_num_frame,
            width=4,
            bg=self.colors['bg_light'],
            fg=self.colors['fg_normal'],
            font=("Consolas", 11),
            state=tk.DISABLED,
            relief=tk.FLAT
        )
        self.line_numbers.pack(fill=tk.Y)
        
        # SQL Text editor
        self.sql_editor = scrolledtext.ScrolledText(
            editor_frame,
            wrap=tk.WORD,
            bg=self.colors['bg_dark'],
            fg=self.colors['fg_bright'],
            insertbackground=self.colors['fg_bright'],
            font=("Consolas", 11),
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        self.sql_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Default query
        self.sql_editor.insert('1.0', "-- SQL Query Editor\n-- Press F5 or click Execute to run query\n\nSELECT * FROM students;\n")
        
        # Bind events
        self.sql_editor.bind('<KeyRelease>', self.update_line_numbers)
        self.update_line_numbers()
    
    def create_data_tab(self):
        """Create data view tab (Excel-like)"""
        self.data_frame = tk.Frame(self.tab_container, bg=self.colors['bg_dark'])
        
        # Toolbar
        toolbar = tk.Frame(self.data_frame, bg=self.colors['bg_medium'], height=35)
        toolbar.pack(fill=tk.X)
        toolbar.pack_propagate(False)
        
        tk.Button(
            toolbar,
            text="➕ Add Row",
            command=self.add_row_dialog,
            bg=self.colors['success'],
            fg=self.colors['bg_dark'],
            font=("Segoe UI", 9),
            relief=tk.FLAT,
            padx=10,
            pady=5,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        tk.Button(
            toolbar,
            text="🗑 Delete Row",
            command=self.delete_selected_row,
            bg=self.colors['error'],
            fg=self.colors['fg_bright'],
            font=("Segoe UI", 9),
            relief=tk.FLAT,
            padx=10,
            pady=5,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=2, pady=5)
        
        tk.Button(
            toolbar,
            text="🔄 Refresh",
            command=self.refresh_data_view,
            bg=self.colors['bg_light'],
            fg=self.colors['fg_normal'],
            font=("Segoe UI", 9),
            relief=tk.FLAT,
            padx=10,
            pady=5,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=2, pady=5)
        
        # Data grid
        grid_frame = tk.Frame(self.data_frame, bg=self.colors['bg_dark'])
        grid_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        columns = ("ma_sv", "ho_ten", "gioi_tinh", "ngay_sinh", "lop", "diem_tb")
        self.data_grid = ttk.Treeview(grid_frame, columns=columns, show='headings', height=15)
        
        # Column headers
        headers = ["Mã SV", "Họ và Tên", "Giới tính", "Ngày sinh", "Lớp", "Điểm TB"]
        widths = [100, 200, 80, 100, 100, 80]
        
        for col, header, width in zip(columns, headers, widths):
            self.data_grid.heading(col, text=header, command=lambda c=col: self.sort_data(c))
            self.data_grid.column(col, width=width, anchor='center')
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(grid_frame, orient=tk.VERTICAL, command=self.data_grid.yview)
        h_scroll = ttk.Scrollbar(grid_frame, orient=tk.HORIZONTAL, command=self.data_grid.xview)
        self.data_grid.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        self.data_grid.grid(row=0, column=0, sticky='nsew')
        v_scroll.grid(row=0, column=1, sticky='ns')
        h_scroll.grid(row=1, column=0, sticky='ew')
        
        grid_frame.grid_rowconfigure(0, weight=1)
        grid_frame.grid_columnconfigure(0, weight=1)
    
    def create_index_tab(self):
        """Create B-Tree index visualization tab"""
        self.index_frame = tk.Frame(self.tab_container, bg=self.colors['bg_dark'])
        
        # Index selector
        selector_frame = tk.Frame(self.index_frame, bg=self.colors['bg_medium'], height=40)
        selector_frame.pack(fill=tk.X)
        selector_frame.pack_propagate(False)
        
        tk.Label(
            selector_frame,
            text="Select Index:",
            bg=self.colors['bg_medium'],
            fg=self.colors['fg_normal'],
            font=("Segoe UI", 9)
        ).pack(side=tk.LEFT, padx=10, pady=10)
        
        self.index_selector = ttk.Combobox(
            selector_frame,
            values=["B-Tree: ma_sv", "B-Tree: ho_ten"],
            state='readonly',
            font=("Segoe UI", 9),
            width=20
        )
        self.index_selector.current(0)
        self.index_selector.pack(side=tk.LEFT, padx=5, pady=10)
        self.index_selector.bind('<<ComboboxSelected>>', lambda e: self.refresh_index_view())
        
        tk.Button(
            selector_frame,
            text="🔄 Refresh",
            command=self.refresh_index_view,
            bg=self.colors['bg_light'],
            fg=self.colors['fg_normal'],
            font=("Segoe UI", 9),
            relief=tk.FLAT,
            padx=10,
            pady=5,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Canvas for B-Tree visualization
        canvas_frame = tk.Frame(self.index_frame, bg=self.colors['bg_dark'])
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.index_canvas = tk.Canvas(
            canvas_frame,
            bg=self.colors['bg_dark'],
            highlightthickness=0
        )
        self.index_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Text representation
        text_frame = tk.LabelFrame(
            self.index_frame,
            text="Text Representation",
            bg=self.colors['bg_light'],
            fg=self.colors['fg_normal'],
            font=("Segoe UI", 9)
        )
        text_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.index_text = scrolledtext.ScrolledText(
            text_frame,
            height=8,
            bg=self.colors['bg_dark'],
            fg=self.colors['success'],
            font=("Consolas", 9),
            wrap=tk.WORD
        )
        self.index_text.pack(fill=tk.X, padx=5, pady=5)
    
    def create_guide_tab(self):
        """Create SQL command guide tab"""
        self.guide_frame = tk.Frame(self.tab_container, bg=self.colors['bg_dark'])
        
        guide_text = scrolledtext.ScrolledText(
            self.guide_frame,
            bg=self.colors['bg_dark'],
            fg=self.colors['fg_normal'],
            font=("Consolas", 10),
            wrap=tk.WORD,
            padx=20,
            pady=20
        )
        guide_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        guide_content = """
╔══════════════════════════════════════════════════════════════════════╗
║                    SQL COMMAND REFERENCE GUIDE                        ║
╚══════════════════════════════════════════════════════════════════════╝

📖 BASIC QUERIES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SELECT - Retrieve data from database
    Syntax: SELECT column1, column2, ... FROM table [WHERE condition]
    
    Examples:
    • SELECT * FROM students;
    • SELECT ma_sv, ho_ten FROM students;
    • SELECT * FROM students WHERE ma_sv = 'SV001';
    • SELECT * FROM students WHERE ho_ten LIKE '%Nguyen%';
    • SELECT * FROM students WHERE diem_tb > 8.0;

INSERT - Add new records
    Syntax: INSERT INTO table VALUES (value1, value2, ...)
    
    Examples:
    • INSERT INTO students VALUES ('SV001', 'Nguyen Van A', 'Nam', 
                                    '2003-05-15', 'CNTT01', 8.5);

UPDATE - Modify existing records
    Syntax: UPDATE table SET column = value WHERE condition
    
    Examples:
    • UPDATE students SET diem_tb = 9.0 WHERE ma_sv = 'SV001';
    • UPDATE students SET ho_ten = 'New Name', diem_tb = 9.5 
      WHERE ma_sv = 'SV001';

DELETE - Remove records
    Syntax: DELETE FROM table WHERE condition
    
    Examples:
    • DELETE FROM students WHERE ma_sv = 'SV001';

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 METADATA QUERIES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SHOW - Display database information
    • SHOW TABLES;            -- List all tables
    • SHOW INDEXES;           -- List all indexes
    • SHOW STATS;             -- Show database statistics

DESCRIBE - Show table structure
    • DESCRIBE students;
    • DESC students;

HELP - Display this help guide
    • HELP;

CLEAR - Clear all database records
    • CLEAR;

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 TIPS & BEST PRACTICES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Use single quotes for string values: 'SV001', 'Nguyen Van A'
2. Commands are case-insensitive: SELECT = select = SeLeCt
3. Always specify WHERE clause for UPDATE and DELETE to avoid accidents
4. Use LIKE with % wildcard for partial matching: LIKE '%Nguyen%'
5. Press F5 or click Execute button to run your query
6. Use -- for comments in your SQL code

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 SEARCH OPERATIONS WITH INDEXES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This database uses B-Tree indexes for fast searching:
• Index on 'ma_sv' (Primary key) - O(log n) search time
• Index on 'ho_ten' (Secondary key) - O(log n) search time

When you use WHERE ma_sv = 'XXX', the database automatically uses
the B-Tree index for efficient lookup instead of scanning all records.

View the Index tab to see B-Tree structure visualization!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        guide_text.insert('1.0', guide_content)
        guide_text.config(state=tk.DISABLED)
    
    def create_results_panel(self, parent):
        """Create results and messages panel (bottom)"""
        results_container = tk.Frame(parent, bg=self.colors['bg_medium'])
        
        # Results notebook
        notebook = ttk.Notebook(results_container)
        notebook.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Results tab
        results_frame = tk.Frame(notebook, bg=self.colors['bg_dark'])
        notebook.add(results_frame, text="📋 Results")
        
        # Results grid
        self.results_tree = ttk.Treeview(results_frame, show='headings', height=10)
        
        v_scroll = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        h_scroll = ttk.Scrollbar(results_frame, orient=tk.HORIZONTAL, command=self.results_tree.xview)
        self.results_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        self.results_tree.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        v_scroll.grid(row=0, column=1, sticky='ns')
        h_scroll.grid(row=1, column=0, sticky='ew')
        
        results_frame.grid_rowconfigure(0, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)
        
        # Messages tab
        messages_frame = tk.Frame(notebook, bg=self.colors['bg_dark'])
        notebook.add(messages_frame, text="💬 Messages")
        
        self.messages_text = scrolledtext.ScrolledText(
            messages_frame,
            bg=self.colors['bg_dark'],
            fg=self.colors['fg_normal'],
            font=("Consolas", 9),
            wrap=tk.WORD
        )
        self.messages_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Command history tab
        history_frame = tk.Frame(notebook, bg=self.colors['bg_dark'])
        notebook.add(history_frame, text="📜 History")
        
        self.history_text = scrolledtext.ScrolledText(
            history_frame,
            bg=self.colors['bg_dark'],
            fg=self.colors['warning'],
            font=("Consolas", 9),
            wrap=tk.WORD
        )
        self.history_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        parent.add(results_container, height=350)
    
    # ==== Navigation Functions ====
    
    def switch_tab(self, tab_id):
        """Switch between tabs"""
        # Hide all tabs
        for widget in self.tab_container.winfo_children():
            widget.pack_forget()
        
        # Reset button colors
        for btn in self.nav_buttons.values():
            btn.config(bg=self.colors['bg_light'], fg=self.colors['fg_normal'])
        
        # Show selected tab
        if tab_id == 'query':
            self.query_frame.pack(fill=tk.BOTH, expand=True)
        elif tab_id == 'data':
            self.data_frame.pack(fill=tk.BOTH, expand=True)
            self.refresh_data_view()
        elif tab_id == 'index':
            self.index_frame.pack(fill=tk.BOTH, expand=True)
            self.refresh_index_view()
        elif tab_id == 'guide':
            self.guide_frame.pack(fill=tk.BOTH, expand=True)
        
        # Highlight selected button
        self.nav_buttons[tab_id].config(bg=self.colors['accent'], fg=self.colors['fg_bright'])
    
    # ==== Query Functions ====
    
    def execute_query(self):
        """Execute SQL query"""
        query = self.sql_editor.get('1.0', tk.END).strip()
        
        if not query or query.startswith('--'):
            self.log_message("No query to execute", "warning")
            return
        
        # Split multiple queries by semicolon
        queries = [q.strip() for q in query.split(';') if q.strip() and not q.strip().startswith('--')]
        
        for sql in queries:
            success, message, result = self.sql_parser.parse_and_execute(sql)
            
            if success:
                self.log_message(f"✓ {message}", "success")
                
                if result:
                    self.display_results(result)
                else:
                    self.log_message("Query executed successfully (no results to display)", "info")
            else:
                self.log_message(f"✗ Error: {message}", "error")
        
        # Refresh all views
        self.refresh_all()
    
    def clear_query(self):
        """Clear query editor"""
        self.sql_editor.delete('1.0', tk.END)
    
    def save_query(self):
        """Save query to file"""
        query = self.sql_editor.get('1.0', tk.END)
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".sql",
            filetypes=[("SQL files", "*.sql"), ("All files", "*.*")]
        )
        
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(query)
            self.log_message(f"Query saved to {filename}", "success")
    
    def insert_template(self, template_type):
        """Insert SQL template"""
        templates = {
            "SELECT": "SELECT * FROM students WHERE ma_sv = 'SV001';",
            "INSERT": "INSERT INTO students VALUES ('SV999', 'Tên Sinh Viên', 'Nam', '2003-01-01', 'CNTT01', 8.0);",
            "UPDATE": "UPDATE students SET diem_tb = 9.0 WHERE ma_sv = 'SV001';",
            "DELETE": "DELETE FROM students WHERE ma_sv = 'SV001';"
        }
        
        template = templates.get(template_type, "")
        if template:
            self.sql_editor.insert(tk.INSERT, f"\n{template}\n")
    
    # ==== Display Functions ====
    
    def display_results(self, results):
        """Display query results in results tree"""
        # Clear previous results
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        if not results:
            return
        
        # Get columns
        columns = list(results[0].keys())
        
        # Configure columns
        self.results_tree['columns'] = columns
        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=120, anchor='center')
        
        # Insert data
        for row in results:
            values = [row.get(col, '') for col in columns]
            self.results_tree.insert('', tk.END, values=values)
        
        self.log_message(f"Displayed {len(results)} row(s)", "info")
    
    def log_message(self, message, msg_type="info"):
        """Log message to messages panel"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        color_map = {
            "success": self.colors['success'],
            "error": self.colors['error'],
            "warning": self.colors['warning'],
            "info": self.colors['fg_normal']
        }
        
        color = color_map.get(msg_type, self.colors['fg_normal'])
        
        self.messages_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.messages_text.see(tk.END)
        
        # Update history
        self.update_history()
    
    def update_history(self):
        """Update command history"""
        self.history_text.delete('1.0', tk.END)
        
        history = self.sql_parser.get_command_history()
        for cmd in history:
            self.history_text.insert(tk.END, f"[{cmd['timestamp']}] {cmd['command']}\n\n")
        
        self.history_text.see(tk.END)
    
    def update_line_numbers(self, event=None):
        """Update line numbers in query editor"""
        line_count = self.sql_editor.get('1.0', tk.END).count('\n')
        line_numbers = '\n'.join(str(i) for i in range(1, line_count + 1))
        
        self.line_numbers.config(state=tk.NORMAL)
        self.line_numbers.delete('1.0', tk.END)
        self.line_numbers.insert('1.0', line_numbers)
        self.line_numbers.config(state=tk.DISABLED)
    
    # ==== Data View Functions ====
    
    def refresh_data_view(self):
        """Refresh data grid"""
        # Clear grid
        for item in self.data_grid.get_children():
            self.data_grid.delete(item)
        
        # Add all students
        for student in self.db.get_all_students():
            self.data_grid.insert('', tk.END, values=(
                student.ma_sv,
                student.ho_ten,
                student.gioi_tinh,
                student.ngay_sinh,
                student.lop,
                student.diem_tb
            ))
    
    def add_row_dialog(self):
        """Show dialog to add new row"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Student")
        dialog.geometry("400x350")
        dialog.configure(bg=self.colors['bg_medium'])
        
        # Input fields
        fields = ["Mã SV:", "Họ và Tên:", "Giới tính:", "Ngày sinh:", "Lớp:", "Điểm TB:"]
        entries = {}
        
        for i, field in enumerate(fields):
            tk.Label(
                dialog,
                text=field,
                bg=self.colors['bg_medium'],
                fg=self.colors['fg_normal'],
                font=("Segoe UI", 10)
            ).grid(row=i, column=0, sticky='e', padx=10, pady=8)
            
            if field == "Giới tính:":
                entry = ttk.Combobox(dialog, values=['Nam', 'Nữ'], state='readonly', width=25)
                entry.current(0)
            else:
                entry = tk.Entry(dialog, width=28, font=("Segoe UI", 10))
            
            entry.grid(row=i, column=1, padx=10, pady=8)
            entries[field] = entry
        
        # Add button
        def add():
            try:
                ma_sv = entries["Mã SV:"].get()
                ho_ten = entries["Họ và Tên:"].get()
                gioi_tinh = entries["Giới tính:"].get()
                ngay_sinh = entries["Ngày sinh:"].get()
                lop = entries["Lớp:"].get()
                diem_tb = float(entries["Điểm TB:"].get())
                
                success, message = self.db.add_student(ma_sv, ho_ten, gioi_tinh, ngay_sinh, lop, diem_tb)
                
                if success:
                    messagebox.showinfo("Success", message)
                    dialog.destroy()
                    self.refresh_all()
                else:
                    messagebox.showerror("Error", message)
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        tk.Button(
            dialog,
            text="Add Student",
            command=add,
            bg=self.colors['success'],
            fg=self.colors['fg_bright'],
            font=("Segoe UI", 10, "bold"),
            padx=20,
            pady=8,
            cursor='hand2'
        ).grid(row=len(fields), column=0, columnspan=2, pady=15)
    
    def delete_selected_row(self):
        """Delete selected row from data grid"""
        selection = self.data_grid.selection()
        
        if not selection:
            messagebox.showwarning("Warning", "Please select a row to delete")
            return
        
        item = self.data_grid.item(selection[0])
        ma_sv = item['values'][0]
        
        confirm = messagebox.askyesno("Confirm", f"Delete student {ma_sv}?")
        
        if confirm:
            success, message = self.db.delete_student(ma_sv)
            if success:
                self.log_message(message, "success")
                self.refresh_all()
            else:
                messagebox.showerror("Error", message)
    
    def sort_data(self, col):
        """Sort data grid by column"""
        # Simple sort implementation
        items = [(self.data_grid.set(item, col), item) for item in self.data_grid.get_children('')]
        items.sort()
        
        for index, (val, item) in enumerate(items):
            self.data_grid.move(item, '', index)
    
    # ==== Index View Functions ====
    
    def refresh_index_view(self):
        """Refresh B-Tree index visualization"""
        selected = self.index_selector.get()
        
        if "ma_sv" in selected:
            structure = self.db.get_index_structure_ma_sv()
            self.draw_btree(self.index_canvas, structure)
            self.show_index_text(structure, "ma_sv")
        else:
            structure = self.db.get_index_structure_ho_ten()
            self.draw_btree(self.index_canvas, structure)
            self.show_index_text(structure, "ho_ten")
    
    def draw_btree(self, canvas, structure):
        """Draw B-Tree on canvas"""
        canvas.delete("all")
        
        if not structure:
            canvas.create_text(
                400, 200,
                text="Empty Tree",
                font=("Segoe UI", 14),
                fill=self.colors['fg_normal']
            )
            return
        
        # Group by level
        levels = {}
        for node in structure:
            level = node['level']
            if level not in levels:
                levels[level] = []
            levels[level].append(node)
        
        # Drawing parameters
        canvas_width = 800
        canvas_height = 400
        node_width = 120
        node_height = 40
        level_height = 100
        
        canvas.config(scrollregion=(0, 0, canvas_width, len(levels) * level_height))
        
        # Draw nodes
        for level, nodes in levels.items():
            y = 50 + level * level_height
            num_nodes = len(nodes)
            spacing = canvas_width / (num_nodes + 1)
            
            for i, node in enumerate(nodes):
                x = spacing * (i + 1)
                
                # Draw box
                color = self.colors['accent'] if node['leaf'] else self.colors['warning']
                
                canvas.create_rectangle(
                    x - node_width/2, y - node_height/2,
                    x + node_width/2, y + node_height/2,
                    fill=color,
                    outline=self.colors['fg_bright'],
                    width=2
                )
                
                # Draw keys
                keys_text = " | ".join(str(k)[:8] for k in node['keys'])
                canvas.create_text(
                    x, y,
                    text=keys_text,
                    font=("Consolas", 9, "bold"),
                    fill=self.colors['bg_dark']
                )
    
    def show_index_text(self, structure, index_name):
        """Show text representation of B-Tree"""
        self.index_text.delete('1.0', tk.END)
        
        if not structure:
            self.index_text.insert('1.0', "Empty tree\n")
            return
        
        self.index_text.insert('1.0', f"B-Tree Index on '{index_name}' (Order 3, t=2)\n")
        self.index_text.insert(tk.END, "="*60 + "\n\n")
        
        levels = {}
        for node in structure:
            level = node['level']
            if level not in levels:
                levels[level] = []
            levels[level].append(node)
        
        for level, nodes in sorted(levels.items()):
            self.index_text.insert(tk.END, f"Level {level}:\n")
            for node in nodes:
                node_type = "LEAF" if node['leaf'] else "INTERNAL"
                self.index_text.insert(tk.END, f"  [{node_type}] Keys: {node['keys']}\n")
            self.index_text.insert(tk.END, "\n")
    
    # ==== Object Explorer Functions ====
    
    def populate_object_tree(self):
        """Populate object explorer tree"""
        # Clear tree
        for item in self.object_tree.get_children():
            self.object_tree.delete(item)
        
        # Add database node
        db_node = self.object_tree.insert('', 'end', text='🗄 Student Database', open=True)
        
        # Add tables node
        tables_node = self.object_tree.insert(db_node, 'end', text='📋 Tables', open=True)
        students_table = self.object_tree.insert(tables_node, 'end', text='📊 students')
        
        # Add columns
        columns = ['ma_sv (PK)', 'ho_ten', 'gioi_tinh', 'ngay_sinh', 'lop', 'diem_tb']
        for col in columns:
            self.object_tree.insert(students_table, 'end', text=f'  ▫ {col}')
        
        # Add indexes node
        indexes_node = self.object_tree.insert(db_node, 'end', text='🔍 Indexes', open=True)
        self.object_tree.insert(indexes_node, 'end', text='🌳 idx_ma_sv (B-Tree)')
        self.object_tree.insert(indexes_node, 'end', text='🌳 idx_ho_ten (B-Tree)')
    
    def refresh_all(self):
        """Refresh all views"""
        self.refresh_data_view()
        self.refresh_index_view()
        self.populate_object_tree()
        self.update_db_info()
    
    def update_db_info(self):
        """Update database info panel"""
        stats = self.db.get_statistics()
        info_text = f"Status: Connected\nRecords: {stats['active_students']}\nIndexes: 2 (B-Tree)\nOperations: {stats['operations']}"
        self.db_info_label.config(text=info_text)
    
    # ==== File Operations ====
    
    def new_database(self):
        """Create new database"""
        confirm = messagebox.askyesno("Confirm", "Create new database? All current data will be lost.")
        if confirm:
            self.db.clear_database()
            self.current_file = None
            self.root.title("Student Database Management Studio - New Database")
            self.refresh_all()
            self.log_message("New database created", "success")
    
    def open_database(self):
        """Open database from file"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.db.clear_database()
                for student_data in data.get('students', []):
                    self.db.add_student(**student_data)
                
                self.current_file = filename
                self.root.title(f"Student Database Management Studio - {os.path.basename(filename)}")
                self.refresh_all()
                self.log_message(f"Database loaded from {filename}", "success")
            
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open database: {str(e)}")
    
    def save_database(self):
        """Save database to current file"""
        if self.current_file:
            self._save_to_file(self.current_file)
        else:
            self.save_database_as()
    
    def save_database_as(self):
        """Save database to new file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            self._save_to_file(filename)
            self.current_file = filename
            self.root.title(f"Student Database Management Studio - {os.path.basename(filename)}")
    
    def _save_to_file(self, filename):
        """Save database to file"""
        try:
            students_data = [s.to_dict() for s in self.db.get_all_students()]
            data = {
                'students': students_data,
                'metadata': {
                    'created': datetime.now().isoformat(),
                    'records': len(students_data)
                }
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.log_message(f"Database saved to {filename}", "success")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save database: {str(e)}")
    
    def export_to_json(self):
        """Export database to JSON"""
        self.save_database_as()
    
    def import_from_json(self):
        """Import database from JSON"""
        self.open_database()
    
    def clear_all_data(self):
        """Clear all database data"""
        confirm = messagebox.askyesno("Confirm", "Clear all data? This cannot be undone!")
        if confirm:
            self.db.clear_database()
            self.refresh_all()
            self.log_message("All data cleared", "warning")
    
    def load_sample_data(self):
        """Load sample data"""
        self.db.clear_database()
        self.db.load_sample_data()
        self.refresh_all()
        self.log_message("Sample data loaded", "success")
    
    # ==== Help Functions ====
    
    def show_btree_window(self):
        """Show B-Tree in separate window"""
        self.switch_tab('index')
    
    def show_statistics(self):
        """Show database statistics"""
        stats = self.db.get_statistics()
        
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Database Statistics")
        stats_window.geometry("400x300")
        stats_window.configure(bg=self.colors['bg_medium'])
        
        info_text = f"""
Database Statistics
{'='*40}

Active Students:     {stats['active_students']}
Total Records:       {stats['total_records']}
Deleted Records:     {stats['deleted_records']}
Total Operations:    {stats['operations']}

Indexes:             2 (B-Tree)
Index Type:          B-Tree Order 3 (t=2)
"""
        
        tk.Label(
            stats_window,
            text=info_text,
            font=("Consolas", 11),
            bg=self.colors['bg_medium'],
            fg=self.colors['fg_normal'],
            justify=tk.LEFT
        ).pack(padx=20, pady=20)
    
    def show_sql_help(self):
        """Show SQL help"""
        self.switch_tab('guide')
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
Student Database Management Studio
Version 2.0

A professional database management system
with B-Tree indexing and SQL support.

Features:
• SQL Query Editor
• B-Tree Index Visualization
• Excel-like Data Grid
• Command History
• Import/Export

© 2024 - Educational Project
"""
        messagebox.showinfo("About", about_text)


def main():
    root = tk.Tk()
    app = DBManagementStudio(root)
    root.mainloop()


if __name__ == "__main__":
    main()
