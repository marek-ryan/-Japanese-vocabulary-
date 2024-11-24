import pandas as pd
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns

data = {
    "Date": [],
    "Difficulty": [],
    "Success %": []

}
df = pd.read_csv("data/user_data.csv")
print(df)

sns.set_style("darkgrid")
sns.relplot(data=df, x="Date", y="Difficulty",
            hue="Success %", palette="dark:salmon",
            kind="scatter", size="Success %")

# Create a Tkinter window
root = tk.Tk()
root.title("Seaborn Plot")
second_window = tk.Toplevel(root)
second_window.title("test")

# Create a FigureCanvasTkAgg object
canvas = FigureCanvasTkAgg(plt.gcf(), master=second_window)
canvas.draw()

# Add the plot to the Tkinter window
canvas.get_tk_widget().pack()

root.mainloop()
