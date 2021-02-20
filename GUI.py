import tkinter as tk
import tkinter.ttk as ttk
import threading
import queue
# import main_code


class RootWindow:

    def __init__(self, master):
        self.master = master
        self.create_widgets()

    class Account:
        def __init__(self, master, acc_dict):
            #tk.Frame.__init__(self, master)
            self.master = master
            self.website = acc_dict[0]
            self.nickname = acc_dict[1]
            self.password = acc_dict[2]

        def listbox_representation(self):
            return self.nickname + '(' + self.website + ')'

    def start_new_game_control_window(self):
        indices = self.acc_listbox.curselection()
        for index in indices:
            new_acc = self.accounts[index]

            acc_window = tk.Toplevel()
            acc_window.title("{}_{}".format(new_acc.website, new_acc.nickname))
            # acc_window.resizable(False, False)

            t = GameControlWindow(acc_window, new_acc)
            t.start()

    def add_acc(self):
        acc_list = [self.add_website.get(), self.add_nickname.get(), self.add_password.get()]
        new_acc_str = '     '.join(acc_list)
        with open("accounts.txt", 'a') as f:
            f.write(new_acc_str + '\n')
        self.accounts.append(self.Account(self, acc_list))
        self.acc_listbox.insert(tk.END, self.accounts[-1].listbox_representation())

    def create_widgets(self):

        # creating add_acc
        self.add_acc_group = tk.Frame(self.master)
        self.add_acc_group.pack(side=tk.LEFT)

        # labels
        self.add_website_label = tk.Label(self.add_acc_group, text="Website:")
        self.add_website_label.grid(row=0, column=0, sticky=tk.E)

        self.add_nickname_label = tk.Label(self.add_acc_group, text="Nickname:")
        self.add_nickname_label.grid(row=1, column=0, sticky=tk.E)

        self.add_password_label = tk.Label(self.add_acc_group, text="Password:")
        self.add_password_label.grid(row=2, column=0, sticky=tk.E)

        # input fields
        self.add_website = tk.Entry(self.add_acc_group)
        self.add_website.grid(row=0, column=1)

        self.add_nickname = tk.Entry(self.add_acc_group)
        self.add_nickname.grid(row=1, column=1)

        self.add_password = tk.Entry(self.add_acc_group)
        self.add_password.grid(row=2, column=1)

        # button
        self.btn_add_acc = tk.Button(self.add_acc_group, text="ADD ACCOUNT", command=self.add_acc)
        self.btn_add_acc.grid(column=1)

        # get all accounts from file
        self.accounts = []
        with open("accounts.txt") as f:
            tags = None
            while True:
                acc = f.readline().replace('\n', '').split("     ")
                if tags is None:
                    tags = acc
                elif acc == ['']:
                    break
                else:
                    self.accounts.append(self.Account(self, acc))

        self.acc_listbox_label = tk.Label(self.master, text="Accounts")
        self.acc_listbox_label.pack()

        self.acc_listbox = tk.Listbox(self.master)
        self.acc_listbox.config(width=0)
        for acc in self.accounts:
            self.acc_listbox.insert(tk.END, acc.listbox_representation())
        self.acc_listbox.pack(padx=5, pady=2)

        self.btn_start = tk.Button(self.master, text="START", command=self.start_new_game_control_window)
        #self.btn_start.place()
        self.btn_start.pack()


