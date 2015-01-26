'''
django admin pages for courseware model
'''

from student.models import UserProfile, UserTestGroup, CourseEnrollmentAllowed
from student.models import CourseEnrollment, Registration, PendingNameChange, CourseAccessRole, CourseAccessRoleAdmin, \
    CourseEnrollmentAdmin
from ratelimitbackend import admin


admin.site.register(UserProfile)

admin.site.register(UserTestGroup)

admin.site.register(CourseEnrollment, CourseEnrollmentAdmin)

admin.site.register(CourseEnrollmentAllowed)

admin.site.register(Registration)

admin.site.register(PendingNameChange)

admin.site.register(CourseAccessRole, CourseAccessRoleAdmin)
