#!/usr/bin/env python3
"""
Modern Modular English Dictionary
MVC Architecture with Dark/Light Theme Support
"""

import json
import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from difflib import get_close_matches
from typing import Dict, List, Set, Optional, Callable


# ==================== CONFIGURATION ====================

class Config:
    """Application configuration constants"""
    APP_NAME = "OP English Dictionary"
    VERSION = "2.0"
    GEOMETRY = "1000x750"
    
    # File paths
    DICT_FILE = 'dictionary_compact.json'
    SAVED_WORDS_FILE = 'saved_words.json'
    SETTINGS_FILE = 'dictionary_settings.json'
    
    # Colors - Light Theme
    LIGHT_BG = "#f5f5f5"
    LIGHT_CARD = "#ffffff"
    LIGHT_TEXT = "#2c3e50"
    LIGHT_ACCENT = "#3498db"
    LIGHT_SECONDARY = "#7f8c8d"
    LIGHT_BORDER = "#e0e0e0"
    LIGHT_SUCCESS = "#27ae60"
    LIGHT_WARNING = "#f39c12"
    LIGHT_ERROR = "#e74c3c"
    
    # Colors - Dark Theme
    DARK_BG = "#1a1a2e"
    DARK_CARD = "#16213e"
    DARK_TEXT = "#eaeaea"
    DARK_ACCENT = "#00d9ff"
    DARK_SECONDARY = "#a0a0a0"
    DARK_BORDER = "#0f3460"
    DARK_SUCCESS = "#00ff88"
    DARK_WARNING = "#ffd700"
    DARK_ERROR = "#ff4757"
    
    # Fonts
    FONT_FAMILY = "Segoe UI"
    FONT_SIZE_SMALL = 9
    FONT_SIZE_NORMAL = 11
    FONT_SIZE_LARGE = 14
    FONT_SIZE_HEADER = 24


# ==================== THEME MANAGER ====================

class ThemeManager:
    """Manages application themes and styling"""
    
    def __init__(self):
        self.is_dark = False
        self.style = ttk.Style()
        self.callbacks: List[Callable] = []
        
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        self.is_dark = not self.is_dark
        self.apply_theme()
        # Notify all registered components
        for callback in self.callbacks:
            callback()
        return self.is_dark
    
    def register(self, callback: Callable):
        """Register a callback for theme changes"""
        self.callbacks.append(callback)
        
    def get_colors(self):
        """Get current theme colors"""
        if self.is_dark:
            return {
                'bg': Config.DARK_BG,
                'card': Config.DARK_CARD,
                'text': Config.DARK_TEXT,
                'accent': Config.DARK_ACCENT,
                'secondary': Config.DARK_SECONDARY,
                'border': Config.DARK_BORDER,
                'success': Config.DARK_SUCCESS,
                'warning': Config.DARK_WARNING,
                'error': Config.DARK_ERROR,
                'select_bg': Config.DARK_ACCENT,
                'select_fg': Config.DARK_BG
            }
        else:
            return {
                'bg': Config.LIGHT_BG,
                'card': Config.LIGHT_CARD,
                'text': Config.LIGHT_TEXT,
                'accent': Config.LIGHT_ACCENT,
                'secondary': Config.LIGHT_SECONDARY,
                'border': Config.LIGHT_BORDER,
                'success': Config.LIGHT_SUCCESS,
                'warning': Config.LIGHT_WARNING,
                'error': Config.LIGHT_ERROR,
                'select_bg': Config.LIGHT_ACCENT,
                'select_fg': 'white'
            }
    
    def apply_theme(self):
        """Apply theme to ttk styles"""
        c = self.get_colors()
        
        # Configure base styles
        self.style.configure('.',
            background=c['bg'],
            foreground=c['text'],
            fieldbackground=c['card'],
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL)
        )
        
        self.style.configure('TFrame', background=c['bg'])
        self.style.configure('TLabel', background=c['bg'], foreground=c['text'])
        self.style.configure('TButton', 
            background=c['accent'],
            foreground=c['text'],
            padding=8,
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL)
        )
        
        # Card frame style
        self.style.configure('Card.TFrame', background=c['card'])
        self.style.configure('Card.TLabel', background=c['card'], foreground=c['text'])
        
        # Accent button
        self.style.configure('Accent.TButton',
            background=c['accent'],
            foreground='white' if not self.is_dark else c['bg'],
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL, 'bold')
        )
        
        # Notebook
        self.style.configure('TNotebook', background=c['bg'], tabmargins=[2, 5, 2, 0])
        self.style.configure('TNotebook.Tab', 
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL),
            padding=[15, 5],
            background=c['bg'],
            foreground=c['secondary']
        )
        self.style.map('TNotebook.Tab',
            background=[('selected', c['card'])],
            foreground=[('selected', c['accent'])],
            expand=[('selected', [1, 1, 1, 0])]
        )
        
        # Entry
        self.style.configure('TEntry',
            fieldbackground=c['card'],
            foreground=c['text'],
            insertcolor=c['text'],
            padding=8
        )
        
        # Scrollbar
        self.style.configure('TScrollbar',
            background=c['border'],
            troughcolor=c['bg'],
            borderwidth=0
        )


