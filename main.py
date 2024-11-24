"""Main script to run the 生徒 software"""

import datetime as dt
import tkinter as tk
from tkinter import messagebox, ttk

import matplotlib.pyplot as plt
import pandas as pd
import playsound
import seaborn as sns
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkextrafont import Font

from Seito import Seito

BACKGROUND_COLOR = "#B1DDC6"
USER_DATA = pd.read_csv("data/user_data.csv")
USER_DATA["Date"] = pd.to_datetime(USER_DATA["Date"], format="%Y.%m.%d")


def make_data():
    """
    Prepares the data that will be used in the software, turns it into a dataframe

    Returns
    -------
    dict
        returns a dictionary with the data that is used to make and evaluate
        the question
    """
    data_file = pd.read_csv("data/split_japanese_words.csv")
    return data_file.to_dict(orient="records")


# ------------------------------------- Functions ---------------------------------- #
seito = Seito(make_data())


# Set difficulty range based on what words you want to learn
def difficulty_set():
    """Sets up a difficulty that will then use to test you on"""
    num_words = int(difficulty_entry.get()) - 1
    num_start = int(start_diff_entry.get())
    seito.start = num_start
    seito.word_total = num_words - num_start + 1
    seito.word_count = num_words - num_start
    seito.difficulty = num_words
    seito.generate_word()

    difficulty_entry.grid_remove()
    start_diff_entry.grid_remove()
    confirm_diff_button.grid_remove()
    question_label.config(text=f"{seito.english}")
    answer_entry.grid()
    diff_label.config(
        text=f"Words remaining: {seito.word_count +1 }", bg="black", fg="grey"
    )
    diff_label.grid(column=3, columnspan=1, row=7, pady=10)


# The main function running the program
def update_question(_):
    """
    Updates the question, then checks for correct answer and based on that makes
    reaction label, after that it updates counter for remaining words as well as the
    previous word and keeps score of mistakes and correct submissions.

    Parameters
    ----------
    _ : N/A
        Optional, just there to make the function work.
    """
    seito.total_q_num += 1
    answer = answer_entry.get()
    answer_entry.delete(0, "end")

    # Check correct answer
    if answer in [seito.kanji, seito.kana]:
        seito.correct_ans += 1
        reaction_label.config(text="Correct", fg="green")
        reaction_label.grid(
            column=0,
            row=2,
            columnspan=4,
            pady=5,
        )
        play_correct()
        seito.remove_word()

    else:
        seito.incorrect_ans += 1
        reaction_label.config(text="Wrong", fg="red")
        reaction_label.grid(column=0, row=2, columnspan=4, pady=5)
        play_incorrect()

    window.after(3000, func=hide_reaction)

    # Remaining counter
    diff_label.config(
        text=f"Words remaining: {seito.word_count + 1}", bg="black", fg="grey"
    )

    # Word left panel
    previous_word.config(text=f"Previous word: {seito.english}")
    correct_answer.config(text=f"Correct answer:  {seito.kanji} [{seito.kana}]")
    input_answer.config(text=f"Input answer:  {answer}")

    # Right counting panel
    total_question.config(text=f"Total questions: {seito.total_q_num}")
    good_answers.config(text=f"Correct answers: {seito.correct_ans}")
    incorrect_answers.config(text=f"Incorrect answers: {seito.incorrect_ans}")

    # New word show up
    seito.generate_word()
    question_label.config(text=f"{seito.english}")

    # End of the learning
    if seito.win:
        diff_label.config(
            text=f"Words remaining: {seito.word_count}", bg="black", fg="grey"
        )
        answer_entry.grid_remove()
        update_data()
        question_label.config(text="Congratulations")

        reset_button.grid()
        messagebox.showinfo(
            title="Finished",
            message=f"You have learned {seito.word_total} words with {int(int(seito.word_total) / seito.total_q_num * 100)}% accuracy, \
                    \n                    Congratulations!",
        )


def play_correct():
    """Plays a success sound when answered correctly"""
    playsound.playsound("sounds/correct.wav")


def play_incorrect():
    """Plays sound for incorrect answer"""
    playsound.playsound("sounds/incorrect.wav")


def hide_reaction():
    """Removes the reaction label"""
    # reaction_label.config(text="")
    reaction_label.grid_remove()


def restart():
    """Button setup that will reset the software once the test is finisshed"""
    seito.win = False
    reset_button.grid_remove()
    diff_label.grid_remove()
    start_diff_entry.grid()
    difficulty_entry.grid()
    confirm_diff_button.grid()
    question_label.config(text="Select Difficulty")

    # Seito data reset
    seito.total_q_num = 0
    seito.correct_ans = 0
    seito.incorrect_ans = 0
    seito.difficulty = 10
    seito.data = make_data()

    # Right counting panel
    total_question.config(text=f"Total questions: {seito.total_q_num}")
    good_answers.config(text=f"Correct answers: {seito.correct_ans}")
    incorrect_answers.config(text=f"Incorrect answers: {seito.incorrect_ans}")


