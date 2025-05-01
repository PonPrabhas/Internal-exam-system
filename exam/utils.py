from difflib import SequenceMatcher

def evaluate_subjective_answer(student_answer, expected_answer, max_marks=10):
    student_answer = student_answer.strip().lower()
    expected_answer = expected_answer.strip().lower()
    similarity = SequenceMatcher(None, student_answer, expected_answer).ratio()
    obtained_marks = similarity * max_marks
    return round(obtained_marks, 2)
