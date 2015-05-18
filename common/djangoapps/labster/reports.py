from collections import defaultdict

from labster.models import (
    UserAnswer, UserAttempt, Problem, get_user_attempts_from_lab_proxy, Lab,
)


ADAPTIVE_LABS = [73]


def get_attempts_and_answers(
        lab_proxy, user, latest_only=False,
        attempts=None,
        problems=None):

    if not attempts:
        attempts = UserAttempt.objects.filter(lab_proxy=lab_proxy, user=user)\
            .exclude(useranswer=None).order_by('-created_at')

    if latest_only:
        attempts = list(attempts)[:1]

    answers = UserAnswer.objects.filter(attempt__in=attempts).order_by('problem__order')

    # special case for LAB_ID 35 (adaptive cytogenetics)
    if lab_proxy.lab_id == 35:
        quiz_ids = ["Cyto-{}-Post".format(i) for i in range(11, 41)]
        if not problems:
            problems = Problem.objects.filter(is_active=True, element_id__in=quiz_ids)
        answers = answers.filter(problem__in=problems)

    elif lab_proxy.lab_id == 73:
        quizblock = "QuizblockPostTest"
        if not problems:
            problems = Problem.objects.filter(is_active=True, quiz_block__lab_id=73, quiz_block__element_id=quizblock)
            print len(problems)
        answers = answers.filter(problem__in=problems)

    answers_by_attempt = defaultdict(list)
    answers_by_attempt_check = defaultdict(list)
    for answer in answers:
        if answer.quiz_id in answers_by_attempt_check[answer.attempt_id]:
            continue

        answers_by_attempt_check[answer.attempt_id].append(answer.quiz_id)
        answers_by_attempt[answer.attempt_id].append(answer)

    for attempt in attempts:
        attempt.answers = answers_by_attempt[attempt.id]

        # FIXME: for LAB_ID 35 only
        if lab_proxy.lab_id in [35, 73]:
            correct_count = len([answer for answer in attempt.answers if answer.is_correct])
            print correct_count, len(problems)
            attempt.custom_score = 100 * correct_count / len(problems)

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
                user.email.encode('utf-8'),
                user.profile.name.encode('utf-8'),
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


def get_end_time_from_userattempt(userattempt):
    if userattempt.finished_at:
        return userattempt.finished_at
    return userattempt.completed_at


def get_last_end_time(userattempt):
    end_time = get_end_time_from_userattempt(userattempt)
    try:
        useranswer = UserAnswer.objects.filter(attempt=userattempt).order_by('-end_time')[0]
    except IndexError:
        pass
    else:
        if end_time and useranswer.end_time:
            end_time = end_time if end_time > useranswer.end_time else useranswer.end_time

    return end_time


def get_play_count(lab):
    return UserAttempt.objects.filter(lab_proxy__lab=lab).count()


def get_duration(lab):
    userattempts = UserAttempt.objects.filter(lab_proxy__lab=lab)
    duration = 0
    for ua in userattempts:
        end_time = get_last_end_time(ua)
        if end_time:
            _duration = (end_time - ua.created_at).seconds
            duration += _duration

    return duration
