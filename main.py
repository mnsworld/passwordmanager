import customtkinter as ctk
import vault

# theme colors - from coolars website
BG_COLOR = "#fdeded" # lavendar blush
CARD_COLOR = "#fbfffe" # white
TEXT_DARK = "#001514" # black
TEXT_MUTED = "#5f4b66" # vintage grape
ACCENT_CORAL = "#f08080" # light coral
ACCENT_CORAL_TEXT = "#f4978e" # salmon

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

class PasswordManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Local Password Manager")
        self.geometry("480x560")
        self.configure(fg_color=BG_COLOR)

        self.master_password = None
        self.entries = []

        if vault.vault_exists():
            self.show_unlock_screen()
        else:
            self.show_setup_screen()


    #------------ first page, master password------------#
    def show_setup_screen(self):
        self._clear()
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(expand=True, fill="both", padx=40, pady=40)

        ctk.CTkLabel(
            frame, text="Create your master password",
            font=ctk.CTkFont(size=20, weight="bold"), text_color=TEXT_DARK
        ).pack(pady=(20, 6))

        ctk.CTkLabel(
            frame,
            text="This protects everything in your vault.\nThere is no way to recover it if you forget it.",
            font=ctk.CTkFont(size=12), text_color=TEXT_MUTED, justify="center"
        ).pack(pady=(0, 24))

        pw_entry = ctk.CTkEntry(
            frame, placeholder_text="Master password", show="*", width=300,
            fg_color=CARD_COLOR, border_color="#e5d5c8", corner_radius=12, text_color=TEXT_DARK
        )
        pw_entry.pack(pady=8)

        error_label = ctk.CTkLabel(frame, text="", text_color="red", font=ctk.CTkFont(size=12))
        error_label.pack(pady=4)

        def on_create():
            pw = pw_entry.get()
            if len(pw) < 8:
                error_label.configure(text="Password must be at least 8 characters.")
                return
            vault.create_vault(pw)
            self.master_password = pw
            self.entries = []
            self.show_main_screen()

        ctk.CTkButton(
            frame, text="Create vault", command=on_create, width=300, corner_radius=12,
            fg_color=ACCENT_CORAL, text_color=ACCENT_CORAL_TEXT, hover_color="#e8584a"
        ).pack(pady=20)


    #------------ unlock exisiting vault------------#
    def show_unlock_screen(self):
        self._clear()
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(expand=True, fill="both", padx=40, pady=40)

        ctk.CTkLabel(
            frame, text="Unlock your vault",
            font=ctk.CTkFont(size=20, weight="bold"), text_color=TEXT_DARK
        ).pack(pady=(60, 24))

        pw_entry = ctk.CTkEntry(
            frame, placeholder_text="Master password", show="*", width=300,
            fg_color=CARD_COLOR, border_color=ACCENT_CORAL, corner_radius=12
        )
        pw_entry.pack(pady=8)
        pw_entry.bind("<Return>", lambda e: on_unlock())

        error_label = ctk.CTkLabel(frame, text="", text_color="#d85a30", font=ctk.CTkFont(size=12))
        error_label.pack(pady=4)

        def on_unlock():
            pw = pw_entry.get()
            try:
                loaded_entries = vault.load_vault(pw)
            except vault.WrongPasswordError:
                error_label.configure(text="Incorrect password.")
                pw_entry.delete(0, "end")
                return
            self.master_password = pw
            self.entries = loaded_entries
            self.show_main_screen()

        ctk.CTkButton(
            frame, text="Unlock", command=on_unlock, width=300, corner_radius=12,
            fg_color=ACCENT_CORAL, text_color=BG_COLOR, hover_color="#e8584a" # voliet
        ).pack(pady=20)
        pw_entry.focus()

    #-------- wipe window to build new screem--#
    # helper-#
    def _clear(self):
        for widget in self.winfo_children():
            widget.destroy()


    # frame - main vault screen #

    def show_main_screen(self):
        self._clear()

        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.pack(fill="x",padx=20, pady=(20,10))


