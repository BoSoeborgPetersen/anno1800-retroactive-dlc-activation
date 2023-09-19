import tkinter as tk
from tkinter import filedialog
import os
from typing import List, Tuple
from lib.enums.DLC import DLC
from lib.a7s.SaveGame import SaveGame
from lib.a7s.GameSetup import GameSetup

# priorly_active_dlcs: List[DLC] = []

class Gui:
    def apply_changes(self):
        dlcs_to_activate = [dlc for dlc in self.selected_dlcs if dlc not in self.priorly_active_dlcs]
        if not self.save_game_file_path:
            self.status_message.set(f"Select an Anno 1800 save game using 'Open Save File'.")
        else:
        # elif dlcs_to_activate:
            self.save_game.remove_dlc_answers()

            self.save_game.save_rda_files("_new")
            new_file_name = self.save_game.save()

            self.status_message.set(f"New file '{new_file_name}' created.")
        # else:
            # self.status_message.set(f"Pick at least one DLC to activate.")

    def update_selected_dlcs(self, dlc: DLC):
        if dlc in self.selected_dlcs:
            self.selected_dlcs.remove(dlc)
        else:
            self.selected_dlcs.append(dlc)
        print(f"DLCs to add: {self.selected_dlcs}") # TODO: Also print hex version, and check log level.

    def open_file(self):
        folder1 = os.path.join(os.getenv("USERPROFILE"), "Documents", "Anno 1800", "accounts")
        folder2 = os.path.join(os.getenv("USERPROFILE"), "OneDrive", "Documents", "Anno 1800", "accounts")

        initial_dir = None
        if os.path.isdir(folder1):
            initial_dir = folder1
        elif os.path.isdir(folder2):
            initial_dir = folder2

        accounts = os.listdir(initial_dir)
        if len(accounts) == 1:
            initial_dir = os.path.join(initial_dir, accounts[0])

        # Set the initial directory to the user's home directory

        # Open the file dialog and save the selected directory
        self.save_game_file_path = filedialog.askopenfilename(initialdir=initial_dir, filetypes=(("Anno 1800 Savegame file", "*.a7s"),))
        self.selected_dir_label.set(os.path.basename(self.save_game_file_path))
        self.refresh_activated_dlcs()

    def refresh_activated_dlcs(self):
        self.selected_dlcs = []
        if self.save_game_file_path:
            self.save_game = SaveGame(self.save_game_file_path)
            self.game_setup = GameSetup(self.save_game.gamesetup)
                        
            self.priorly_active_dlcs = self.game_setup.dlcs
            for (dlc, checkbox) in self.checkboxes:
                checkbox.config(state='active')
                checkbox.deselect()
                if self.priorly_active_dlcs and dlc in self.priorly_active_dlcs:
                    checkbox.select()
                    checkbox.config(state='disabled')

    def __init__(self):
        self.save_game: SaveGame | None = None
        self.game_setup: GameSetup | None = None
        # DLCs selected by the checkboxes
        self.selected_dlcs: List[DLC] = []
        self.save_game_file_path: str | None = None
        self.priorly_active_dlcs: List[DLC] = []

        # Create the main window
        window = tk.Tk()
        window.title("Anno 1800 DLC Activator - Beta 1")
        window.resizable(False, False)

        # configure columns to fill available space
        for i in range(3):
            window.columnconfigure(i, weight=1)

        # configure rows to fill available space
        for i in range(4):
            window.rowconfigure(i, weight=1)

        tk.Label(window, text="Beta version !").grid(row=0, column=0, columnspan=4)
        tk.Label(window, text="May contain bugs and might not work for your save game").grid(row=1, column=0, columnspan=4)
        tk.Button(window, text="Open Save File", command=self.open_file).grid(row=2, column=0, padx=16, pady=16, ipadx=16, columnspan=4)

        self.selected_dir_label = tk.StringVar()
        tk.Label(window, textvariable=self.selected_dir_label).grid(row=3, column=0, padx=16, pady=(0, 16), columnspan=4)

        self.checkboxes: List[Tuple[DLC, tk.Checkbutton]] = []
        # for checkbox_gui_model in get_checkboxes_gui_models():
        i = 0
        for dlc_name in DLC._member_names_:
            cb = tk.Checkbutton(window, text=DLC.__getitem__(dlc_name).name,
                                command=lambda dlc=DLC.__getitem__(dlc_name): self.update_selected_dlcs(dlc))
            cb.grid(row=int(4+(i/3)), padx=16, column=i%3, sticky="w")
            self.checkboxes.append((DLC.__getitem__(dlc_name), cb))
            i = (3 if i == 0 else i + 1)

        tk.Button(window, text="Apply", command=self.apply_changes).grid(row=9, column=0, padx=(32, 32), pady=(32, 16), ipadx=16, sticky="e", columnspan=4)

        self.status_message = tk.StringVar()
        tk.Label(window, textvariable=self.status_message).grid(row=10, column=0, columnspan=4)

        window.mainloop()

if __name__ == '__main__':
    Gui()