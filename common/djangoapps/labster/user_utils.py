import re


def generate_unique_username(name, model):
    """
    Generate unique username from name by removing spaces, and
    adding numbers if necessary
    """

    index = 0
    while True:
        try:
            username = generate_username(name.strip(), index=index)
            model.objects.get(username__iexact=username)
        except model.DoesNotExist:
            return username
        else:
            index += 1


def generate_username(name, index):
    name = re.sub(r'[^\w+]+', '', name)
    if index > 0:
        name = "{}{}".format(name, index)

    return name
