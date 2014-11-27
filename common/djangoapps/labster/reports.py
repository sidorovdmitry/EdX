from collections import defaultdict

from labster.models import UserAnswer, UserAttempt


def get_attempts_and_answers(lab_proxy, user):
    attempts = UserAttempt.objects.filter(lab_proxy=lab_proxy, user=user).order_by('-created_at')
    answers = UserAnswer.objects.filter(attempt__in=attempts)

    answers_by_attempt = defaultdict(list)
    for answer in answers:
        answers_by_attempt[answer.attempt_id].append(answer)

    for attempt in attempts:
        attempt.answers = answers_by_attempt[attempt.id]

    return attempts


def get_answers(user_attempt):
    answers = UserAnswer.objects.filter(attempt=user_attempt).order_by('created_at')
    return answers