# ------------------------------------- Data GUI ------------------------------------ #
def open_second_window():
    """
    Opens second window containing the data and graph with progress
    """

    second_window = tk.Toplevel(window)
    second_window.title("Second Window")
    second_window.geometry("1100x850")
    second_window.resizable(False, False)
    second_window.title("User_Data")
    second_window.config(pady=15, padx=20, bg="black", highlightthickness=20)
    table = ttk.Treeview(second_window, columns=list(USER_DATA.columns))
    table["show"] = "headings"

    for col in table["columns"]:
        table.heading(col, text=col)

    for i, row in USER_DATA.iterrows():
        table.insert("", "end", values=row.tolist())

    table.grid(
        column=0,
        row=7,
        columnspan=6,
        rowspan=5,
        pady=10,
        padx=5,
        sticky="NSEW",
    )

    # sns.set(color_codes=True)
    # sns.set_palette("Blues")
    sns.set()
    g = sns.relplot(
        data=USER_DATA,
        x="Date",
        y="Difficulty",
        hue="Success %",
        kind="scatter",
        size="Success %",
        palette="Oranges",
    )
    g.figure.autofmt_xdate()
    canvas = FigureCanvasTkAgg(plt.gcf(), master=second_window)
    canvas.draw()
    canvas.get_tk_widget().grid(
        row=0, column=0, columnspan=5, rowspan=6, pady=10, padx=5
    )


def update_data():
    """
    Updates the progress user data after a successful finish of given difficulty
    """
    global USER_DATA
    new_data = {
        "Date": dt.date.today(),
        "Difficulty": difficulty_entry.get(),
        "Success %": int(int(seito.word_total) / seito.total_q_num * 100),
        "Mistakes": int(seito.incorrect_ans),
        "Total words": int(seito.word_total),
    }
    print("xd")
    new_df = pd.DataFrame(new_data, index=[0])
    user_data = pd.concat([USER_DATA, new_df])
    user_data.to_csv("data/user_data.csv", index=False)
    USER_DATA = pd.read_csv("data/user_data.csv")
    USER_DATA["Date"] = pd.to_datetime(USER_DATA["Date"], format="%Y.%m.%d")


# --------------------------------------- GUI --------------------------------------- #
# Window
window = tk.Tk()
window.resizable(False, False)
window.title("生徒")
window.config(
    pady=15, padx=50, bg="black", highlightthickness=20, highlightcolor="grey"
)
window.bind("<Return>", func=update_question)

font_notosans = Font(file="data/NotoSansCJKjp-Regular.ttf")
font_gen = Font(file="data/Gen Jyuu Gothic Monospace Regular.ttf")

# Canvas
black_canvas = tk.Canvas(width=600, height=150, highlightthickness=2, bg="black")
black_canvas.grid(column=0, row=4, columnspan=4, rowspan=3, pady=0)

# Labels
description_label = tk.Label(
    text="Write word in Japanese:",
    font=("mincho", 15),
    fg="yellow",
    bg="black",
)
description_label.grid(column=0, row=0, columnspan=4, pady=20)
question_label = tk.Label(
    text="Select Difficulty",
    font=("mincho", 30, "bold"),
    fg="white",
    bg="black",
)
question_label.grid(column=0, row=1, columnspan=4, pady=20)
reaction_label = tk.Label(text="", font=("mincho", 20, "bold"), bg="black")
reaction_label.grid(column=0, row=2, columnspan=4, pady=5)

previous_word = tk.Label(
    text="Previous word:  -  ",
    fg="white",
    bg="black",
    font=(font_notosans, 11),
)
previous_word.grid(column=0, row=4, pady=0)
correct_answer = tk.Label(
    text="Correct answer:  -  ",
    fg="white",
    bg="black",
    font=(font_notosans, 11),
)
correct_answer.grid(column=0, row=5, pady=0)
input_answer = tk.Label(
    text="Input answer:  -  ",
    fg="white",
    bg="black",
    font=(font_notosans, 11),
)
input_answer.grid(column=0, row=6, pady=0)

total_question = tk.Label(text="Total questions:  -  ", fg="yellow", bg="black")
total_question.grid(column=3, row=4, pady=0)
good_answers = tk.Label(text="Good answers:  -  ", fg="green", bg="black")
good_answers.grid(column=3, row=5, pady=0)
incorrect_answers = tk.Label(text="Bad answers:  -  ", fg="red", bg="black")
incorrect_answers.grid(column=3, row=6, pady=0)
diff_label = tk.Label(
    text=f"Words {seito.difficulty} remaining", width=20, bg="black", fg="grey"
)

# Entry
answer_entry = tk.Entry(width=30, font=(font_notosans, 25))
answer_entry.grid(column=0, row=3, columnspan=4, pady=70)
answer_entry.grid_remove()
difficulty_entry = tk.Entry(width=10, font=(font_notosans, 12), bg="grey")
difficulty_entry.insert(0, string="... Up to diff")
difficulty_entry.grid(column=1, row=7, columnspan=1, pady=10, padx=10)
start_diff_entry = tk.Entry(width=10, font=(font_notosans, 12), bg="grey")
start_diff_entry.insert(0, string="Start from ...")
start_diff_entry.grid(column=0, row=7, columnspan=1, pady=10, padx=10)

# Button
confirm_diff_button = tk.Button(
    width=20, text="Confirm difficulty", bg="grey", command=difficulty_set
)
confirm_diff_button.grid(column=3, columnspan=2, row=7, pady=10)
reset_button = tk.Button(width=20, text="Reset", bg="grey", command=restart)
reset_button.grid(column=0, row=7, columnspan=1, pady=10)
reset_button.grid_remove()
data_button = tk.Button(width=10, text="Data", bg="grey", command=open_second_window)
data_button.grid(column=3, row=8)

# ------------------------------------- Testing ------------------------------------- #
# test_button = tk.Button(text="Test", command=update_question)
# test_button.grid(column=2, row=8)


window.mainloop()
