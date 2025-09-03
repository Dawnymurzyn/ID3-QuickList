import os
import shutil
from tkinter import Tk, Label, Button, Entry, filedialog, messagebox
from mutagen.id3 import ID3, TRCK

class MP3RenumberTool:
    def __init__(self, master):
        self.master = master
        self.master.title("MP3 Track Renumber Tool")

        self.folder_path = ""
        self.file_to_insert = ""
        
        Label(master, text="Step 1: Select MP3 folder").pack(pady=5)
        Button(master, text="Browse Folder", command=self.browse_folder).pack(pady=5)

        Label(master, text="Step 2: Select MP3 file to insert").pack(pady=5)
        Button(master, text="Browse MP3 File", command=self.browse_file).pack(pady=5)

        Label(master, text="Step 3: Enter track number to insert at").pack(pady=5)
        self.track_entry = Entry(master)
        self.track_entry.pack(pady=5)

        Button(master, text="Execute", command=self.execute).pack(pady=10)

    def browse_folder(self):
        self.folder_path = filedialog.askdirectory(title="Select MP3 Folder")
        if self.folder_path:
            messagebox.showinfo("Folder Selected", f"Selected folder:\n{self.folder_path}")

    def browse_file(self):
        self.file_to_insert = filedialog.askopenfilename(
            title="Select MP3 File",
            filetypes=[("MP3 Files", "*.mp3")]
        )
        if self.file_to_insert:
            messagebox.showinfo("File Selected", f"Selected file:\n{self.file_to_insert}")

    def execute(self):
        if not self.folder_path or not self.file_to_insert:
            messagebox.showerror("Error", "Please select both folder and MP3 file.")
            return

        try:
            insert_number = int(self.track_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid track number.")
            return

        files = [f for f in os.listdir(self.folder_path) if f.lower().endswith('.mp3')]
        files.sort()

        # Shift existing tracks
        for filename in sorted(files, reverse=True):
            try:
                track_num = int(filename[:2])
            except ValueError:
                continue  # ignore files without valid two-digit prefix
            if track_num >= insert_number:
                new_num = track_num + 1
                old_path = os.path.join(self.folder_path, filename)
                new_name = f"{new_num:02d}{filename[2:]}"
                new_path = os.path.join(self.folder_path, new_name)
                os.rename(old_path, new_path)

                # Update ID3 track number
                audio = ID3(new_path)
                audio["TRCK"] = TRCK(encoding=3, text=str(new_num))
                audio.save(v2_version=3)

        # Insert new file
        base_name = os.path.basename(self.file_to_insert)
        if base_name[:2].isdigit():
            new_name = f"{insert_number:02d}{base_name[2:]}"
        else:
            new_name = f"{insert_number:02d} {base_name}"

        destination = os.path.join(self.folder_path, new_name)
        shutil.copy2(self.file_to_insert, destination)

        audio = ID3(destination)
        audio["TRCK"] = TRCK(encoding=3, text=str(insert_number))
        audio.save(v2_version=3)

        messagebox.showinfo("Success", "Tracks have been renumbered and file inserted successfully.")

def main():
    root = Tk()
    app = MP3RenumberTool(root)
    root.mainloop()

if __name__ == "__main__":
    main()
