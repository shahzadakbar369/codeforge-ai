def calculate_average(scores):
    if len(scores) == 0:
        return 0
    return round(sum(scores) / len(scores), 2)


def letter_grade(score):
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "F"


def grade_points(letter):
    if letter == "A":
        return 4.0
    if letter == "B":
        return 3.0
    if letter == "C":
        return 2.0
    if letter == "D":
        return 1.0
    return 0.0


def gpa(scores):
    if len(scores) == 0:
        return 0.0
    total = 0
    for s in scores:
        total += grade_points(letter_grade(s))
    return round(total / len(scores), 2)


def weighted_grade(scores, weights):
    if len(scores) != len(weights):
        raise ValueError("Scores and weights differ in length")
    total_weight = sum(weights)
    if total_weight == 0:
        raise ValueError("Total weight is zero")
    weighted_sum = 0
    for s, w in zip(scores, weights):
        weighted_sum += s * w
    return round(weighted_sum / total_weight, 2)


def count_passing(scores, pass_mark):
    count = 0
    for s in scores:
        if s >= pass_mark:
            count += 1
    return count


def grade_distribution(scores):
    distribution = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
    for s in scores:
        distribution[letter_grade(s)] += 1
    return distribution


def highest_score(scores):
    if len(scores) == 0:
        return None
    return max(scores)


def rank_scores(scores):
    return sorted(scores, reverse=True)


def curve_scores(scores, bonus):
    return [min(100, s + bonus) for s in scores]


def is_honor_roll(scores):
    if not scores:
        return False
    avg = calculate_average(scores)
    if avg < 90:
        return False
    if min(scores) < 80:
        return False
    return True
