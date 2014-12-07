from collections import defaultdict

from labster.models import UserAnswer, UserAttempt, Problem


def get_attempts_and_answers(lab_proxy, user, latest_only=False):

    # attempts = UserAttempt.objects.filter(lab_proxy=lab_proxy)\
    attempts = UserAttempt.objects.filter(lab_proxy=lab_proxy, user=user)\
        .exclude(useranswer=None).order_by('-created_at')

    if latest_only:
        attempts = list(attempts)[:1]

    answers = UserAnswer.objects.filter(attempt__in=attempts).order_by('problem__order')

    # special case for LAB_ID 35 (adaptive cytogenetics)
    if lab_proxy.lab_id == 35:
        quiz_ids = ["Cyto-{}-Post".format(i) for i in range(11, 41)]
        problems = Problem.objects.filter(is_active=True, element_id__in=quiz_ids)
        answers = answers.filter(problem__in=problems)

    answers_by_attempt = defaultdict(list)
    for answer in answers:
        answers_by_attempt[answer.attempt_id].append(answer)

    for attempt in attempts:
        attempt.answers = answers_by_attempt[attempt.id]

        # FIXME: for LAB_ID 35 only
        if lab_proxy.lab_id == 35:
            correct_count = len([answer for answer in attempt.answers if answer.is_correct])
            attempt.custom_score = 100 * correct_count / problems.count()

    return attempts


def get_answers(user_attempt):
    answers = UserAnswer.objects.filter(attempt=user_attempt).order_by('created_at')
    return answers