# ==================== DATA MANAGER ====================

class DataManager:
    """Handles all data operations"""
    
    def __init__(self):
        self.dictionary: Dict[str, any] = {}
        self.saved_words: Set[str] = set()
        self.history: List[str] = []
        self.settings: Dict = {}
        
    def load_dictionary(self, filepath: str) -> bool:
        """Load dictionary from JSON file"""
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    self.dictionary = json.load(f)
                return True
            return False
        except Exception as e:
            print(f"Error loading dictionary: {e}")
            return False
    
    def load_saved_words(self):
        """Load saved words from file"""
        try:
            if os.path.exists(Config.SAVED_WORDS_FILE):
                with open(Config.SAVED_WORDS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.saved_words = set(data.get('words', []))
        except Exception as e:
            print(f"Error loading saved words: {e}")
            self.saved_words = set()
    
    def save_saved_words(self):
        """Save saved words to file"""
        try:
            with open(Config.SAVED_WORDS_FILE, 'w', encoding='utf-8') as f:
                json.dump({'words': list(self.saved_words)}, f)
        except Exception as e:
            print(f"Error saving words: {e}")
    
    def load_settings(self):
        """Load app settings"""
        try:
            if os.path.exists(Config.SETTINGS_FILE):
                with open(Config.SETTINGS_FILE, 'r') as f:
                    self.settings = json.load(f)
        except:
            self.settings = {}
    
    def save_settings(self):
        """Save app settings"""
        try:
            with open(Config.SETTINGS_FILE, 'w') as f:
                json.dump(self.settings, f)
        except:
            pass
    
    def lookup(self, word: str) -> Optional[any]:
        """Look up a word in the dictionary"""
        return self.dictionary.get(word.lower())
    
    def get_suggestions(self, word: str, n: int = 5) -> List[str]:
        """Get spelling suggestions"""
        return get_close_matches(word.lower(), self.dictionary.keys(), n=n, cutoff=0.6)
    
    def toggle_saved(self, word: str) -> bool:
        """Toggle save status of a word. Returns True if now saved."""
        word = word.lower()
        if word in self.saved_words:
            self.saved_words.remove(word)
            return False
        else:
            self.saved_words.add(word)
            return True
    
    def is_saved(self, word: str) -> bool:
        """Check if word is saved"""
        return word.lower() in self.saved_words
    
    def add_to_history(self, word: str):
        """Add word to search history"""
        word = word.lower()
        if word in self.history:
            self.history.remove(word)
        self.history.insert(0, word)
        if len(self.history) > 50:
            self.history.pop()
    
    def get_stats(self) -> Dict[str, int]:
        """Get dictionary statistics"""
        return {
            'total_words': len(self.dictionary),
            'saved_count': len(self.saved_words),
            'history_count': len(self.history)
        }


# ==================== CLIPBOARD MONITOR ====================

class ClipboardMonitor:
    """Monitors system clipboard for auto-search"""
    
    def __init__(self, callback: Callable[[str], None]):
        self.callback = callback
        self.active = False
        self.last_text = ""
        self.check_interval = 1000  # ms
        
    def start(self):
        """Start monitoring"""
        self.active = True
        self._check()
        
    def stop(self):
        """Stop monitoring"""
        self.active = False
        
    def _check(self):
        """Check clipboard content"""
        if not self.active:
            return
            
        try:
            # Use xclip to get primary selection
            result = subprocess.run(
                ['xclip', '-o', '-selection', 'primary'],
                capture_output=True,
                text=True,
                timeout=0.5
            )
            
            if result.returncode == 0:
                text = result.stdout.strip().lower()
                # Validate: single word, changed, in dictionary
                if (text and 
                    len(text.split()) == 1 and 
                    text != self.last_text and
                    len(text) < 50):
                    
                    self.last_text = text
                    self.callback(text)
                    
        except:
            pass
            
        # Schedule next check
        if self.active:
            # Use tkinter's after method via a timer reference
            pass  # Will be handled by caller
    
    def get_clipboard_text(self) -> str:
        """Get current clipboard text safely"""
        try:
            result = subprocess.run(
                ['xclip', '-o', '-selection', 'primary'],
                capture_output=True,
                text=True,
                timeout=0.5
            )
            return result.stdout.strip() if result.returncode == 0 else ""
        except:
            return ""


# ==================== UI COMPONENTS ====================

class SearchBar(ttk.Frame):
    """Modern search bar component"""
    
    def __init__(self, parent, on_search: Callable, on_save: Callable, theme: ThemeManager, **kwargs):
        super().__init__(parent, **kwargs)
        self.on_search = on_search
        self.on_save = on_save
        self.theme = theme
        
        self.columnconfigure(0, weight=1)
        
        # Search entry with placeholder
        self.search_var = tk.StringVar()
        self.entry = tk.Entry(
            self,
            textvariable=self.search_var,
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_LARGE),
            relief='flat',
            highlightthickness=2,
            bd=0
        )
        self.entry.grid(row=0, column=0, sticky='ew', padx=(0, 10), ipady=8)
        self.entry.bind('<Return>', lambda e: self._do_search())
        self.entry.bind('<FocusIn>', self._on_focus_in)
        self.entry.bind('<FocusOut>', self._on_focus_out)
        
        # Buttons frame
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=0, column=1)
        
        self.search_btn = tk.Button(
            btn_frame,
            text="🔍",
            command=self._do_search,
            relief='flat',
            cursor='hand2',
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_LARGE)
        )
        self.search_btn.pack(side='left', padx=2)
        
        self.save_btn = tk.Button(
            btn_frame,
            text="⭐",
            command=self._do_save,
            relief='flat',
            cursor='hand2',
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_LARGE)
        )
        self.save_btn.pack(side='left', padx=2)
        
        # Update styling
        self._update_style()
        theme.register(self._update_style)
        
    def _update_style(self):
        """Update component styling based on theme"""
        c = self.theme.get_colors()
        
        self.entry.config(
            bg=c['card'],
            fg=c['text'],
            insertbackground=c['text'],
            highlightcolor=c['accent'],
            highlightbackground=c['border']
        )
        
        self.search_btn.config(
            bg=c['accent'],
            fg='white' if not self.theme.is_dark else c['bg'],
            activebackground=c['accent']
        )
        
        self.save_btn.config(
            bg=c['warning'] if self.theme.is_dark else '#f1c40f',
            fg=c['bg'] if self.theme.is_dark else c['text'],
            activebackground=c['warning']
        )
        
    def _do_search(self):
        word = self.search_var.get().strip()
        if word:
            self.on_search(word)
            
    def _do_save(self):
        word = self.search_var.get().strip()
        if word:
            is_saved = self.on_save(word)
            self.update_save_icon(is_saved)
            
    def update_save_icon(self, is_saved: bool):
        """Update save button appearance"""
        self.save_btn.config(text="❌" if is_saved else "⭐")
        
    def set_text(self, text: str):
        """Set search text"""
        self.search_var.set(text)
        
    def get_text(self) -> str:
        """Get search text"""
        return self.search_var.get().strip()
        
    def _on_focus_in(self, event):
        self.entry.select_range(0, 'end')
        
    def _on_focus_out(self, event):
        pass


