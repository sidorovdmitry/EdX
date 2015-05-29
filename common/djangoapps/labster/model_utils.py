from labster.models import UserSave


def get_latest_user_save(lab_proxy, user_id, user_attempt):
    try:
        user_save = UserSave.objects\
            .filter(lab_proxy=lab_proxy, user_id=user_id, attempt=user_attempt).latest('id')
    except:
        return None

    return user_save