class GameControlWindow(threading.Thread):

    class Container:
        def __init__(self):
            pass

    class TabMain:
        def __init__(self, master):
            self.master = master

    class TabBuild:
        def __init__(self, master):
            self.master = master

    def __init__(self, master, acc):
        threading.Thread.__init__(self)
        self.master = master
        self.acc = acc
        self.acc.server = self.acc.website.split('.')[0].split("//")[-1]
        self.acc.country = self.acc.website.split('.')[-1]

        # this is for the information holding in this particular acc
        self.container = self.Container()
        self.container.website = self.acc.website
        self.container.server = self.acc.server
        self.container.country = self.acc.country
        self.container.nickname = self.acc.nickname
        self.container.password = self.acc.password
        self.container.sleep_time = 150
        self.container.timeout = 10
        self.container.stock_fill_up_time_limit = 3

        # giving log the information it will need
        import logging_make
        self.container.log = logging_make.Log(self.container).log

        # helper
        import helper
        self.container.helper = helper.Helper(self.container)

        self.container.building_names = {
            "academy": "g22",
            "bakery": "g9",
            "barracks": "g19",
            "brickyard": "g6",
            "cranny": "g23",
            "embassy": "g18",
            "grain mill": "g8",
            "granary": "g11",
            "hero's mansion": "g37",
            "iron foundry": "g7",
            "main building": "g15",
            "marketplace": "g17",
            "rally point": "g16",
            "residence": "g25",
            "sawmill": "g5",
            "smithy": "g13",
            "stable": "g20",
            "stonemason": "g34",
            "town hall": "g24",
            "wall": "g31Top",
            "warehouse": "g10",
            "workshop": "g21"
        }

        self.queue = queue.Queue()

    def create_widgets(self):
        
        class WidgetELementContainer:
            def __init__(self):
                pass

        def create_main_tab_widgets():
            self.main_tab = tk.Frame(self.notebook)
            self.notebook.add(self.main_tab, text="main")

            self.build_tab_container = WidgetELementContainer()

            self.build_tab_container.btn_start = tk.Button(self.main_tab, text="START", command=self.start_travian)
            self.build_tab_container.btn_start.pack()

        def create_build_tab_widgets():

            def refresh():
                import village_management
                self.build_tab_container.villages_names = village_management.VillageControl(self.container).get_all_villages_names()
                self.build_tab_container.villages_listboxes = []
                for village_name in self.build_tab_container.villages_names:
                    try:
                        if village_name in self.build_tab_container.villages_names_old:
                            continue
                    except:
                        pass
                    self.build_tab_container.village_build_info = tk.Frame(self.build_tab_container.all_build_info)
                    self.build_tab_container.village_build_info.pack(side=tk.LEFT)

                    self.build_tab_container.village_label = tk.Label(self.build_tab_container.village_build_info, text=village_name)
                    self.build_tab_container.village_label.pack()

                    self.build_tab_container.plan = tk.StringVar()
                    self.build_tab_container.plan.set("Casual")
                    self.build_tab_container.village_plan = tk.OptionMenu(self.build_tab_container.village_build_info, self.build_tab_container.plan, 
                        "None", "Casual", "Extended", "Offence", "Scout")
                    self.build_tab_container.village_plan.pack()

                    cases = [1, 2, 3]
                    cases_list = tk.Listbox(self.build_tab_container.village_build_info)
                    cases_list.config(width=0, height=0)
                    for case in cases:
                        cases_list.insert(tk.END, "55555555555555555555555555")
                    cases_list.pack(padx=5, pady=2)

                    self.build_tab_container.villages_listboxes.append(cases_list)
                self.build_tab_container.villages_names_old = self.build_tab_container.villages_names

            def add_case():
                pass

            def remove_case():
                for village in self.build_tab_container.villages_listboxes:
                    index = village.curselection()
                    if index:
                        # if index:
                        village.delete(index[0])
                        break

            def add_build():
                pass

            def remove_build():
                for village in self.build_tab_container.villages_listboxes:
                    index = village.curselection()
                    if index:
                        # if index:
                        village.delete(index[0])
                        break
                    


            self.build_tab = tk.Frame(self.notebook)
            self.notebook.add(self.build_tab, text="build")

            self.build_tab_container = WidgetELementContainer()

            self.build_tab_container.refresh_button = tk.Button(self.build_tab, text="REFRESH", command=refresh)
            self.build_tab_container.refresh_button.pack()

            self.build_tab_container.all_build_info = tk.Frame(self.build_tab)
            self.build_tab_container.all_build_info.pack(side=tk.TOP)

            # maybe refresh() here
            self.build_tab_listbox_buttons = tk.Frame(self.build_tab)
            self.build_tab_listbox_buttons.pack()

            # for buildings
            self.build_tab_container.building = tk.StringVar()
            self.build_tab_container.level = tk.StringVar()
            self.build_tab_container.add_build_menu_label = tk.Label(self.build_tab_listbox_buttons, text="Building")
            self.build_tab_container.add_build_menu_label.grid(row=0, column=0)
            self.build_tab_container.add_build_level_label = tk.Label(self.build_tab_listbox_buttons, text="Level")
            self.build_tab_container.add_build_level_label.grid(row=0, column=1)
            self.build_tab_container.add_build_menu = tk.OptionMenu(self.build_tab_listbox_buttons, self.build_tab_container.building, 
                        "None", "Casual", "Extended", "Offence", "Scout")
            self.build_tab_container.add_build_menu.grid(row=1, column=0)
            self.build_tab_container.add_build_level = tk.OptionMenu(self.build_tab_listbox_buttons, self.build_tab_container.level, 
                        "None", "Casual", "Extended", "Offence", "Scout")
            self.build_tab_container.add_build_level.grid(row=1, column=1)
            self.build_tab_container.add_build_button = tk.Button(self.build_tab_listbox_buttons, text="ADD BUILD", command=add_build)
            self.build_tab_container.add_build_button.grid(row=1, column=2)
            self.build_tab_container.remove_build_button = tk.Button(self.build_tab_listbox_buttons, text="REMOVE BUILD", command=remove_build)
            self.build_tab_container.remove_build_button.grid(row=1, column=3)

            # for cases
            self.build_tab_container.case = tk.StringVar()
            self.build_tab_container.add_build_menu_label = tk.Label(self.build_tab_listbox_buttons, text="Case")
            self.build_tab_container.add_build_menu_label.grid(row=0, column=4)
            self.build_tab_container.add_build_menu = tk.OptionMenu(self.build_tab_listbox_buttons, self.build_tab_container.case, 
                        "None", "Casual", "Extended", "Offence", "Scout")
            self.build_tab_container.add_build_menu.grid(row=1, column=4)
            self.build_tab_container.add_case_button = tk.Button(self.build_tab_listbox_buttons, text="ADD CASE", command=add_case)
            self.build_tab_container.add_case_button.grid(row=1, column=5)
            self.build_tab_container.remove_case_button = tk.Button(self.build_tab_listbox_buttons, text="REMOVE CASE", command=remove_case)
            self.build_tab_container.remove_case_button.grid(row=1, column=6)
        

        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack()
        create_main_tab_widgets()
        create_build_tab_widgets()

       

        

    def run(self):
        self.create_widgets()

    def start_travian(self):

        # a shitty solution, but how to make log files for separate acc?
        import main_code

        # new_thread = main_code.TravianThread(self.acc.website, self.acc.nickname, self.acc.password)
        new_thread = main_code.TravianThread(self.container)
        new_thread.start()

    def pause_button(self):
        pass  # TODO


if __name__ == "__main__":
    root = tk.Tk()
    root.title("jdT")
    root.resizable(False,False)
    RootWindow(root)
    root.mainloop()