class DefinitionView(tk.Frame):
    """Component for displaying word definitions"""
    
    def __init__(self, parent, on_word_click: Callable, theme: ThemeManager, **kwargs):
        super().__init__(parent, **kwargs)
        self.on_word_click = on_word_click
        self.theme = theme
        
        self.text = scrolledtext.ScrolledText(
            self,
            wrap=tk.WORD,
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL),
            padx=20,
            pady=20,
            relief='flat',
            state=tk.DISABLED,
            cursor='arrow'
        )
        self.text.pack(fill='both', expand=True)
        
        # Configure tags
        self._setup_tags()
        theme.register(self._update_style)
        
    def _setup_tags(self):
        """Configure text tags"""
        self.text.tag_config("header", font=(Config.FONT_FAMILY, Config.FONT_SIZE_HEADER, 'bold'))
        self.text.tag_config("phonetic", font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL, 'italic'))
        self.text.tag_config("pos", font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL, 'bold'))
        self.text.tag_config("number", font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL, 'bold'))
        self.text.tag_config("definition", font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL))
        self.text.tag_config("example", font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL, 'italic'))
        self.text.tag_config("saved", font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL))
        self.text.tag_config("error", font=(Config.FONT_FAMILY, Config.FONT_SIZE_LARGE))
        self.text.tag_config("suggestion", font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL))
        
        # Clickable tags
        self.text.tag_config("link", underline=True)
        self.text.tag_bind("link", "<Button-1>", self._on_link_click)
        self.text.tag_bind("link", "<Enter>", lambda e: self.text.config(cursor="hand2"))
        self.text.tag_bind("link", "<Leave>", lambda e: self.text.config(cursor="arrow"))
        
    def _update_style(self):
        """Update colors based on theme"""
        c = self.theme.get_colors()
        
        self.config(bg=c['bg'])
        self.text.config(
            bg=c['card'],
            fg=c['text'],
            insertbackground=c['text']
        )
        
        # Update tag colors
        self.text.tag_config("header", foreground=c['accent'])
        self.text.tag_config("phonetic", foreground=c['secondary'])
        self.text.tag_config("pos", foreground=c['warning'])
        self.text.tag_config("number", foreground=c['accent'])
        self.text.tag_config("definition", foreground=c['text'])
        self.text.tag_config("example", foreground=c['secondary'])
        self.text.tag_config("saved", foreground=c['success'])
        self.text.tag_config("error", foreground=c['error'])
        self.text.tag_config("suggestion", foreground=c['secondary'])
        self.text.tag_config("link", foreground=c['accent'])
        
    def display_word(self, word: str, definition: any, is_saved: bool):
        """Display a word definition"""
        self.text.config(state=tk.NORMAL)
        self.text.delete(1.0, tk.END)
        
        # Header
        self.text.insert(tk.END, f"{word.upper()}\n", "header")
        
        # Saved indicator
        if is_saved:
            self.text.insert(tk.END, "⭐ Saved to your collection\n", "saved")
            
        self.text.insert(tk.END, "\n")
        
        # Definition content
        if isinstance(definition, list):
            for i, defn in enumerate(definition[:5], 1):
                self.text.insert(tk.END, f"{i}. ", "number")
                self.text.insert(tk.END, f"{defn}\n\n", "definition")
        else:
            self.text.insert(tk.END, f"{definition}\n", "definition")
            
        self.text.config(state=tk.DISABLED)
        
    def display_not_found(self, word: str, suggestions: List[str]):
        """Display not found message with suggestions"""
        self.text.config(state=tk.NORMAL)
        self.text.delete(1.0, tk.END)
        
        self.text.insert(tk.END, f"'{word}' not found\n\n", "error")
        
        if suggestions:
            self.text.insert(tk.END, "Did you mean:\n\n", "suggestion")
            for suggestion in suggestions:
                self.text.insert(tk.END, f"  • {suggestion}\n", "link")
                # Add tag for this specific line
                start = self.text.index("end-2l linestart+4c")
                end = self.text.index("end-2l lineend")
                self.text.tag_add(f"word_{suggestion}", start, end)
                self.text.tag_bind(f"word_{suggestion}", "<Button-1>", 
                    lambda e, w=suggestion: self.on_word_click(w))
                    
        self.text.config(state=tk.DISABLED)
        
    def clear(self):
        """Clear display"""
        self.text.config(state=tk.NORMAL)
        self.text.delete(1.0, tk.END)
        self.text.config(state=tk.DISABLED)
        
    def _on_link_click(self, event):
        """Handle link click"""
        index = self.text.index(f"@{event.x},{event.y}")
        line = self.text.get(f"{index} linestart", f"{index} lineend")
        word = line.replace("•", "").strip()
        if word:
            self.on_word_click(word)


