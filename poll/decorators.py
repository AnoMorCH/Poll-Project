from django.shortcuts import redirect
from django.urls import resolve


def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('poll:hello')
        else:
            return view_func(request, *args, **kwargs)

    return wrapper_func


def allowed_users(allowed_roles=[], allowed_candidate_statuses=[], is_voted_allowed=True):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            # Admin always has access to all web pages
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            role = request.user.ROLE_CHOICES[request.user.role - 1][1]

            # Redirecting moderator to 'moderator-hello' if he isn't allowed visiting the web page
            if role == 'Moderator':
                if not (role in allowed_roles):
                    return redirect('poll:moderator-hello')
                else:
                    return view_func(request, *args, **kwargs)

            if not (role in allowed_roles):
                return redirect('poll:notice-access-is-forbidden')

            # Protection from access to the pages through 'Elector' or 'Candidate' roles
            current_url = resolve(request.path_info).url_name

            if current_url in ['moderator-candidates', 'moderator-detail']:
                return redirect('poll:notice-access-is-forbidden')

            if role == 'Elector':
                # Since 'Elector' has only one possible group 'Voted', this construction is acceptable
                is_user_voted = request.user.groups.exists()

                if is_user_voted == True and is_voted_allowed == False:
                    return redirect('poll:notice-access-is-forbidden')
                else:
                    return view_func(request, *args, **kwargs)

            if role == 'Candidate':
                # If there is only one group, it means there is only candidate_status. In another situation it means
                # this user has voted and there is need to find out which cell of the list user.groups.all() is stored
                # a candidate status
                groups_amount = len(request.user.groups.all())

                if groups_amount == 1:
                    if allowed_candidate_statuses[0] == 'all':
                        return view_func(request, *args, **kwargs)

                    candidate_status = request.user.groups.all()[0].name

                    if candidate_status in allowed_candidate_statuses:
                        return view_func(request, *args, **kwargs)
                    else:
                        return redirect('poll:notice-access-is-forbidden')

                if groups_amount == 2:
                    is_candidate_group_allowed = False

                    if allowed_candidate_statuses[0] == 'all':
                        is_candidate_group_allowed = True
                    else:
                        candidate_status = request.user.groups.all()[0].name

                        if candidate_status == 'Voted':
                            candidate_status = request.user.groups.all()[1].name

                        if candidate_status in allowed_candidate_statuses:
                            is_candidate_group_allowed = True

                    if is_candidate_group_allowed and is_voted_allowed:
                        return view_func(request, *args, **kwargs)
                    else:
                        return redirect('poll:notice-access-is-forbidden')

        return wrapper_func

    return decorator
