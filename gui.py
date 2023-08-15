import tkinter.ttk as ttk
from tkinter import *
import tkinter as tk
import pandas as pd
import customtkinter
from CTkTable import *
import os
from PIL import Image
import threading
from db import get_plate_numbers, insert_detected_plate_number, insert_whitelist, delete_whitelist_entry, get_whitelists, delete_whitelist_entry, update_whitelist_entry
from tkinter import messagebox
import ttkthemes
from datetime import datetime

os.chdir(os.path.dirname(os.path.abspath(__file__)))

class MainGui(customtkinter.CTk):
    def __init__(self, start_anpr=None):
        super().__init__()
        self.title('Plate Number Detection')
        width = 1300
        height = 600
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        self.resizable(False, False)

        # variable initialization
        self.whitelists = get_whitelists
        self.plate_numbers = get_plate_numbers()
        self.start_anpr = start_anpr
        # self.detected_plate_number = detected_plate_number
        # self.detected_time_stamp = detected_time_stamp
        # self.detected_image_dir = detected_image_dir

        # set grid layout 1x2
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # load images with light and dark mode image
        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_images")
        self.image_icon_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "image_icon_light.png")), size=(20, 20))
        self.home_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "home_dark.png")),
                                                 dark_image=Image.open(os.path.join(image_path, "home_light.png")), size=(20, 20))
        self.chat_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "chat_dark.png")),
                                                 dark_image=Image.open(os.path.join(image_path, "chat_light.png")), size=(20, 20))
        self.add_user_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "add_user_dark.png")),
                                                     dark_image=Image.open(os.path.join(image_path, "add_user_light.png")), size=(20, 20))

        # create navigation frame
        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(4, weight=1)

        self.home_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Home",
                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                   image=self.home_image, anchor="w", command=self.home_button_event)
        self.home_button.grid(row=1, column=0, sticky="ew")

        self.frame_2_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Whitelist",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      image=self.chat_image, anchor="w", command=self.frame_2_button_event)
        self.frame_2_button.grid(row=2, column=0, sticky="ew")

        # self.frame_3_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Frame 3",
        #                                               fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
        #                                               image=self.add_user_image, anchor="w", command=self.frame_3_button_event)
        # self.frame_3_button.grid(row=3, column=0, sticky="ew")

        # create home frame
        self.home_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.home_frame.grid(row=0, column=0, sticky='nsew')
        
        self.header_wrapper = customtkinter.CTkFrame(self.home_frame, corner_radius=0)
        self.header_wrapper.grid_columnconfigure(1, weight=1)
        self.header_wrapper.grid(row=0, column=0, sticky='we')

        self.start_detection = customtkinter.CTkButton(self.header_wrapper, text="Start Detection", command=self.start_anpr, height=40)
        self.start_detection.grid(row=0, column=4, pady=10, sticky='e')

        # table contents
        self.detected_table_scroll = Scrollbar(self.home_frame, orient='vertical')
        self.detected_table_scroll.grid(row=1, column=1, sticky='ns')

        self.detected_table = ttk.Treeview(self.home_frame, columns=("name", "age", "reason", "plate_number", "time_in", 'classification'), yscrollcommand=self.detected_table_scroll.set, xscrollcommand=self.detected_table_scroll.set)

        self.detected_table.grid(row=1, column=0, sticky='nsew')

        self.home_frame.grid_rowconfigure(1, weight=1)
        self.home_frame.grid_columnconfigure(0, weight=1)
        self.detected_table_scroll.configure(command=self.detected_table.yview)
        self.detected_table.configure(xscrollcommand=self.detected_table_scroll.set)

        self.detected_table.column("#0", minwidth=0, width=60) 
        self.detected_table.heading("#0", text="ID") 

        self.detected_table.column("name", anchor='w')
        self.detected_table.heading("name", text="Name", anchor='w')

        self.detected_table.column("age", anchor='w', width=80)
        self.detected_table.heading("age", text="Age", anchor='w')

        self.detected_table.column("reason", anchor='w')
        self.detected_table.heading("reason", text="Reason", anchor='w')

        self.detected_table.column("plate_number", anchor='w')
        self.detected_table.heading("plate_number", text="Plate Number", anchor='w')

        self.detected_table.column("time_in", anchor='w')
        self.detected_table.heading("time_in", text="Time in", anchor='w')

        self.detected_table.column("classification", anchor='w', width=110)
        self.detected_table.heading("classification", text="Classification", anchor='w')

        self.detected_table.tag_configure("unauthorized", background='lightgrey', font=('arial', 12))        

        self.style = ttkthemes.ThemedStyle(self)
        self.style.theme_use('clam')
        self.style.configure("Treeview", font=('Verdana', 11), rowheight=25)
        self.style.configure("Treeview.Heading", font=('Verdana', 11, 'bold'), background='White')
        self.style.map("Treeview",
          foreground=self.fixed_map("foreground"),
          background=self.fixed_map("background"))
        
        # create second frame
        self.second_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.second_frame.grid(row=0, column=0, sticky='nsew')

        # whitelist header
        self.whitelist_header_wrapper = customtkinter.CTkFrame(self.second_frame, corner_radius=0)
        self.whitelist_header_wrapper.grid_columnconfigure(0, weight=1)
        self.whitelist_header_wrapper.grid(row=0, column=0, sticky='sw')

        self.whitelist_name_entry = customtkinter.CTkEntry(self.whitelist_header_wrapper, placeholder_text="Name", height=40, width=200)
        self.whitelist_name_entry.grid(column=0, row=0, sticky="w", padx=5)

        self.whitelist_plate_number_entry = customtkinter.CTkEntry(self.whitelist_header_wrapper, placeholder_text="Plate Number", height=40, width=200)
        self.whitelist_plate_number_entry.grid(column=1, row=0, sticky="w", padx=5)
        
        self.classficiation_combobox = customtkinter.CTkComboBox(self.whitelist_header_wrapper, values=["Visitor", "Student", "Employee"],
                                     command=self.handle_get_classification,
                                     height=40)
        self.classficiation_combobox.grid(row=0, column=2, sticky="ew", pady=10)

        self.update_whitelist_button = customtkinter.CTkButton(self.whitelist_header_wrapper, text="Update", height=40, command=self.handle_update_whitelist_entry)
        self.update_whitelist_button.grid(row=0, column=3, pady=10, padx=10, sticky='w')

        self.delete_whitelist_button = customtkinter.CTkButton(self.whitelist_header_wrapper, text="Delete", height=40, command=self.handle_remove_whitelist_entry)
        self.delete_whitelist_button.grid(row=0, column=4, pady=10, sticky='w')

        self.new_whitelist_button = customtkinter.CTkButton(self.whitelist_header_wrapper, text="New", height=40, command=self.handle_add_whitelist_entry)
        self.new_whitelist_button.grid(row=0, column=5, pady=10, sticky='w', padx=10)

        

        self.whitelist_table_scroll = Scrollbar(self.second_frame, orient='vertical')
        self.whitelist_table_scroll.grid(row=1, column=1, sticky='ns')

        self.whitelist_table = ttk.Treeview(self.second_frame, columns=("name", "plate_number"), yscrollcommand=self.whitelist_table_scroll.set, xscrollcommand=self.whitelist_table_scroll.set)
        self.second_frame.grid_rowconfigure(1, weight=1)
        self.second_frame.grid_columnconfigure(0, weight=1)

        
        self.whitelist_table.column("#0", minwidth=0, width=30) 
        self.whitelist_table.heading("#0", text="ID") 

        self.whitelist_table.column("name", anchor='w')
        self.whitelist_table.heading("name", text="Name", anchor='w')

        self.whitelist_table.column("plate_number", anchor='w')
        self.whitelist_table.heading("plate_number", text="Plate Number", anchor='w')

        self.whitelist_table.grid(row=1, column=0, sticky='nsew')

        self.whitelist_table_scroll.configure(command=self.whitelist_table.yview)
        self.whitelist_table.configure(xscrollcommand=self.whitelist_table_scroll.set)
        # create third frame
        # self.third_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")

        # select default frame
        self.select_frame_by_name("home")

        # call updates/initialize
        self.update_detected_table()
        self.update_whitelist_table()

        # bind treeview
        def on_select_whitelist(event):
            cur_item = self.whitelist_table.focus()
            if cur_item:
                cur_index = self.whitelist_table.item(cur_item)["values"]
                name_value = cur_index[0]
                self.whitelist_name_entry.delete(0, tk.END)
                self.whitelist_name_entry.insert(0, name_value)
                plate_number_value = cur_index[1]
                self.whitelist_plate_number_entry.delete(0, tk.END)
                self.whitelist_plate_number_entry.insert(0, plate_number_value)
        self.whitelist_table.bind("<<TreeviewSelect>>", on_select_whitelist)

    def handle_update_whitelist_entry(self):
        name_entry = self.whitelist_name_entry.get()
        plate_number_entry = self.whitelist_plate_number_entry.get()
        classification_entry = self.classficiation_combobox.get()

        if name_entry.strip() == '':
           return messagebox.showwarning(title='Warning', message='name field must not be empty')
        elif plate_number_entry.strip() == '':
           return messagebox.showwarning(title='Warning', message='plate number field must not be empty')
        
        update_whitelist_entry(name_entry.strip(), plate_number_entry.strip(), classification_entry)
        self.whitelist_name_entry.delete(0, tk.END)
        self.whitelist_plate_number_entry.delete(0, tk.END)
        self.update_whitelist_table()

    def handle_add_whitelist_entry(self):
        name_entry = self.whitelist_name_entry.get()
        plate_number_entry = self.whitelist_plate_number_entry.get()
        classification_entry =  self.classficiation_combobox.get()
      
        
        if name_entry.strip() == '':
           return messagebox.showwarning(title='Warning', message='name field must not be empty')
        elif plate_number_entry.strip() == '':
           return messagebox.showwarning(title='Warning', message='plate number field must not be empty')

        insert_whitelist(name_entry.strip(), plate_number_entry.strip(), classification_entry)
        self.whitelist_name_entry.delete(0, tk.END)
        self.whitelist_plate_number_entry.delete(0, tk.END)
        self.update_whitelist_table()

    def handle_remove_whitelist_entry(self):
        name_entry = self.whitelist_name_entry.get()
        delete_whitelist_entry(name_entry)
        self.whitelist_name_entry.delete(0, tk.END)
        self.whitelist_plate_number_entry.delete(0, tk.END)
        self.update_whitelist_table()

    def handle_remove_whitelist_entry(self):
        name_entry = self.whitelist_name_entry.get()
        delete_whitelist_entry(name_entry)
        self.whitelist_name_entry.delete(0, tk.END)
        self.whitelist_plate_number_entry.delete(0, tk.END)
        self.update_whitelist_table()

    def fixed_map(self, option):
        # Returns the style map for 'option' with any styles starting with
        # ("!disabled", "!selected", ...) filtered out

        # style.map() returns an empty list for missing options, so this should
        # be future-safe
        return [elm for elm in self.style.map("Treeview", query_opt=option)
                if elm[:2] != ("!disabled", "!selected")]
    
    def update_whitelist_table(self):
        self.whitelists = get_whitelists()
        self.whitelist_table.delete(*self.whitelist_table.get_children())
        for index, whitelist_data in enumerate(self.whitelists):
            self.whitelist_table.insert("", "end", text=index+1, values=(
                    whitelist_data["name"],
                    whitelist_data["plate_number"],
                    ))
        self.whitelist_table.update()

    def update_detected_table(self):
        self.plate_numbers = get_plate_numbers()
        self.detected_table.delete(*self.detected_table.get_children())
        
        # Sort the plate numbers based on the "time_in" field in descending order
        sorted_plate_numbers = sorted(self.plate_numbers, key=lambda x: datetime.strptime(x["time_in"], "%B, %d, %Y, %I:%M %p"), reverse=True)
        
        for index, plate_data in enumerate(sorted_plate_numbers):
            if plate_data["on_whitelist"] == "False":
                self.detected_table.insert("", "end", text=index+1, values=(
                    plate_data["name"],
                    plate_data["age"],
                    plate_data["reason"],
                    plate_data["plate_number"],
                    plate_data["time_in"],
                    plate_data["classification"],
                ), tags='unauthorized')
            else:
                self.detected_table.insert("", "end", text=index+1, values=(
                    plate_data["name"],
                    plate_data["age"],
                    plate_data["reason"],
                    plate_data["plate_number"],
                    plate_data["time_in"],
                    plate_data["classification"],
                ))

        self.detected_table.update()

    def select_frame_by_name(self, name):
        # set button color for selected button
        self.home_button.configure(fg_color=("gray75", "gray25") if name == "home" else "transparent")
        self.frame_2_button.configure(fg_color=("gray75", "gray25") if name == "frame_2" else "transparent")

        # show selected frame
        if name == "home":
            self.home_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.home_frame.grid_forget()
        if name == "frame_2":
            self.second_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.second_frame.grid_forget()


    def home_button_event(self):
        self.select_frame_by_name("home")

    def frame_2_button_event(self):
        self.select_frame_by_name("frame_2")


    def open_popup(self, detected_plate_number, detected_time_stamp, detected_image_dir, detected_on_whitelist): 
        if detected_on_whitelist == 'True':  
             insert_detected_plate_number('', '', '', detected_plate_number, detected_time_stamp, detected_image_dir, detected_on_whitelist, '')
             self.update_whitelist_table()
             self.update_detected_table()
        else:
            def handle_save_detected_plate_number():
                if text_input_name.get().strip() == '' or text_input_age.get().strip() == '' or text_input_reason.get().strip() == '':
                        error_message = "Please fill in all the required fields."
                        messagebox.showerror("Error", error_message)
                else:
                    insert_detected_plate_number(text_input_name.get(), 
                                                text_input_age.get(), 
                                                text_input_reason.get(), 
                                                text_input_plate_number.get(), 
                                                detected_time_stamp, 
                                                detected_image_dir,
                                                detected_on_whitelist,
                                                self.classficiation_combobox.get())
                    insert_whitelist(text_input_name.get(), text_input_plate_number.get(), self.classficiation_combobox.get())
                    self.update_detected_table()
                    self.update_whitelist_table()
                    popup.destroy()
            
                # Create the popup window
            popup = customtkinter.CTkToplevel()
            popup.title("Unrecognized Plate Number Detected")
            width = 400
            height = 350

            screen_width = popup.winfo_screenwidth()
            screen_height = popup.winfo_screenheight()
            x = (screen_width - width) // 2
            y = (screen_height - height) // 2

            popup.geometry(f"{width}x{height}+{x}+{y}")
            popup.resizable(False, False)

            wrapper = customtkinter.CTkFrame(popup)

            name_label = customtkinter.CTkLabel(wrapper, text="Name:")
            name_label.grid(column=0, row=0, sticky="w", padx=10)
            text_input_name = customtkinter.CTkEntry(wrapper, placeholder_text="Name", height=40)
            text_input_name.grid(column=1, row=0, sticky="ew", pady=10)

            age_label = customtkinter.CTkLabel(wrapper, text="Age:")
            age_label.grid(column=0, row=1, sticky="w", padx=10)
            text_input_age = customtkinter.CTkEntry(wrapper, placeholder_text="Age", height=40)
            text_input_age.grid(column=1, row=1, sticky="ew")

            reason_label = customtkinter.CTkLabel(wrapper, text="Reason:")
            reason_label.grid(column=0, row=2, sticky="w", padx=10)
            text_input_reason = customtkinter.CTkEntry(wrapper, placeholder_text="Reason", height=40)
            text_input_reason.grid(column=1, row=2, sticky="ew", pady=10)

            plate_number_label = customtkinter.CTkLabel(wrapper, text="Plate Number:")
            plate_number_label.grid(column=0, row=3, sticky="w", padx=10)
            text_input_plate_number = customtkinter.CTkEntry(wrapper, placeholder_text="Plate Number", height=40)
            if detected_plate_number:
                text_input_plate_number.insert(0, detected_plate_number)
            text_input_plate_number.grid(column=1, row=3, sticky="ew")


            self.classficiation_combobox = customtkinter.CTkComboBox(wrapper, values=["Visitor", "Student", "Employee"],
                                     command=self.handle_get_classification,
                                     height=40)
            self.classficiation_combobox.grid(column=1, row=4, sticky="ew", pady=10)

            cancel_button = customtkinter.CTkButton(wrapper, text="Cancel", command=popup.destroy, height=40)
            cancel_button.grid(column=0, row=5, sticky="ew", padx=5, pady=10)
            submit_button = customtkinter.CTkButton(wrapper, text="Save",
                                                    command=handle_save_detected_plate_number, 
                                                    height=40)
            submit_button.grid(column=1, row=5, sticky="ew", pady=10)

            wrapper.grid(column=0, row=0, sticky="ew", padx=10, pady=10)
            wrapper.columnconfigure(1, weight=1)
            popup.columnconfigure(0, weight=1)
            popup.grab_set()
            popup.wait_window()

    def handle_get_classification(self, choice):
        return choice
        

    def on_select_whitelist(self, event):
        cur_item = self.whitelist_tree.focus()
        if cur_item:
            cur_index = self.whitelist_tree.item(cur_item)["values"]
            name_value = cur_index[0]
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, name_value)
            whitelist_value = cur_index[1]
            self.whitelist_entry.delete(1, tk.END)
            self.whitelist_entry.insert(1, whitelist_value)
        self.whitelist_tree.bind("<<TreeviewSelect>>", self.on_select_whitelist)

    def open_image(self, event):
        item = self.captured_tree.identify('item', event.x, event.y)
        captured_image_directory = self.captured_tree.item(item, 'values')[2]
        img = Image.open(captured_image_directory)
        t = threading.Thread(target=img.show)
        t.start()
    


    # whitelist
    # def add_entry_whitelist(self):
    #     name_value = self.name_entry.get()
    #     whitelist_value = self.whitelist_entry.get()
    #     df_whitelist.loc[len(df_whitelist)] = [name_value, whitelist_value]
    #     self.whitelist_tree.insert("", "end", values=[name_value, whitelist_value])
    #     df_whitelist.to_excel("whitelist.xlsx", index=False, engine="openpyxl")
    #     self.whitelist_tree.delete(*self.whitelist_tree.get_children())
    #     self.populate_table_whitelist(df_whitelist)
        
        # self.name_entry.delete(0, "end")
        # self.whitelist_entry.delete(0, "end")

    # def delete_entry_whitelist(self):
    #     item = self.whitelist_tree.focus()
    #     if not item:
    #         return
    #     index = int(self.whitelist_tree.item(item, "text"))
    #     df_whitelist.drop(df_whitelist.index[index], inplace=True)
    #     self.whitelist_tree.delete(*self.whitelist_tree.get_children())
    #     df_whitelist.to_excel("whitelist.xlsx", index=False)
    #     self.populate_table_whitelist(df_whitelist)

    # def save_entries_whitelist(self):
    #     item = self.whitelist_tree.focus()
    #     index = int(self.whitelist_tree.item(item, "text"))
    #     if self.whitelist_entry.get():
    #         df_whitelist.at[index, 'whitelist'] = self.whitelist_entry.get()
    #         self.whitelist_tree.delete(*self.whitelist_tree.get_children())
    #         df_whitelist.to_excel("whitelist.xlsx", index=False)
    #         self.populate_table_whitelist(df_whitelist)

    # def add_captured_data(self, plate_number, time_in, captured_image_directory, is_on_whitelist):
    #     last_index = len(df_captured)
    #     df_captured.loc[last_index] = [plate_number, time_in, captured_image_directory, is_on_whitelist]
    #     df_captured.to_excel("captured.xlsx", index=False, engine="openpyxl")
    #     self.captured_tree.delete(*self.captured_tree.get_children())
    #     self.populate_table_captured(df_captured)
        
    
    def populate_table_captured(self, df):
        df['time_in'] = pd.to_datetime(df['time_in'])  # convert time_in to datetime
        for index, row in df.sort_values('time_in', ascending=False).reset_index(drop=True).iterrows():
            self.captured_tree.insert("", "end", text=index+1, values=(f'{row["plate_number"]}', f'{row["time_in"]}', f'{row["captured_image_directory"]}', f'{row["is_on_whitelist"]}'))

        # for index, row in df.iterrows():
        #     self.captured_tree.insert("", "end", text=index, values=(f'{row["plate_number"]}', f'{row["time_in"]}', f'{row["captured_image_directory"]}', f'{row["is_on_whitelist"]}'))
    
    def populate_table_whitelist(self, df):
        for index, row in df.iterrows():
            self.whitelist_tree.insert("", "end", text=index, values=(f'{row["name"]}', f'{row["whitelist"]}'))
    # main
    def show_home(self):
        self.home_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.config_frame.pack_forget()

    def show_config(self):
        self.config_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.home_frame.pack_forget()

# if __name__ == "__main__":
#     app = MainGui()
#     app.mainloop()