class WordList(tk.Frame):
    """Reusable word list component with search"""
    
    def __init__(self, parent, title: str, on_select: Callable, theme: ThemeManager, **kwargs):
        super().__init__(parent, **kwargs)
        self.title = title
        self.on_select = on_select
        self.theme = theme
        self.words: List[str] = []
        
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        # Search filter
        self.filter_var = tk.StringVar()
        self.filter_var.trace('w', self._on_filter_change)
        
        self.filter_entry = tk.Entry(
            self,
            textvariable=self.filter_var,
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL),
            relief='flat'
        )
        self.filter_entry.grid(row=0, column=0, sticky='ew', pady=(0, 10), ipady=5)
        
        # Listbox
        list_frame = tk.Frame(self)
        list_frame.grid(row=1, column=0, sticky='nsew')
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.grid(row=0, column=1, sticky='ns')
        
        self.listbox = tk.Listbox(
            list_frame,
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL),
            yscrollcommand=scrollbar.set,
            selectmode=tk.SINGLE,
            activestyle='none',
            relief='flat',
            exportselection=False
        )
        self.listbox.grid(row=0, column=0, sticky='nsew')
        scrollbar.config(command=self.listbox.yview)
        
        # Bindings
        self.listbox.bind('<Double-Button-1>', lambda e: self._on_double_click())
        self.listbox.bind('<Return>', lambda e: self._on_double_click())
        
        # Update style
        self._update_style()
        theme.register(self._update_style)
        
    def _update_style(self):
        c = self.theme.get_colors()
        
        self.config(bg=c['bg'])
        self.filter_entry.config(
            bg=c['card'],
            fg=c['text'],
            insertbackground=c['text'],
            highlightcolor=c['accent'],
            highlightthickness=1
        )
        self.listbox.config(
            bg=c['card'],
            fg=c['text'],
            selectbackground=c['select_bg'],
            selectforeground=c['select_fg']
        )
        
    def set_words(self, words: List[str]):
        """Set the word list"""
        self.words = sorted(words)
        self._refresh_list()
        
    def _on_filter_change(self, *args):
        """Filter list based on search"""
        self._refresh_list()
        
    def _refresh_list(self):
        """Refresh listbox with filtered words"""
        filter_text = self.filter_var.get().lower()
        self.listbox.delete(0, tk.END)
        
        for word in self.words:
            if filter_text in word.lower():
                self.listbox.insert(tk.END, word)
                
    def _on_double_click(self):
        """Handle double click"""
        selection = self.listbox.curselection()
        if selection:
            word = self.listbox.get(selection[0])
            self.on_select(word)
            
    def get_selected(self) -> Optional[str]:
        """Get selected word"""
        selection = self.listbox.curselection()
        return self.listbox.get(selection[0]) if selection else None
        
    def remove_selected(self):
        """Remove selected item from list"""
        selection = self.listbox.curselection()
        if selection:
            word = self.listbox.get(selection[0])
            self.listbox.delete(selection[0])
            if word in self.words:
                self.words.remove(word)
            return word
        return None


