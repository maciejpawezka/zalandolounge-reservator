import tkinter as tk
from tkinter import ttk, messagebox
import threading
from browser_utils import launch_browser
from reserve import login, reserve
from campaign import campaign_grab


class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Zalando Lounge Reservator")
        self.root.configure(bg="#f5f6fa")
        self.root.resizable(False, False)
        self.driver = None
        self.running = False
        self.password_visible = False
        self.mode = None
        self._build_gui()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_gui(self):
        self.BG = "#f5f6fa"
        CARD_BG = "#ffffff"
        ACCENT = "#2563eb"
        TEXT = "#1e293b"
        TEXT_LIGHT = "#64748b"
        BORDER = "#e2e8f0"
        SUCCESS = "#16a34a"
        INPUT_BG = "#f8fafc"

        self._card_bg = CARD_BG
        self._input_bg = INPUT_BG
        self._text = TEXT
        self._accent = ACCENT
        self._accent_hover = "#1d4ed8"
        self._border = BORDER
        self._text_light = TEXT_LIGHT

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Main.TFrame", background=self.BG)
        style.configure("Card.TFrame", background=CARD_BG)
        style.configure("Title.TLabel", background=self.BG, foreground=ACCENT,
                         font=("Segoe UI", 18, "bold"))
        style.configure("Subtitle.TLabel", background=self.BG, foreground=TEXT_LIGHT,
                         font=("Segoe UI", 9))
        style.configure("Field.TLabel", background=CARD_BG, foreground=TEXT,
                         font=("Segoe UI", 10))
        style.configure("Status.TLabel", background=self.BG, foreground=SUCCESS,
                         font=("Segoe UI", 10))

        main = ttk.Frame(self.root, style="Main.TFrame", padding=30)
        main.pack(fill="both", expand=True)
        self.main = main

        ttk.Label(main, text="🛒 Zalando Lounge Reservator",
                  style="Title.TLabel").pack(pady=(0, 2))
        ttk.Label(main, text="Automatic product reservation",
                  style="Subtitle.TLabel").pack(pady=(0, 20))

        mode_frame = tk.Frame(main, bg=self.BG)
        mode_frame.pack(fill="x", pady=(0, 15))

        self.btn_reserve_mode = tk.Button(
            mode_frame, text="🔗  Product Reserve",
            font=("Segoe UI", 12, "bold"),
            bg=CARD_BG, fg=TEXT, activebackground="#e0e7ff",
            activeforeground=ACCENT, relief="solid", bd=1,
            cursor="hand2", pady=14,
            command=lambda: self._select_mode("reserve")
        )
        self.btn_reserve_mode.pack(side="left", expand=True, fill="x", padx=(0, 6))

        self.btn_campaign_mode = tk.Button(
            mode_frame, text="🛍️  Campaign Grab",
            font=("Segoe UI", 12, "bold"),
            bg=CARD_BG, fg=TEXT, activebackground="#e0e7ff",
            activeforeground=ACCENT, relief="solid", bd=1,
            cursor="hand2", pady=14,
            command=lambda: self._select_mode("campaign")
        )
        self.btn_campaign_mode.pack(side="left", expand=True, fill="x", padx=(6, 0))

        self.card_frame = tk.Frame(main, bg=self.BG)
        self.entries = {}

        btn_frame = tk.Frame(main, bg=self.BG)
        btn_frame.pack(fill="x", pady=(5, 10))
        self.action_btn_frame = btn_frame

        self.btn_start = tk.Button(
            btn_frame, text="▶  START",
            font=("Segoe UI", 11, "bold"),
            bg=ACCENT, fg="white", activebackground=self._accent_hover,
            activeforeground="white", relief="flat", bd=0,
            cursor="hand2", padx=30, pady=10,
            command=self._on_start
        )
        self.btn_start.pack(side="left", expand=True, fill="x", padx=(0, 5), ipady=2)

        self.btn_stop = tk.Button(
            btn_frame, text="■  STOP",
            font=("Segoe UI", 10, "bold"),
            bg="#94a3b8", fg="white", activebackground="#dc2626",
            activeforeground="white", relief="flat", bd=0,
            cursor="hand2", padx=20, pady=8,
            state="disabled", command=self._on_stop
        )
        self.btn_stop.pack(side="left", expand=True, fill="x", padx=(5, 0), ipady=2)

        self.status_var = tk.StringVar(value="Select a mode to begin")
        ttk.Label(main, textvariable=self.status_var,
                  style="Status.TLabel").pack(anchor="w", pady=(0, 5))

        log_frame = tk.Frame(main, bg=self.BG)
        log_frame.pack(fill="both", expand=True, pady=(5, 0))

        self.log_text = tk.Text(
            log_frame, height=8, bg="#f1f5f9", fg=TEXT,
            font=("Consolas", 9), relief="solid", bd=1,
            insertbackground=ACCENT, state="disabled", wrap="word"
        )
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        self.log_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.root.geometry("580x640")
        self.root.minsize(580, 400)

    def _select_mode(self, mode):
        self.mode = mode

        if mode == "reserve":
            self.btn_reserve_mode.configure(
                bg=self._accent, fg="white", relief="flat"
            )
            self.btn_campaign_mode.configure(
                bg=self._card_bg, fg=self._text, relief="solid"
            )
        else:
            self.btn_campaign_mode.configure(
                bg=self._accent, fg="white", relief="flat"
            )
            self.btn_reserve_mode.configure(
                bg=self._card_bg, fg=self._text, relief="solid"
            )

        self.card_frame.pack_forget()
        for w in self.card_frame.winfo_children():
            w.destroy()
        self.entries.clear()

        card = ttk.Frame(self.card_frame, style="Card.TFrame", padding=20)
        card.pack(fill="x")

        if mode == "reserve":
            self._add_field(card, "Product URL:", "url", 0)
            self._add_field(card, "Email:", "email", 1)
            self._add_password_field(card, 2)
            self._add_field(card, "Sizes (e.g. M,L,XL):", "sizes", 3)
        else:
            self._add_field(card, "Campaign Code:", "code", 0)
            self._add_field(card, "Email:", "email", 1)
            self._add_password_field(card, 2)
            self._add_field(card, "Sizes (e.g. M,L,XL):", "sizes", 3)
            self._add_field(card, "Brand:", "brand", 4)

            lbl = ttk.Label(card, text="Sort:", style="Field.TLabel")
            lbl.grid(row=5, column=0, sticky="w", pady=6, padx=(0, 12))
            self.sort_var = tk.StringVar(value="Popularne")
            sort_combo = ttk.Combobox(
                card, textvariable=self.sort_var,
                values=["Popularne", "Najniższa cena", "Najwyższa cena", "Wyprzedaż"],
                state="readonly", font=("Segoe UI", 10), width=42
            )
            sort_combo.grid(row=5, column=1, pady=6, sticky="ew")

        card.columnconfigure(1, weight=1)

        self.card_frame.pack(fill="x", pady=(0, 15),
                             before=self.action_btn_frame)

        self._set_status("Ready")

    def _add_field(self, card, label_text, key, row):
        ttk.Label(card, text=label_text, style="Field.TLabel").grid(
            row=row, column=0, sticky="w", pady=6, padx=(0, 12)
        )
        entry = tk.Entry(
            card, width=45, font=("Segoe UI", 10),
            bg=self._input_bg, fg=self._text,
            relief="solid", bd=1,
            highlightthickness=2, highlightcolor=self._accent,
            highlightbackground=self._border
        )
        entry.grid(row=row, column=1, pady=6, sticky="ew")
        self.entries[key] = entry

    def _add_password_field(self, card, row):
        ttk.Label(card, text="Password:", style="Field.TLabel").grid(
            row=row, column=0, sticky="w", pady=6, padx=(0, 12)
        )
        pw_frame = tk.Frame(card, bg=self._card_bg)
        pw_frame.grid(row=row, column=1, pady=6, sticky="ew")

        entry = tk.Entry(
            pw_frame, width=38, font=("Segoe UI", 10),
            show="•", bg=self._input_bg, fg=self._text,
            relief="solid", bd=1,
            highlightthickness=2, highlightcolor=self._accent,
            highlightbackground=self._border
        )
        entry.pack(side="left", fill="x", expand=True)

        self.btn_toggle_pw = tk.Button(
            pw_frame, text="👁", font=("Segoe UI", 10),
            bg=self._card_bg, fg=self._text_light, relief="flat", bd=0,
            cursor="hand2", command=self._toggle_password,
            activebackground=self._card_bg
        )
        self.btn_toggle_pw.pack(side="right", padx=(4, 0))

        self.entries["password"] = entry
        self.password_visible = False

    def _toggle_password(self):
        self.password_visible = not self.password_visible
        entry = self.entries["password"]
        if self.password_visible:
            entry.configure(show="")
            self.btn_toggle_pw.configure(text="🔒")
        else:
            entry.configure(show="•")
            self.btn_toggle_pw.configure(text="👁")

    def _log(self, msg):
        def _update():
            self.log_text.configure(state="normal")
            self.log_text.insert("end", msg + "\n")
            self.log_text.see("end")
            self.log_text.configure(state="disabled")
        self.root.after(0, _update)

    def _set_status(self, msg):
        self.root.after(0, lambda: self.status_var.set(msg))

    def _on_start(self):
        if not self.mode:
            messagebox.showwarning("No mode", "Please select a mode first.")
            return

        email = self.entries.get("email")
        password = self.entries.get("password")
        sizes_entry = self.entries.get("sizes")

        if not email or not password or not sizes_entry:
            messagebox.showwarning("Missing data", "Please fill in all fields.")
            return

        email_val = email.get().strip()
        pw_val = password.get().strip()
        sizes_raw = sizes_entry.get().strip()

        if not all([email_val, pw_val, sizes_raw]):
            messagebox.showwarning("Missing data", "Please fill in Email, Password and Sizes.")
            return

        sizes = [s.strip() for s in sizes_raw.split(",")]

        if self.mode == "reserve":
            url = self.entries["url"].get().strip()
            if not url:
                messagebox.showwarning("Missing data", "Please enter the Product URL.")
                return
        else:
            code = self.entries["code"].get().strip()
            if not code:
                messagebox.showwarning("Missing data", "Please enter the Campaign Code.")
                return

        self.running = True
        self.btn_start.configure(state="disabled", bg="#94a3b8")
        self.btn_stop.configure(state="normal", bg="#ef4444")
        for e in self.entries.values():
            e.configure(state="disabled")

        if self.mode == "reserve":
            thread = threading.Thread(
                target=self._run_reserve, args=(url, email_val, pw_val, sizes),
                daemon=True
            )
        else:
            sort = self.sort_var.get()
            brand_entry = self.entries.get("brand")
            brand_val = brand_entry.get().strip() if brand_entry else ""
            thread = threading.Thread(
                target=self._run_campaign, args=(code, email_val, pw_val, sizes, sort, brand_val),
                daemon=True
            )

        thread.start()

    def _on_stop(self):
        self.running = False
        self._set_status("Stopping...")
        self._log("Stopping...")

    def _on_close(self):
        self.running = False
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
        self.root.destroy()

    def _reset_ui(self):
        def _r():
            self.btn_start.configure(state="normal", bg=self._accent)
            self.btn_stop.configure(state="disabled", bg="#94a3b8")
            for e in self.entries.values():
                e.configure(state="normal")
        self.root.after(0, _r)

    def _run_reserve(self, url, email, password, sizes):
        try:
            self._set_status("Launching browser...")
            self._log("=== Product Reserve Mode ===")
            self._log("Launching browser...")

            self.driver = launch_browser()

            self._set_status("Logging in...")
            login(self.driver, url, email, password, log=self._log)

            if not self.running:
                return

            self._set_status(f"Looking for: {', '.join(sizes)}")
            self._log(f"Looking for sizes: {', '.join(sizes)}")

            success = reserve(
                self.driver, sizes,
                log=self._log,
                is_running=lambda: self.running
            )

            if success:
                self._set_status("✅ Success! Product added to cart.")
            elif not self.running:
                self._set_status("Stopped.")

        except Exception as e:
            self._log(f"Error: {e}")
            self._set_status("Error")
        finally:
            self._reset_ui()

    def _run_campaign(self, code, email, password, sizes, sort, brand):
        try:
            self._set_status("Launching browser...")
            self._log("=== Campaign Grab Mode ===")
            self._log("Launching browser...")

            self.driver = launch_browser()

            self._set_status("Logging in & waiting for campaign...")

            added = campaign_grab(
                self.driver, code, email, password, sizes, sort, brand,
                log=self._log,
                is_running=lambda: self.running
            )

            if added >= 20:
                self._set_status(f"✅ Done! {added} products in cart.")
            elif not self.running:
                self._set_status(f"Stopped. {added} products in cart.")
            else:
                self._set_status(f"Finished. {added} products added to cart.")

        except Exception as e:
            self._log(f"Error: {e}")
            self._set_status("Error")
        finally:
            self._reset_ui()
