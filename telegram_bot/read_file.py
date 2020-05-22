with open('phrases.txt', 'r') as file:
    fdata = file.read()
    file.close()

with open('answers_with_questions.txt', 'r') as file:
    ans_for_q = file.read()
    file.close()

with open('phrases_answers.txt', 'r') as file:
    phr_answ = file.read()
    file.close()