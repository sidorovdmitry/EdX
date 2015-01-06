from django.shortcuts import render_to_response


def lms_robots(request):
    return render_to_response('labster/lms/robots.txt', {})


def cms_robots(request):
    return render_to_response('labster/cms/robots.txt', {})
