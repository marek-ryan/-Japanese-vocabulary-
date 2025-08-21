#!/usr/bin/env python3
"""Alternative GUI implementation using tkinter for compatibility testing"""

import datetime as dt
import os
import sys
import threading
import platform

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import pygame

# Try to import Seito module
try:
    from Seito import Seito
except ImportError:
    print(
        "Error: Seito module not found. Please ensure Seito.py is in the same directory."
    )
    sys.exit(1)

# --- GUI Backend Selection with OS Detection ---
GUI_BACKEND = None

# If on Linux, prioritize GTK. Otherwise, prioritize tkinter.
if platform.system() == "Linux":
    print("Linux detected, prioritizing GTK backend.")
    try:
        import gi

        gi.require_version("Gtk", "3.0")
        GUI_BACKEND = "gtk"
        print("Using GTK backend")
    except ImportError:
        try:
            import tkinter

            GUI_BACKEND = "tkinter"
            print("GTK not found, falling back to tkinter backend.")
        except ImportError:
            print("Error: Neither GTK nor tkinter is available.")
            sys.exit(1)
else:
    print(f"{platform.system()} detected, prioritizing tkinter backend.")
    try:
        import tkinter

        GUI_BACKEND = "tkinter"
        print("Using tkinter backend")
    except ImportError:
        try:
            import gi

            gi.require_version("Gtk", "3.0")
            GUI_BACKEND = "gtk"
            print("tkinter not found, falling back to GTK backend.")
        except ImportError:
            print("Error: Neither tkinter nor GTK is available.")
            sys.exit(1)

# --- Import GUI components based on selected backend ---
if GUI_BACKEND == "tkinter":
    import tkinter as tk
    from tkinter import messagebox, ttk
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
elif GUI_BACKEND == "gtk":
    import gi

    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk, Gdk, GLib, Pango
    from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas

# --- Constants and Data Loading ---
DATE_FORMAT = "%Y/%m/%d %H:%M"
try:
    USER_DATA = pd.read_csv("data/user_data.csv")
    # Convert the 'Date' column to datetime objects for plotting
    USER_DATA["Date"] = pd.to_datetime(
        USER_DATA["Date"], format=DATE_FORMAT, errors="coerce"
    )
    USER_DATA.dropna(subset=["Date"], inplace=True)
except FileNotFoundError:
    print("Warning: user_data.csv not found. Creating empty dataframe.")
    USER_DATA = pd.DataFrame(
        columns=["Date", "Difficulty", "Success %", "Mistakes", "Total words"]
    )


def make_data():
    try:
        data_file = pd.read_csv("data/split_japanese_words.csv")
        return data_file.to_dict(orient="records")
    except FileNotFoundError:
        print("Error: split_japanese_words.csv not found.")
        return []


