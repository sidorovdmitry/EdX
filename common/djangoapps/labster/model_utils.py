from labster.models import UserSave


def get_latest_user_save(lab_proxy, user_id):
    try:
        user_save = UserSave.objects\
            .filter(lab_proxy=lab_proxy, user_id=user_id).latest('id')
    except:
        return None

    return user_save
