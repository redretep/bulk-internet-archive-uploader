import os
import re
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
from internetarchive import configure, upload

# Set up the visual theme
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class IAUploaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Internet Archive Bulk Uploader")
        self.geometry("600x750")
        self.selected_folder = ""

        # --- STEP 1: CREDENTIALS ---
        self.lbl_creds = ctk.CTkLabel(self, text="1. Internet Archive Login", font=("Arial", 14, "bold"))
        self.lbl_creds.pack(pady=(15, 5))

        self.ent_email = ctk.CTkEntry(self, placeholder_text="Email Address", width=450)
        self.ent_email.pack(pady=5)

        self.ent_pass = ctk.CTkEntry(self, placeholder_text="Password", show="*", width=450)
        self.ent_pass.pack(pady=5)

        # --- STEP 2: METADATA ---
        self.lbl_meta = ctk.CTkLabel(self, text="2. Item Metadata", font=("Arial", 14, "bold"))
        self.lbl_meta.pack(pady=(15, 5))

        self.ent_identifier = ctk.CTkEntry(self, placeholder_text="Unique Item Identifier (e.g., katzenjammer-grosser-mann)", width=450)
        self.ent_identifier.pack(pady=5)

        self.ent_title = ctk.CTkEntry(self, placeholder_text="Item Title", width=450)
        self.ent_title.pack(pady=5)

        self.ent_creator = ctk.CTkEntry(self, placeholder_text="Creator / Author", width=450)
        self.ent_creator.pack(pady=5)

        self.ent_date = ctk.CTkEntry(self, placeholder_text="Date (YYYY-MM-DD or YYYY)", width=450)
        self.ent_date.pack(pady=5)

        self.txt_desc = ctk.CTkTextbox(self, width=450, height=60)
        self.txt_desc.pack(pady=5)
        self.txt_desc.insert("0.0", "Description...")

        # --- STEP 3: FILE SELECTION ---
        self.lbl_files = ctk.CTkLabel(self, text="3. Select Files", font=("Arial", 14, "bold"))
        self.lbl_files.pack(pady=(15, 5))

        self.btn_browse = ctk.CTkButton(self, text="Select Folder to Upload", command=self.browse_folder)
        self.btn_browse.pack(pady=5)

        self.lbl_folder_path = ctk.CTkLabel(self, text="No folder selected", text_color="gray")
        self.lbl_folder_path.pack(pady=2)

        # --- STEP 4: UPLOAD & DETAILED LOG ---
        self.btn_upload = ctk.CTkButton(self, text="START BULK UPLOAD", fg_color="green", hover_color="darkgreen", font=("Arial", 14, "bold"), command=self.start_upload_thread)
        self.btn_upload.pack(pady=(15, 10))

        self.lbl_log_title = ctk.CTkLabel(self, text="Detailed Upload Status:", font=("Arial", 12, "bold"))
        # FIXED: Changed px=75 to padx=75
        self.lbl_log_title.pack(anchor="w", padx=75, pady=(5, 2))

        self.txt_log = ctk.CTkTextbox(self, width=450, height=150, font=("Courier New", 12))
        self.txt_log.pack(pady=5)
        self.log_message("System ready. Awaiting folder selection...")

    def log_message(self, message):
        self.txt_log.insert("end", f"{message}\n")
        self.txt_log.see("end")

    def clean_identifier(self, identifier):
        id_clean = identifier.lower()
        id_clean = id_clean.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
        id_clean = re.sub(r'[^a-z0-9._-]', '-', id_clean)
        id_clean = re.sub(r'-+', '-', id_clean)
        return id_clean.strip('-')

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.selected_folder = folder
            self.lbl_folder_path.configure(text=f"Selected: {os.path.basename(folder)}", text_color="white")
            self.log_message(f"Selected folder: {folder}")

    def start_upload_thread(self):
        threading.Thread(target=self.process_upload, daemon=True).start()

    def process_upload(self):
        email = self.ent_email.get().strip()
        password = self.ent_pass.get().strip()
        raw_identifier = self.ent_identifier.get().strip()
        title = self.ent_title.get().strip()
        creator = self.ent_creator.get().strip()
        date = self.ent_date.get().strip()
        description = self.txt_desc.get("1.0", "end-1c").strip()

        if not email or not password:
            messagebox.showerror("Error", "Please enter your IA email and password.")
            return
        if not raw_identifier or not title:
            messagebox.showerror("Error", "Identifier and Title are required.")
            return
        if not self.selected_folder:
            messagebox.showerror("Error", "Please select a folder containing the files.")
            return

        identifier = self.clean_identifier(raw_identifier)
        if identifier != raw_identifier:
            self.log_message(f"NOTICE: Adjusted identifier to match IA rules: '{identifier}'")

        files_to_upload = []
        for root, dirs, files in os.walk(self.selected_folder):
            for file in files:
                files_to_upload.append(os.path.join(root, file))

        total_files = len(files_to_upload)
        if total_files == 0:
            messagebox.showerror("Error", "The selected folder is empty.")
            return

        self.log_message(f"Found {total_files} files to upload.")

        try:
            self.log_message("Authenticating with archive.org...")
            configure(email, password, host='archive.org')
            self.log_message("Authentication successful.")

            metadata = {
                'title': title,
                'mediatype': 'audio',
                'creator': creator,
                'date': date,
                'description': description
            }

            for index, file_path in enumerate(files_to_upload, start=1):
                file_name = os.path.basename(file_path)
                self.log_message(f"[{index}/{total_files}] Uploading: {file_name}...")
                
                r = upload(identifier, files=[file_path], metadata=metadata, verbose=True)
                
                if r[0].status_code == 200:
                    self.log_message(f" -> Successfully uploaded {file_name}")
                else:
                    self.log_message(f" -> ERROR: Failed on {file_name} (Code: {r[0].status_code})")
                    raise Exception(f"Server rejected file {file_name}")

            self.log_message("--- ALL UPLOADS COMPLETE ---")
            self.log_message(f"Your item is processing at: https://archive.org/details/{identifier}")
            messagebox.showinfo("Success", f"All files uploaded successfully to item page:\n{identifier}")

        except Exception as e:
            self.log_message(f"CRITICAL ERROR: {str(e)}")
            messagebox.showerror("Error", f"An error occurred during upload:\n{str(e)}")

if __name__ == "__main__":
    app = IAUploaderApp()
    app.mainloop()