class SeitoApp:
    def __init__(self):
        self.seito = Seito(make_data())
        pygame.mixer.init()
        if GUI_BACKEND == "tkinter":
            self.setup_tkinter()
        elif GUI_BACKEND == "gtk":
            self.setup_gtk()

    # --- Tkinter Implementation ---
    def setup_tkinter(self):
        self.window = tk.Tk()
        self.window.resizable(False, False)
        self.window.title("生徒")
        self.window.config(pady=15, padx=50, bg="black")
        self.window.bind("<Return>", self.update_question)
        # Labels
        self.description_label = tk.Label(
            text="Write word in Japanese:", font=("Arial", 15), fg="#DAA520", bg="black"
        )
        self.description_label.grid(column=0, row=0, columnspan=4, pady=20)
        self.question_label = tk.Label(
            text="Select Difficulty", font=("Arial", 30, "bold"), fg="white", bg="black"
        )
        self.question_label.grid(column=0, row=1, columnspan=4, pady=20)
        self.reaction_label_container = tk.Frame(self.window, height=40, bg="black")
        self.reaction_label_container.grid(column=0, row=2, columnspan=4, pady=5)
        self.reaction_label_container.grid_propagate(False)
        self.reaction_label = tk.Label(
            self.reaction_label_container,
            text="",
            font=("Arial", 20, "bold"),
            bg="black",
        )
        self.reaction_label.pack()

        self.previous_word = tk.Label(
            text="Previous word:  -  ", fg="white", bg="black", font=("Arial", 11)
        )
        self.previous_word.grid(column=0, row=4, pady=0, sticky="w")
        self.correct_answer = tk.Label(
            text="Correct answer:  -  ", fg="white", bg="black", font=("Arial", 11)
        )
        self.correct_answer.grid(column=0, row=5, pady=0, sticky="w")
        self.input_answer = tk.Label(
            text="Input answer:  -  ", fg="white", bg="black", font=("Arial", 11)
        )
        self.input_answer.grid(column=0, row=6, pady=0, sticky="w")
        self.total_question = tk.Label(
            text="Total questions:  -  ", fg="yellow", bg="black"
        )
        self.total_question.grid(column=3, row=4, pady=0, sticky="w")
        self.good_answers = tk.Label(text="Good answers:  -  ", fg="green", bg="black")
        self.good_answers.grid(column=3, row=5, pady=0, sticky="w")
        self.incorrect_answers = tk.Label(
            text="Bad answers:  -  ", fg="red", bg="black"
        )
        self.incorrect_answers.grid(column=3, row=6, pady=0, sticky="w")
        self.diff_label = tk.Label(
            text=f"Words {self.seito.difficulty} remaining",
            width=20,
            bg="black",
            fg="grey",
        )
        self.diff_label.grid(column=3, row=7, pady=10, sticky="w")
        self.diff_label.grid_remove()

        # Entry
        self.answer_entry = tk.Entry(width=30, font=("Arial", 25))
        self.answer_entry.grid(column=0, row=3, columnspan=4, pady=70)
        self.difficulty_entry = tk.Entry(width=10, font=("Arial", 12), bg="grey")
        self.difficulty_entry.insert(0, string="10")
        self.difficulty_entry.grid(column=1, row=8, columnspan=1, pady=10, padx=10)
        self.start_diff_entry = tk.Entry(width=10, font=("Arial", 12), bg="grey")
        self.start_diff_entry.insert(0, string="1")
        self.start_diff_entry.grid(column=0, row=8, columnspan=1, pady=10, padx=10)

        # Buttons
        self.confirm_diff_button = tk.Button(
            width=20, text="Confirm difficulty", bg="grey", command=self.difficulty_set
        )
        self.confirm_diff_button.grid(column=3, columnspan=2, row=8, pady=10)
        self.reset_button = tk.Button(
            width=20, text="Reset", bg="grey", command=self.restart
        )
        self.reset_button.grid(column=0, row=9, columnspan=1, pady=10)
        self.data_button = tk.Button(
            width=10, text="Data", bg="grey", command=self.open_second_window
        )
        self.data_button.grid(column=3, row=9)

        # Initial state
        self.answer_entry.grid_remove()
        self.reset_button.grid_remove()
        self.reaction_label.pack_forget()

    # --- GTK Implementation ---
    def setup_gtk(self):
        self.window = Gtk.Window(title="生徒")
        self.window.connect("destroy", Gtk.main_quit)
        self.window.set_resizable(False)
        self.window.set_default_size(800, 650)

        css_provider = Gtk.CssProvider()
        css = """
        window { background-color: black; }
        #yellow { color: yellow; }
        #grey { color: grey; }
        #white { color: white; }
        #question { font-size: 30px; font-weight: bold; }
        #description { font-size: 15px; color: #DAA520; }
        #good-answers-label { color: #00FF00; }
        #bad-answers-label { color: #FF0000; }
        #reaction { font-size: 20px; font-weight: bold; }
        #reaction.green { color: #00FF00; }
        #reaction.red { color: #FF0000; }
        
        entry { font-size: 25px; padding: 5px; }
        
        .compact-widget {
            font-size: 14px;
            padding: 5px;
            min-height: 0;
        }
        """
        css_provider.load_from_data(css.encode())
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

        self.grid = Gtk.Grid(column_spacing=10, row_spacing=15)
        self.grid.set_halign(Gtk.Align.CENTER)
        self.grid.set_valign(Gtk.Align.CENTER)
        self.window.add(self.grid)

        def create_styled_label(text, name):
            label = Gtk.Label(label=text)
            label.set_name(name)
            label.set_halign(Gtk.Align.START)
            return label

        self.description_label = create_styled_label(
            "Write word in Japanese:", "description"
        )
        self.description_label.set_halign(Gtk.Align.CENTER)
        self.grid.attach(self.description_label, 0, 0, 4, 1)

        self.question_label = create_styled_label("Select Difficulty", "question")
        self.question_label.set_halign(Gtk.Align.CENTER)
        self.grid.attach(self.question_label, 0, 1, 4, 1)

        self.reaction_label_container = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=0
        )
        self.reaction_label_container.set_size_request(-1, 40)
        self.grid.attach(self.reaction_label_container, 0, 2, 4, 1)

        self.reaction_label = create_styled_label("", "reaction")
        self.reaction_label.set_halign(Gtk.Align.CENTER)
        self.reaction_label.set_valign(Gtk.Align.CENTER)
        self.reaction_label_container.pack_start(self.reaction_label, True, True, 0)
        self.reaction_label.set_visible(False)

        info_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=80)
        info_box.set_halign(Gtk.Align.CENTER)
        self.grid.attach(info_box, 0, 4, 4, 3)

        left_column = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        info_box.pack_start(left_column, False, False, 0)

        self.previous_word = create_styled_label("Previous word:  -  ", "white")
        left_column.pack_start(self.previous_word, False, False, 0)
        self.correct_answer = create_styled_label("Correct answer:  -  ", "white")
        left_column.pack_start(self.correct_answer, False, False, 0)
        self.input_answer = create_styled_label("Input answer:  -  ", "white")
        left_column.pack_start(self.input_answer, False, False, 0)

        self.right_column = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        info_box.pack_start(self.right_column, False, False, 0)

        self.total_question = create_styled_label("Total questions:  -  ", "yellow")
        self.right_column.pack_start(self.total_question, False, False, 0)
        self.good_answers = create_styled_label(
            "Good answers:  -  ", "good-answers-label"
        )
        self.right_column.pack_start(self.good_answers, False, False, 0)
        self.incorrect_answers = create_styled_label(
            "Bad answers:  -  ", "bad-answers-label"
        )
        self.right_column.pack_start(self.incorrect_answers, False, False, 0)

        self.diff_label = create_styled_label(
            f"Words {self.seito.difficulty} remaining", "grey"
        )

        self.answer_entry = Gtk.Entry(width_chars=25)
        self.answer_entry.set_halign(Gtk.Align.CENTER)
        self.answer_entry.connect("activate", self.update_question)

        self.reset_button = Gtk.Button(label="Reset")
        self.reset_button.get_style_context().add_class("compact-widget")
        self.reset_button.connect("clicked", self.restart)

        self.difficulty_entry = Gtk.Entry()
        self.difficulty_entry.set_text("2")
        self.difficulty_entry.get_style_context().add_class("compact-widget")

        self.start_diff_entry = Gtk.Entry()
        self.start_diff_entry.set_text("1")
        self.start_diff_entry.get_style_context().add_class("compact-widget")

        self.confirm_diff_button = Gtk.Button(label="Confirm difficulty")
        self.confirm_diff_button.get_style_context().add_class("compact-widget")
        self.confirm_diff_button.connect("clicked", self.difficulty_set)

        self.grid.attach(self.start_diff_entry, 1, 8, 1, 1)
        self.grid.attach(self.difficulty_entry, 2, 8, 1, 1)
        self.grid.attach(self.confirm_diff_button, 3, 8, 1, 1)

        self.data_button = Gtk.Button(label="Data")
        self.data_button.get_style_context().add_class("compact-widget")
        self.data_button.connect("clicked", self.open_second_window)
        self.grid.attach(self.data_button, 3, 9, 1, 1)

    # --- Shared Logic ---
    def difficulty_set(self, widget=None):
        try:
            if GUI_BACKEND == "tkinter":
                num_words = int(self.difficulty_entry.get()) - 1
                num_start = int(self.start_diff_entry.get())
            else:  # GTK
                num_words = int(self.difficulty_entry.get_text()) - 1
                num_start = int(self.start_diff_entry.get_text())
        except ValueError:
            self.show_error(
                "Error", "Please enter valid numbers for difficulty settings."
            )
            return

        self.seito.start = num_start
        self.seito.word_total = num_words - num_start + 1
        self.seito.word_count = num_words - num_start
        self.seito.difficulty = num_words
        self.seito.generate_word()

        if GUI_BACKEND == "tkinter":
            self.difficulty_entry.grid_remove()
            self.start_diff_entry.grid_remove()
            self.confirm_diff_button.grid_remove()
            self.question_label.config(text=f"{self.seito.english}")
            self.answer_entry.grid()
            self.answer_entry.focus()
            self.diff_label.config(text=f"Words remaining: {self.seito.word_count + 1}")
            self.diff_label.grid()
        else:  # GTK
            self.grid.remove(self.difficulty_entry)
            self.grid.remove(self.start_diff_entry)
            self.grid.remove(self.confirm_diff_button)

            self.question_label.set_text(f"{self.seito.english}")
            self.grid.attach(self.answer_entry, 0, 3, 4, 1)
            self.answer_entry.show()
            self.answer_entry.grab_focus()

            self.right_column.pack_start(self.diff_label, False, False, 0)
            self.diff_label.set_text(f"Words remaining: {self.seito.word_count + 1}")
            self.diff_label.show()

    def update_question(self, widget=None):
        if GUI_BACKEND == "tkinter" and not self.answer_entry.winfo_viewable():
            return
        if GUI_BACKEND == "gtk" and not self.answer_entry.get_visible():
            return

        self.seito.total_q_num += 1
        answer = (
            self.answer_entry.get()
            if GUI_BACKEND == "tkinter"
            else self.answer_entry.get_text()
        )
        if GUI_BACKEND == "tkinter":
            self.answer_entry.delete(0, "end")
        else:
            self.answer_entry.set_text("")

        if answer in [self.seito.kanji, self.seito.kana]:
            self.seito.correct_ans += 1
            self.show_reaction("Correct", "green")
            self.play_correct()
            self.seito.remove_word()
        else:
            self.seito.incorrect_ans += 1
            self.show_reaction("Wrong", "red")
            self.play_incorrect()

        if GUI_BACKEND == "tkinter":
            self.window.after(1500, self.hide_reaction)
        else:
            GLib.timeout_add(1500, self.hide_reaction)

        self.update_ui_text(answer)

        self.seito.generate_word()
        if self.seito.english:
            if GUI_BACKEND == "tkinter":
                self.question_label.config(text=f"{self.seito.english}")
            else:
                self.question_label.set_text(f"{self.seito.english}")

        if self.seito.win:
            self.end_session()

    def update_ui_text(self, answer):
        diff_text = f"Words remaining: {self.seito.word_count + 1}"
        prev_word_text = f"Previous word: {self.seito.english}"
        correct_ans_text = f"Correct answer:  {self.seito.kanji} [{self.seito.kana}]"
        input_ans_text = f"Input answer:  {answer}"
        total_q_text = f"Total questions: {self.seito.total_q_num}"
        good_ans_text = f"Good answers: {self.seito.correct_ans}"
        bad_ans_text = f"Incorrect answers: {self.seito.incorrect_ans}"

        if GUI_BACKEND == "tkinter":
            self.diff_label.config(text=diff_text)
            self.previous_word.config(text=prev_word_text)
            self.correct_answer.config(text=correct_ans_text)
            self.input_answer.config(text=input_ans_text)
            self.total_question.config(text=total_q_text)
            self.good_answers.config(text=good_ans_text)
            self.incorrect_answers.config(text=bad_ans_text)
        else:  # GTK
            self.diff_label.set_text(diff_text)
            self.previous_word.set_text(prev_word_text)
            self.correct_answer.set_text(correct_ans_text)
            self.input_answer.set_text(input_ans_text)
            self.total_question.set_text(total_q_text)
            self.good_answers.set_text(good_ans_text)
            self.incorrect_answers.set_text(bad_ans_text)

    def end_session(self):
        if GUI_BACKEND == "tkinter":
            self.diff_label.config(text=f"Words remaining: {self.seito.word_count}")
            self.answer_entry.grid_remove()
            self.question_label.config(text="Congratulations")
            self.reset_button.grid()
        else:  # GTK
            self.diff_label.set_text(f"Words remaining: {self.seito.word_count}")
            self.grid.remove(self.answer_entry)
            self.question_label.set_text("Congratulations")
            self.grid.attach(self.reset_button, 0, 9, 1, 1)
            self.reset_button.show()

        self.update_data()
        accuracy = int(int(self.seito.word_total) / self.seito.total_q_num * 100)
        self.show_info(
            "Finished",
            f"You have learned {self.seito.word_total} words with {accuracy}% accuracy.\nCongratulations!",
        )

    def show_reaction(self, text, color):
        if GUI_BACKEND == "tkinter":
            self.reaction_label.config(text=text, fg=color)
            self.reaction_label.pack()
        else:  # GTK
            context = self.reaction_label.get_style_context()
            context.remove_class("green")
            context.remove_class("red")
            context.add_class(color)

            self.reaction_label.set_text(text)
            self.reaction_label.set_visible(True)

    def hide_reaction(self):
        if GUI_BACKEND == "tkinter":
            self.reaction_label.pack_forget()
        else:
            self.reaction_label.set_visible(False)
        return False

    def restart(self, widget=None):
        self.seito.win = False
        self.seito.total_q_num = 0
        self.seito.correct_ans = 0
        self.seito.incorrect_ans = 0
        self.seito.difficulty = 10
        self.seito.data = make_data()
        self.update_ui_text("")

        if GUI_BACKEND == "tkinter":
            self.reset_button.grid_remove()
            self.diff_label.grid_remove()
            self.start_diff_entry.grid()
            self.difficulty_entry.grid()
            self.confirm_diff_button.grid()
            self.question_label.config(text="Select Difficulty")
            self.previous_word.config(text="Previous word:  -  ")
            self.correct_answer.config(text="Correct answer:  -  ")
            self.input_answer.config(text="Input answer:  -  ")
        else:  # GTK
            self.grid.remove(self.reset_button)
            if self.diff_label.get_parent():
                self.diff_label.get_parent().remove(self.diff_label)

            self.grid.attach(self.start_diff_entry, 1, 8, 1, 1)
            self.grid.attach(self.difficulty_entry, 2, 8, 1, 1)
            self.grid.attach(self.confirm_diff_button, 3, 8, 1, 1)
            self.start_diff_entry.show()
            self.difficulty_entry.show()
            self.confirm_diff_button.show()

            self.question_label.set_text("Select Difficulty")
            self.previous_word.set_text("Previous word:  -  ")
            self.correct_answer.set_text("Correct answer:  -  ")
            self.input_answer.set_text("Input answer:  -  ")
            self.total_question.set_text("Total questions:  -  ")
            self.good_answers.set_text("Good answers:  -  ")
            self.incorrect_answers.set_text("Incorrect answers:  -  ")

    #
    def open_second_window(self, widget=None):
        if GUI_BACKEND == "tkinter":
            win = tk.Toplevel(self.window)
            win.title("User Data")
            win.geometry("1100x850")
            win.resizable(False, False)
            container = win
        else:  # GTK
            win = Gtk.Window(title="User Data")
            win.set_default_size(1100, 850)
            win.set_resizable(False)
            vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, margin=10)
            win.add(vbox)
            container = vbox

        if not USER_DATA.empty:
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.set()
            # The 'Date' column in USER_DATA is already a datetime object here
            scatter = ax.scatter(
                USER_DATA["Date"],
                USER_DATA["Difficulty"],
                c=USER_DATA["Success %"],
                s=USER_DATA["Success %"] * 2,
                cmap="Oranges",
                alpha=0.7,
            )

            # Set color
            ax.set_facecolor("#9C9C9C")
            fig.patch.set_facecolor("#7F7F7F")
            ax.grid(True, color="black", alpha=0.2)
            ax.set_xlabel("Date", color="black", fontweight="bold")
            ax.set_ylabel("Difficulty", color="black", fontweight="bold")
            ax.set_title("Learning Progress", color="black", fontweight="bold")

            # Set x-axis major formatter to show only date (yyyy-mm-dd)
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
            fig.autofmt_xdate()
            cbar = plt.colorbar(scatter)
            cbar.set_label("Success %")

            if GUI_BACKEND == "tkinter":
                canvas = FigureCanvasTkAgg(fig, master=container)
                canvas.draw()
                canvas.get_tk_widget().grid(row=0, column=0, pady=10, padx=5)
                table = ttk.Treeview(
                    container, columns=list(USER_DATA.columns), show="headings"
                )
                for col in table["columns"]:
                    table.heading(col, text=col)
                for _, row in USER_DATA.iterrows():
                    row_values = row.to_dict()
                    # Format the datetime object back to a string for display
                    row_values["Date"] = row_values["Date"].strftime(DATE_FORMAT)
                    table.insert("", "end", values=list(row_values.values()))
                table.grid(row=1, column=0, pady=10, padx=5, sticky="NSEW")
            else:  # GTK
                canvas = FigureCanvas(fig)
                canvas.set_size_request(1000, 600)
                container.pack_start(canvas, True, True, 0)

                scrolled_window = Gtk.ScrolledWindow()
                scrolled_window.set_hexpand(True)
                scrolled_window.set_vexpand(True)
                container.pack_start(scrolled_window, True, True, 0)

                # Create a new dataframe for display with formatted date strings
                display_df = USER_DATA.copy()
                display_df["Date"] = display_df["Date"].dt.strftime(DATE_FORMAT)

                liststore = Gtk.ListStore(*([str] * len(display_df.columns)))
                for _, row in display_df.iterrows():
                    # *** THE FIX IS HERE: Convert all items in the row to strings ***
                    liststore.append([str(item) for item in row])

                treeview = Gtk.TreeView(model=liststore)
                scrolled_window.add(treeview)

                for i, col_name in enumerate(display_df.columns):
                    renderer = Gtk.CellRendererText()
                    column = Gtk.TreeViewColumn(col_name, renderer, text=i)
                    treeview.append_column(column)

                win.show_all()
        else:
            if GUI_BACKEND == "tkinter":
                tk.Label(container, text="No data available yet.").grid(
                    row=0, column=0, pady=50
                )
            else:  # GTK
                no_data_label = Gtk.Label(
                    label="No data available yet. Complete a session to see progress."
                )
                container.pack_start(no_data_label, True, True, 0)
                win.show_all()

    def update_data(self):
        global USER_DATA
        new_data = {
            "Date": dt.datetime.now(),  # Keep as datetime object for now
            "Difficulty": (
                self.difficulty_entry.get()
                if GUI_BACKEND == "tkinter"
                else self.difficulty_entry.get_text()
            ),
            "Success %": int(int(self.seito.word_total) / self.seito.total_q_num * 100),
            "Mistakes": int(self.seito.incorrect_ans),
            "Total words": int(self.seito.word_total),
        }

        new_df = pd.DataFrame(new_data, index=[0])

        # Add new data to the global dataframe
        USER_DATA = pd.concat([USER_DATA, new_df], ignore_index=True)

        # Create a copy for saving with formatted date strings
        save_df = USER_DATA.copy()
        save_df["Date"] = save_df["Date"].dt.strftime(DATE_FORMAT)

        os.makedirs("data", exist_ok=True)
        save_df.to_csv("data/user_data.csv", index=False)

    def show_error(self, title, message):
        if GUI_BACKEND == "tkinter":
            messagebox.showerror(title, message)
        else:  # GTK
            dialog = Gtk.MessageDialog(
                transient_for=self.window,
                flags=0,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.CANCEL,
                text=title,
            )
            dialog.format_secondary_text(message)
            dialog.run()
            dialog.destroy()

    def show_info(self, title, message):
        if GUI_BACKEND == "tkinter":
            messagebox.showinfo(title, message)
        else:  # GTK
            dialog = Gtk.MessageDialog(
                transient_for=self.window,
                flags=0,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text=title,
            )
            dialog.format_secondary_text(message)
            dialog.run()
            dialog.destroy()

    def play_correct(self):
        sound_path = "sounds/correct.mp3"
        if os.path.exists(sound_path):
            try:
                pygame.mixer.Sound(sound_path).play()
            except pygame.error as e:
                print(f"Error playing sound {sound_path}: {e}")

    def play_incorrect(self):
        sound_path = "sounds/incorrect.mp3"
        if os.path.exists(sound_path):
            try:
                pygame.mixer.Sound(sound_path).play()
            except pygame.error as e:
                print(f"Error playing sound {sound_path}: {e}")

    def run(self):
        if GUI_BACKEND == "tkinter":
            self.window.mainloop()
        elif GUI_BACKEND == "gtk":
            self.window.show_all()
            Gtk.main()


if __name__ == "__main__":
    app = SeitoApp()
    app.run()