class ToggleSwitch(tk.Canvas):
    """Modern toggle switch widget"""
    
    def __init__(self, parent, command: Callable, initial=False, **kwargs):
        self.width = 50
        self.height = 26
        super().__init__(parent, width=self.width, height=self.height, 
                        highlightthickness=0, **kwargs)
        
        self.command = command
        self.active = initial
        self.theme = None
        
        self.bind('<Button-1>', self.toggle)
        
    def set_theme(self, theme: ThemeManager):
        self.theme = theme
        self.draw()
        theme.register(self.draw)
        
    def draw(self):
        self.delete('all')
        if not self.theme:
            return
            
        c = self.theme.get_colors()
        
        # Background
        bg_color = c['accent'] if self.active else c['border']
        self.create_oval(2, 2, self.height-2, self.height-2, fill=bg_color, outline='')
        self.create_oval(self.width-self.height+2, 2, self.width-2, self.height-2, fill=bg_color, outline='')
        self.create_rectangle(self.height//2, 2, self.width-self.height//2, self.height-2, fill=bg_color, outline='')
        
        # Circle
        circle_x = self.width - self.height//2 - 2 if self.active else self.height//2 + 2
        self.create_oval(circle_x-10, 3, circle_x+10, self.height-3, fill=c['card'], outline='')
        
    def toggle(self, event=None):
        self.active = not self.active
        self.draw()
        if self.command:
            self.command(self.active)
        return self.active


# ==================== MAIN APPLICATION ====================

class DictionaryApp:
    """Main application controller"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(Config.APP_NAME)
        self.root.geometry(Config.GEOMETRY)
        self.root.minsize(800, 600)
        
        # Initialize MVC components
        self.theme = ThemeManager()
        self.data = DataManager()
        self.monitor = ClipboardMonitor(self._on_clipboard_word)
        
        # Load data
        self._load_data()
        
        # Build UI
        self._build_ui()
        
        # Apply initial theme
        self.theme.apply_theme()
        if self.data.settings.get('dark_mode', False):
            self.theme.toggle_theme()
            
        # Protocols
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Start clipboard check loop
        self._schedule_clipboard_check()
        
    def _load_data(self):
        """Load all data"""
        if not self.data.load_dictionary(Config.DICT_FILE):
            messagebox.showerror(
                "Dictionary Not Found",
                f"Could not find {Config.DICT_FILE}\n\n"
                "Download from:\n"
                "https://github.com/matthewreagan/WebstersEnglishDictionary"
            )
        self.data.load_saved_words()
        self.data.load_settings()
        
    def _build_ui(self):
        """Build the user interface"""
        c = self.theme.get_colors()
        
        # Main container with padding
        self.main_frame = tk.Frame(self.root, bg=c['bg'])
        self.main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(2, weight=1)
        
        # Header with theme toggle
        header_frame = tk.Frame(self.main_frame, bg=c['bg'])
        header_frame.grid(row=0, column=0, sticky='ew', pady=(0, 20))
        header_frame.columnconfigure(0, weight=1)
        
        title = tk.Label(
            header_frame,
            text=Config.APP_NAME,
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_HEADER, 'bold'),
            bg=c['bg'],
            fg=c['accent']
        )
        title.grid(row=0, column=0, sticky='w')
        
        # Theme toggle
        toggle_frame = tk.Frame(header_frame, bg=c['bg'])
        toggle_frame.grid(row=0, column=1, sticky='e')
        
        self.theme_label = tk.Label(
            toggle_frame,
            text="🌙" if self.theme.is_dark else "☀️",
            font=(Config.FONT_FAMILY, 16),
            bg=c['bg'],
            fg=c['text']
        )
        self.theme_label.pack(side='left', padx=5)
        
        self.theme_switch = ToggleSwitch(toggle_frame, self._on_theme_toggle, self.theme.is_dark)
        self.theme_switch.pack(side='left')
        self.theme_switch.set_theme(self.theme)
        
        # Search bar
        self.search_bar = SearchBar(
            self.main_frame,
            on_search=self._do_search,
            on_save=self._do_save,
            theme=self.theme
        )
        self.search_bar.grid(row=1, column=0, sticky='ew', pady=(0, 20))
        
        # Content notebook
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.grid(row=2, column=0, sticky='nsew')
        
        # Tab 1: Definition
        self.def_view = DefinitionView(
            self.notebook,
            on_word_click=self._do_search,
            theme=self.theme
        )
        self.notebook.add(self.def_view, text="  📖 Definition  ")
        
        # Tab 2: Saved Words
        self.saved_frame = tk.Frame(self.notebook, bg=c['bg'])
        self.saved_frame.columnconfigure(0, weight=1)
        self.saved_frame.rowconfigure(0, weight=1)
        
        self.saved_list = WordList(
            self.saved_frame,
            title="Saved Words",
            on_select=self._do_search,
            theme=self.theme
        )
        self.saved_list.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        self.saved_list.set_words(list(self.data.saved_words))
        
        # Saved words buttons
        saved_btn_frame = tk.Frame(self.saved_frame, bg=c['bg'])
        saved_btn_frame.grid(row=1, column=0, sticky='ew', padx=10, pady=(0, 10))
        
        self._create_button(saved_btn_frame, "🔍 Look Up", self._lookup_saved).pack(side='left', padx=2)
        self._create_button(saved_btn_frame, "🗑️ Remove", self._remove_saved).pack(side='left', padx=2)
        self._create_button(saved_btn_frame, "📤 Export", self._export_saved).pack(side='left', padx=2)
        
        self.notebook.add(self.saved_frame, text=f"  ⭐ Saved ({len(self.data.saved_words)})  ")
        
        # Tab 3: History
        self.history_frame = tk.Frame(self.notebook, bg=c['bg'])
        self.history_frame.columnconfigure(0, weight=1)
        self.history_frame.rowconfigure(0, weight=1)
        
        self.history_list = WordList(
            self.history_frame,
            title="Search History",
            on_select=self._do_search,
            theme=self.theme
        )
        self.history_list.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        
        self.notebook.add(self.history_frame, text="  🕐 History  ")
        
        # Status bar
        self.status_frame = tk.Frame(self.main_frame, bg=c['bg'])
        self.status_frame.grid(row=3, column=0, sticky='ew', pady=(10, 0))
        
        self.status_label = tk.Label(
            self.status_frame,
            text=self._get_status_text(),
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
            bg=c['bg'],
            fg=c['secondary']
        )
        self.status_label.pack(side='left')
        
        # Auto-search toggle
        self.auto_var = tk.BooleanVar(value=self.data.settings.get('auto_search', False))
        auto_check = tk.Checkbutton(
            self.status_frame,
            text="⚡ Auto-search",
            variable=self.auto_var,
            command=self._toggle_auto_search,
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
            bg=c['bg'],
            fg=c['text'],
            selectcolor=c['card'],
            activebackground=c['bg'],
            activeforeground=c['text']
        )
        auto_check.pack(side='right')
        
        # Theme change callback
        self.theme.register(self._on_theme_change)
        
    def _create_button(self, parent, text, command):
        """Create a styled button"""
        c = self.theme.get_colors()
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL),
            bg=c['accent'],
            fg='white' if not self.theme.is_dark else c['bg'],
            activebackground=c['accent'],
            activeforeground='white' if not self.theme.is_dark else c['bg'],
            relief='flat',
            cursor='hand2',
            padx=15,
            pady=5
        )
        return btn
        
    def _on_theme_change(self):
        """Handle theme change"""
        c = self.theme.get_colors()
        
        # Update main containers
        self.root.config(bg=c['bg'])
        self.main_frame.config(bg=c['bg'])
        
        # Update status bar
        self.status_frame.config(bg=c['bg'])
        self.status_label.config(bg=c['bg'], fg=c['secondary'])
        
        # Update theme icon
        self.theme_label.config(text="🌙" if self.theme.is_dark else "☀️", bg=c['bg'], fg=c['text'])
        
        # Update notebook tabs
        self.notebook.tab(0, text="  📖 Definition  ")
        self.notebook.tab(1, text=f"  ⭐ Saved ({len(self.data.saved_words)})  ")
        self.notebook.tab(2, text="  🕐 History  ")
        
        # Refresh lists
        self.saved_list._update_style()
        self.history_list._update_style()
        
    def _on_theme_toggle(self, active):
        """Handle theme toggle switch"""
        if active != self.theme.is_dark:
            self.theme.toggle_theme()
            
    def _do_search(self, word: str):
        """Perform word search"""
        word = word.strip().lower()
        if not word:
            return
            
        self.search_bar.set_text(word)
        self.data.add_to_history(word)
        
        definition = self.data.lookup(word)
        
        if definition:
            self.def_view.display_word(word, definition, self.data.is_saved(word))
            self.search_bar.update_save_icon(self.data.is_saved(word))
        else:
            suggestions = self.data.get_suggestions(word)
            self.def_view.display_not_found(word, suggestions)
            
        # Update history list
        self.history_list.set_words(self.data.history)
        
        # Switch to definition tab
        self.notebook.select(0)
        
    def _do_save(self, word: str) -> bool:
        """Toggle save word"""
        is_saved = self.data.toggle_saved(word.lower())
        self.data.save_saved_words()
        self.saved_list.set_words(list(self.data.saved_words))
        self.notebook.tab(1, text=f"  ⭐ Saved ({len(self.data.saved_words)})  ")
        self._update_status()
        return is_saved
        
    def _lookup_saved(self):
        """Look up selected saved word"""
        word = self.saved_list.get_selected()
        if word:
            self._do_search(word)
            
    def _remove_saved(self):
        """Remove selected saved word"""
        word = self.saved_list.remove_selected()
        if word:
            self.data.saved_words.discard(word)
            self.data.save_saved_words()
            self.notebook.tab(1, text=f"  ⭐ Saved ({len(self.data.saved_words)})  ")
            self._update_status()
            
    def _export_saved(self):
        """Export saved words to file"""
        if not self.data.saved_words:
            messagebox.showinfo("Export", "No saved words to export!")
            return
            
        filename = "my_dictionary.txt"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"My Saved Dictionary Words\n")
                f.write("=" * 50 + "\n\n")
                for word in sorted(self.data.saved_words):
                    f.write(f"{word.upper()}\n")
                    definition = self.data.lookup(word)
                    if isinstance(definition, list):
                        for i, d in enumerate(definition, 1):
                            f.write(f"  {i}. {d}\n")
                    else:
                        f.write(f"  {definition}\n")
                    f.write("\n")
                    
            messagebox.showinfo("Export Successful", 
                f"Saved {len(self.data.saved_words)} words to {filename}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))
            
    def _toggle_auto_search(self):
        """Toggle clipboard monitoring"""
        if self.auto_var.get():
            self.monitor.start()
            self._show_status("Auto-search enabled - Select text to search")
        else:
            self.monitor.stop()
            self._show_status("Auto-search disabled")
            
    def _on_clipboard_word(self, word: str):
        """Handle word from clipboard"""
        if word in self.data.dictionary:
            self.root.after(0, lambda: self._do_search(word))
            self.root.lift()
            self._show_status(f"Auto-searched: '{word}'")
            
    def _schedule_clipboard_check(self):
        """Schedule periodic clipboard checks"""
        if self.monitor.active:
            self.monitor._check()
        self.root.after(1000, self._schedule_clipboard_check)
        
    def _show_status(self, message: str):
        """Show temporary status message"""
        self.status_label.config(text=message)
        self.root.after(3000, self._update_status)
        
    def _update_status(self):
        """Update status bar"""
        self.status_label.config(text=self._get_status_text())
        
    def _get_status_text(self) -> str:
        """Get status bar text"""
        stats = self.data.get_stats()
        return f"📚 {stats['total_words']:,} words | ⭐ {stats['saved_count']} saved"
        
    def _on_close(self):
        """Handle window close"""
        self.monitor.stop()
        self.data.settings['dark_mode'] = self.theme.is_dark
        self.data.settings['auto_search'] = self.auto_var.get()
        self.data.save_settings()
        self.data.save_saved_words()
        self.root.destroy()


def main():
    # Check for xclip
    try:
        subprocess.run(['xclip', '-version'], capture_output=True, check=True)
    except:
        print("⚠️  Install xclip for auto-search: sudo apt install xclip")
        
    root = tk.Tk()
    app = DictionaryApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()