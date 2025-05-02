def group_context(request):
    """
    Context processor that adds group-based information to the template context.
    """
    if request.user.is_authenticated:
        try:
            primary_group = request.user.profile.get_primary_group()
            return {
                'user_group': primary_group.name if primary_group else None,
                'user_group_display': primary_group.name.replace('_', ' ').title() if primary_group else None,
                'user_groups': request.user.groups.all(),
                'is_admin': request.user.groups.filter(name='Administrator').exists(),
                'is_coordinator': request.user.groups.filter(name='Course Coordinator').exists(),
                'is_instructor': request.user.groups.filter(name='Instructor').exists(),
                'is_student': request.user.groups.filter(name='Student').exists(),
            }
        except Exception:
            pass
    
    return {
        'user_group': None,
        'user_group_display': 'Guest',
        'user_groups': [],
        'is_admin': False,
        'is_coordinator': False,
        'is_instructor': False,
        'is_student': False,
    } 