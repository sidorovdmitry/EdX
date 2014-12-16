from collections import defaultdict

from labster.models import UserAnswer, UserAttempt, Problem, get_user_attempts_from_lab_proxy


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
    answers_by_attempt_check = defaultdict(list)
    for answer in answers:
        if answer.quiz_id in answers_by_attempt_check[answer.quiz_id]:
            continue

        answers_by_attempt_check[answer.attempt_id].append(answer.quiz_id)
        answers_by_attempt[answer.attempt_id].append(answer)

    for attempt in attempts:
        attempt.answers = answers_by_attempt[attempt.id]

        # FIXME: for LAB_ID 35 only
        if lab_proxy.lab_id == 35:
            correct_count = len([answer for answer in attempt.answers if answer.is_correct])
            attempt.custom_score = 100 * correct_count / problems.count()

            if attempt.custom_score > 100:
                attempt.custom_score = 100

    return attempts


def get_answers(user_attempt):
    answers = UserAnswer.objects.filter(attempt=user_attempt).order_by('created_at')
    return answers


def user_attempts_to_rows(user_attempts):
    rows = []
    for user_attempt in user_attempts:
        user = user_attempt.user
        user_answers = UserAnswer.objects.filter(attempt=user_attempt).order_by('problem__order', '-created_at')
        answered = []

        for user_answer in user_answers:
            if user_answer.quiz_id in answered:
                continue

            answered.append(user_answer.quiz_id)

            row = [
                user.email,
                user.profile.name,
                user_answer.question.encode('utf-8'),
                user_answer.answer_string.encode('utf-8'),
                user_answer.correct_answer.encode('utf-8'),
                user_answer.completion_time,
                user_answer.score,
                10,
                "yes" if user_answer.is_view_theory_clicked else "",
                user_answer.attempt_count,
            ]

            rows.append(row)
    return rows


def unique_user_attempts(user_attempts):
    attempts = []
    user_ids = []
    for user_attempt in user_attempts:
        if user_attempt.user.id in user_ids:
            continue

        user_ids.append(user_attempt.user.id)
        attempts.append(user_attempt)

    return attempts


def export_answers(lab_proxy):

    headers = [
        'Email',
        'Name',
        'Question',
        'User Answer',
        'Correct Answer',
        'Time Spent (seconds)',
        'Score',
        'Max Score',
        'View Theory',
        'Number of Attempts',
    ]

    user_attempts = get_user_attempts_from_lab_proxy(lab_proxy)
    all_users = user_attempts.values_list('user__id', flat=True)
    all_users = list(set(all_users))

    completed_user_attempts = user_attempts.filter(is_completed=True).order_by('-created_at')
    completed_users = completed_user_attempts.values_list('user__id', flat=True)
    completed_users = list(set(completed_users))

    missing_users = set(all_users) - set(completed_users)
    missing_user_attempts = user_attempts.filter(user__id__in=missing_users).order_by('-created_at')

    completed_user_attempts = unique_user_attempts(completed_user_attempts)
    missing_user_attempts = unique_user_attempts(missing_user_attempts)

    rows = [headers]
    rows.extend(user_attempts_to_rows(completed_user_attempts))
    rows.extend(user_attempts_to_rows(missing_user_attempts))

    return rows
