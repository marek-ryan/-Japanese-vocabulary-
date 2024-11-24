import random


# ------------------------------------- Data import ------------------------------ #
class Seito:
    def __init__(self, data):
        self.r_num = 1
        self.total_q_num = 0
        self.correct_ans = 0
        self.incorrect_ans = 0
        self.english = ""
        self.kanji = ""
        self.kana = ""
        self.data = data
        self.start = 0
        self.difficulty = 10
        self.word_total = 0
        self.word_count = 0
        self.generate_word()
        self.win = False

    def check_answer(self, event):
        pass

    def generate_word(self):
        self.r_num = random.randint(self.start, self.difficulty)
        self.english = self.data[self.r_num]["English"]
        self.kanji = self.data[self.r_num]["Japanese"]
        self.kana = self.data[self.r_num]["Kana"]

    def remove_word(self):
        if self.word_count > 0:
            self.word_count -= 1
            self.difficulty -= 1
            self.data.pop(self.r_num)
        else:
            self.win = True
