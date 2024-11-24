import pandas as pandas

data = pandas.read_csv("data/japanese_words.csv")
data["Kana"] = "..."
print(data)

for column, row in data.iterrows():
    if "[" not in row.Japanese:
        row.Kana = row.Japanese
    else:
        x = row.Japanese.index("[")
        y = row.Japanese.index("]")
        new_str = row.Japanese[x + 1 : y]
        row.Kana = new_str

        row.Japanese = row.Japanese[:x]

print(data)
data.to_csv("split_japanese_words.csv", index=False)
