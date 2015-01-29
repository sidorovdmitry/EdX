# create dummy user

`sudo -u www-data /edx/bin/python.edxapp ./manage.py lms --settings=aws labster_dummy_user 14`

14 is the number of dummy user

# create courses for all labs

`sudo -u www-data /edx/bin/python.edxapp ./manage.py cms --settings=aws create_all_course data/config.yaml`

You could check `data/create_all_courses.yaml` for example.