# Your Vault text
        ctk.CTkLabel(
            top_bar, text="Your vault", font=ctk.CTkFont(size=20, weight="bold"), text_color=TEXT_DARK
        ).pack(side="left")

        ctk.CTkButton(
            top_bar, text="+ Add entry", width=110, corner_radius=20,
            fg_color=ACCENT_CORAL, text_color=BG_COLOR, hover_color="#e8584a",# dark coral hover color ###########
            command=self.show_add_entry_dialog
        ).pack(side="right")

        self.entry_list_frame = ctk.CTkScrollableFrame(
            self, width=440, height=420, fg_color="transparent"
        )
        self.entry_list_frame.pack(expand=True, fill="both", padx=20, pady=10)

        self.refresh_entry_list()

    # fills with what is in self entires ----- #

    def refresh_entry_list(self):
        for widget in self.entry_list_frame.winfo_children():
            widget.destroy()

        if not self.entries:
            ctk.CTkLabel(
                self.entry_list_frame, text =" No entries yet.",
                text_color=BG_COLOR).pack(pady=30) # violet text
            return

        avatar_colors = ["#f5c4b3", "#cebcf6", "#9fe1cb", "#f4c0d1", "#fac775"] # colors for entries

        for index, entry in enumerate(self.entries):
            row = ctk.CTkFrame(self.entry_list_frame, fg_color=CARD_COLOR, corner_radius=16)
            row.pack(fill="x", pady=6, padx=4)

            avatar_color = avatar_colors[index % len(avatar_colors)]
            initial = entry["site"][0].upper() if entry["site"] else "?"

            avatar = ctk.CTkLabel(
                row, text=initial, width=32, height=32, corner_radius=16,
                fg_color=avatar_color, text_color=TEXT_DARK,
                font=ctk.CTkFont(size=13, weight="bold")
            )
            avatar.pack(side="left", padx=(14, 10), pady=12)

            text_col = ctk.CTkFrame(row, fg_color="transparent")
            text_col.pack(side="left", fill="x", expand=True, pady=10)

            ctk.CTkLabel(
                text_col, text=entry["site"], font=ctk.CTkFont(size=13, weight="bold"),
                text_color=TEXT_DARK, anchor="w"
            ).pack(fill="x")
            ctk.CTkLabel(
                text_col, text=entry["username"], text_color=TEXT_MUTED,
                font=ctk.CTkFont(size=11), anchor="w"
            ).pack(fill="x")

            btn_col = ctk.CTkFrame(row, fg_color="transparent")
            btn_col.pack(side="right", padx=10)

            ctk.CTkButton(
                btn_col, text="View", width=60, corner_radius=10,
                fg_color=ACCENT_CORAL, text_color=CARD_COLOR, hover_color="#e8584a", # hover color
                command=lambda i=index: self.show_view_entry_dialog(i)
            ).pack(side="left", padx=4)
            ctk.CTkButton(
                btn_col, text="Delete", width=60, corner_radius=10,
                fg_color="transparent", border_width=1, border_color="#e5b3a3",
                text_color=TEXT_MUTED, hover_color="#f5e3da", #
                command=lambda i=index: self.delete_entry(i)
            ).pack(side="left", padx=4)

      # add entry popup
    def show_add_entry_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add new entry")
        dialog.geometry("360x340")
        dialog.configure(fg_color=BG_COLOR)
        dialog.transient(self)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Site", text_color=TEXT_MUTED, font=ctk.CTkFont(size=12)).pack(pady=(24, 4))
        site_entry = ctk.CTkEntry(dialog, width=280, fg_color=CARD_COLOR, corner_radius=10, border_color="#e5d5c8", text_color=TEXT_DARK)
        site_entry.pack()

        ctk.CTkLabel(dialog, text="Username / email", text_color=TEXT_MUTED, font=ctk.CTkFont(size=12)).pack(pady=(16, 4))
        user_entry = ctk.CTkEntry(dialog, width=280, fg_color=CARD_COLOR, corner_radius=10, border_color="#e5d5c8", text_color=TEXT_DARK)
        user_entry.pack()

        ctk.CTkLabel(dialog, text="Password", text_color=TEXT_MUTED, font=ctk.CTkFont(size=12)).pack(pady=(16, 4))
        pass_entry = ctk.CTkEntry(dialog, width=280, show="*", fg_color=CARD_COLOR, corner_radius=10, border_color="#e5d5c8", text_color=TEXT_DARK)
        pass_entry.pack()

        error_label = ctk.CTkLabel(dialog, text="", text_color="#d85a30", font=ctk.CTkFont(size=12))
        error_label.pack(pady=(8, 0))

        def on_save():
            site = site_entry.get().strip()
            username = user_entry.get().strip()
            password = pass_entry.get()
            if not site or not password:
                error_label.configure(text="Site and password are required.")
                return
            self.entries.append({"site": site, "username": username, "password": password})
            vault.save_vault(self.master_password, self.entries)
            self.refresh_entry_list()
            dialog.destroy()

        ctk.CTkButton(
            dialog, text="Save entry", command=on_save, width=280, corner_radius=12,
            fg_color=ACCENT_CORAL, text_color=BG_COLOR, hover_color="#e8584a"
        ).pack(pady=20)
        site_entry.focus()
         #######################

        # ---------- view entry popup ----------

    def show_view_entry_dialog(self, index):
        entry = self.entries[index]
        dialog = ctk.CTkToplevel(self)
        dialog.title(entry["site"])
        dialog.geometry("360x300")
        dialog.configure(fg_color=BG_COLOR)
        dialog.transient(self)
        dialog.grab_set()

        ctk.CTkLabel(
            dialog, text=entry["site"], font=ctk.CTkFont(size=16, weight="bold"), text_color=TEXT_DARK
        ).pack(pady=(24, 16))

        ctk.CTkLabel(dialog, text="Username / email", text_color=TEXT_MUTED, font=ctk.CTkFont(size=12)).pack()
        user_box = ctk.CTkEntry(
            dialog, width=280, fg_color=CARD_COLOR, corner_radius=10,
            border_color="#e5d5c8", text_color=TEXT_DARK
        )
        user_box.insert(0, entry["username"])
        user_box.configure(state="readonly")
        user_box.pack(pady=(0, 12))

        ctk.CTkLabel(dialog, text="Password", text_color=TEXT_MUTED, font=ctk.CTkFont(size=12)).pack()
        pw_box = ctk.CTkEntry(
            dialog, width=280, show="*", fg_color=CARD_COLOR, corner_radius=10,
            border_color="#e5d5c8", text_color=TEXT_DARK
        )
        pw_box.insert(0, entry["password"])
        pw_box.configure(state="readonly")
        pw_box.pack(pady=(0, 16))

        def toggle_visibility():
            current = pw_box.cget("show")
            pw_box.configure(show="" if current == "*" else "*")

        ctk.CTkButton(
            dialog, text="Show / Hide password", command=toggle_visibility, width=280, corner_radius=12,
            fg_color=ACCENT_CORAL, border_width=1, border_color="#e5b3a3", text_color=TEXT_MUTED,
            hover_color="#f5e3da"
        ).pack(pady=8)

#----- delete entries----#
    def delete_entry(self, index):
        del self.entries[index]
        vault.save_vault(self.master_password, self.entries)
        self.refresh_entry_list()


if __name__ == "__main__":
        app = PasswordManagerApp()
        app.mainloop()
