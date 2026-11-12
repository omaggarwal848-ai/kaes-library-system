def user_role_context(request):
    if request.user.is_authenticated:
        profile = getattr(request.user, 'profile', None)
        is_admin = False
        is_student = False
        if profile:
            is_admin = profile.is_admin
            is_student = profile.is_student
        elif request.user.is_superuser or request.user.is_staff:
            is_admin = True
        return {
            'user_profile': profile,
            'is_admin': is_admin,
            'is_student': is_student,
        }
    return {
        'user_profile': None,
        'is_admin': False,
        'is_student': False,
    }
