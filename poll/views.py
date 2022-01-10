from django.http import Http404
from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate, logout, get_user_model

from .models import Candidate, AdminData
from .decorators import unauthenticated_user, allowed_users
from .forms import CreateCandidateForm, ModerateCandidateForm, CreateUserForm, EditModeratorInstruction

User = get_user_model()


@unauthenticated_user
def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('poll:hello')
        else:
            messages.info(request, 'Username OR password is incorrect')

    return render(request, 'poll/login.html')


@unauthenticated_user
def register_page(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)

        if form.is_valid():
            user = form.save()

            user.role = User.ELECTOR
            user.save()

            username = form.cleaned_data.get('username')
            messages.success(request, 'Account was successfully create for ' + username)

    context = {'form': form}

    return render(request, 'poll/register.html', context)


@login_required(login_url='poll:login')
def logout_page(request):
    logout(request)
    return redirect('poll:login')


@login_required(login_url='poll:login')
@allowed_users(['Elector', 'Candidate'], ['all'])
def hello(request):
    context = standard_context(request)
    return render(request, 'poll/hello.html', context)


# Moderator has access to views 'candidate' and 'detail' because they are used in the logic of moderator's pages
@login_required(login_url='poll:login')
@allowed_users(['Elector', 'Candidate', 'Moderator'], ['all'])
def candidates(request, **kwargs):
    context = standard_context(request)

    candidates_list = Candidate.objects.order_by('name')
    context['candidates_list'] = candidates_list
    template = kwargs['template_name']

    return render(request, template, context)


@login_required(login_url='poll:login')
@allowed_users(['Elector', 'Candidate', 'Moderator'], ['all'])
def detail(request, candidate_id, **kwargs):
    context = standard_context(request)

    candidate = get_object_or_404(Candidate, pk=candidate_id)
    context['candidate'] = candidate
    template = kwargs['template_name']

    return render(request, template, context)


@login_required(login_url='poll:login')
@allowed_users(['Candidate'], ['Application Draft', 'Application Final'])
def notifications(request):
    context = standard_context(request)

    candidate = get_object_or_404(Candidate, author=request.user.username)
    context['moderated'] = candidate.moderated
    context['refusal_reason'] = candidate.refusal_reason

    return render(request, 'poll/notifications.html', context)


@login_required(login_url='poll:login')
@allowed_users(['Elector', 'Candidate'], ['all'], False)
def vote(request):
    try:
        selected_candidate = request.POST['choice']
    except(KeyError, Candidate.DoesNotExist):
        return Http404
    else:
        new_group = Group.objects.get(name='Voted')
        request.user.groups.add(new_group)

        candidate = get_object_or_404(Candidate, pk=selected_candidate)
        candidate.votes += 1
        candidate.save()

        return redirect('poll:results')


@login_required(login_url='poll:login')
@allowed_users(['Elector', 'Candidate'], ['Application Process'])
def create_participate_form(request):
    form = CreateCandidateForm()

    new_group = Group.objects.get(name='Application Process')
    request.user.groups.add(new_group)
    request.user.role = User.CANDIDATE
    request.user.save()

    context = standard_context(request)
    context['form'] = form

    if request.method == 'POST':
        form = CreateCandidateForm(request.POST, request.FILES)

        if form.is_valid():
            result_form = form.save(commit=False)
            result_form.author = request.user
            result_form.save()

            check_candidate(request, form)

            return change_group_by_button(request, form)

    return render(request, 'poll/participate.html', context)


@login_required(login_url='poll:login')
@allowed_users(['Candidate'], ['Application Draft'])
def update_participate_form(request, author):
    context = standard_context(request)

    # It checks if another user tries to change data of a foreign user
    if author != request.user.username:
        return redirect('poll:notice-access-is-forbidden')

    candidate = get_object_or_404(Candidate, author=author)
    form = CreateCandidateForm(instance=candidate)

    user = request.user
    if user.checked_by_moderator:
        context['refusal_reason'] = candidate.refusal_reason
        context['checked_by_moderator'] = True

    context['form'] = form

    if request.method == 'POST':
        form = CreateCandidateForm(request.POST, instance=candidate)

        if form.is_valid():
            form.save()
            check_candidate(request, form)

        return change_group_by_button(request, form)

    return render(request, 'poll/participate.html', context)


@login_required(login_url='poll:login')
@allowed_users(['Moderator'])
def moderator_page(request):
    context = standard_context(request)
    return render(request, 'poll/moderator-hello.html', context)


@login_required(login_url='poll:login')
@allowed_users(['Moderator'])
def moderator_moderate(request):
    if request.method == 'POST':
        selected_choice = request.POST['choice']
        selected_candidate = request.POST['candidate-id']

        candidate = get_object_or_404(Candidate, pk=selected_candidate)

        moderated_user = get_object_or_404(User, username=candidate.author)
        moderated_user.checked_by_moderator = True
        moderated_user.save()

        if selected_choice == 'ACCEPT':
            candidate.moderated = True
            candidate.save()

            return redirect('poll:notice-moderator-candidate-accepted')
        else:
            return redirect('poll:moderator-refuse', candidate_id=selected_candidate)


@login_required(login_url='poll:login')
@allowed_users(['Moderator'])
def moderator_refuse(request, candidate_id):
    context = standard_context(request)

    candidate = Candidate.objects.get(id=candidate_id)
    context['candidate'] = candidate

    form = ModerateCandidateForm()

    if request.method == 'POST':
        form = ModerateCandidateForm(request.POST, instance=candidate)

        if form.is_valid():
            form.save()

        moderated_user = get_object_or_404(User, username=candidate.author)
        switch_users_candidate_status(moderated_user, 'Application Draft')

        return redirect('poll:notice-moderator-candidate-refused')

    context['form'] = form

    return render(request, 'poll/moderator-refusal.html', context)


@login_required(login_url='poll:login')
@allowed_users(['Moderator'])
def moderator_instruction(request):
    context = standard_context(request)
    context['instruction'] = create_admin_data_or_use_current().instruction

    if request.method == 'POST':
        return redirect('poll:moderator-edit-instruction')

    return render(request, 'poll/moderator-instruction.html', context)


@login_required(login_url='poll:login')
@allowed_users()
def moderator_edit_instruction(request):
    context = standard_context(request)

    admin_data = create_admin_data_or_use_current()
    context['instruction'] = create_admin_data_or_use_current().instruction

    form = EditModeratorInstruction(instance=admin_data)

    if request.method == 'POST':
        form = EditModeratorInstruction(request.POST, instance=admin_data)

        if form.is_valid():
            form.save()

        return redirect('poll:notice-moderator-instruction-saved')

    context['form'] = form

    return render(request, 'poll/moderator-edit-instruction.html', context)


@login_required(login_url='poll:login')
@allowed_users(['Elector', 'Candidate'], ['all'])
def notice_access_is_forbidden(request):
    context = standard_context(request)
    return render(request, 'poll/notice-access-is-forbidden.html', context)


@login_required(login_url='poll:login')
@allowed_users(['Elector'])
def notice_participate_change_status(request):
    context = standard_context(request)
    return render(request, 'poll/notice-participate-change-status.html', context)


@login_required(login_url='poll:login')
@allowed_users(['Candidate'], ['Application Draft'])
def notice_participate_candidate_already_exists(request):
    context = standard_context(request)
    return render(request, 'poll/notice-participate-candidate-already-exists.html', context)


@login_required(login_url='poll:login')
@allowed_users(['Candidate'], ['Application Final'])
def notice_participate_sent(request):
    context = standard_context(request)
    return render(request, 'poll/notice-participate-sent.html', context)


@login_required(login_url='poll:login')
@allowed_users(['Candidate'], ['Application Draft'])
def notice_participate_update_sent(request):
    context = standard_context(request)
    return render(request, 'poll/notice-participate-update-sent.html', context)


@login_required(login_url='poll:login')
@allowed_users()
def notice_moderator_instruction_saved(request):
    context = standard_context(request)
    return render(request, 'poll/notice-moderator-instruction-saved.html', context)


@login_required(login_url='poll:login')
@allowed_users(['Moderator'])
def notice_moderator_candidate_accepted(request):
    context = standard_context(request)
    return render(request, 'poll/notice-moderator-candidate-accepted.html', context)


@login_required(login_url='poll:login')
@allowed_users(['Moderator'])
def notice_moderator_candidate_refused(request):
    context = standard_context(request)
    return render(request, 'poll/notice-moderator-candidate-refused.html', context)


# If a user has no groups, then he can't be 'Voted'.
# If he has only one group, then he can be either 'Voter' or 'Candidate' ('Application Process', ...)
# If he has two groups, then he definitely has to be 'Candidate' and 'Voted' according the architecture of the project
def is_user_voted(request):
    if not request.user.groups.exists():
        return False

    if len(request.user.groups.all()) == 2:
        return True

    current_group = request.user.groups.all()[0]

    if current_group.name == 'Voted':
        return True


def get_users_candidate_status(user):
    current_status = user.groups.all()[0]

    if current_status.name == 'Voted':
        current_status = user.groups.all()[1]

    return current_status


def switch_users_candidate_status(user, new_status_name):
    current_status = get_users_candidate_status(user)
    user.groups.remove(current_status)

    new_status = Group.objects.get(name=new_status_name)
    user.groups.add(new_status)


def standard_context(request):
    context = {
        'username': request.user.username,
    }

    if request.user.is_superuser:
        context['role'] = 'Admin'
    else:
        context['role'] = request.user.ROLE_CHOICES[request.user.role - 1][1]

    if is_user_voted(request):
        context['voted'] = True

    if context['role'] == 'Candidate':
        context['candidate_status'] = get_users_candidate_status(request.user).name
        context['checked_by_moderator'] = request.user.checked_by_moderator

    return context


def change_group_by_button(request, form):
    if 'final version' in form.data:
        candidate = Candidate.objects.get(author=request.user.username)

        if candidate.refusal_reason != '':
            candidate.refusal_reason = ''
            candidate.save()

            request.user.checked_by_moderator = False
            request.user.save()

        switch_users_candidate_status(request.user, 'Application Final')

        return redirect('poll:participate-sent')
    elif 'draft version' in form.data:
        switch_users_candidate_status(request.user, 'Application Draft')
        return redirect('poll:participate-update-sent')


def are_coinciding_candidates(request):
    new_candidates_name = request.POST['name']
    candidates_list = Candidate.objects.order_by('id')

    for candidate in candidates_list[:len(candidates_list) - 1]:
        if candidate.name == new_candidates_name:
            return True
    else:
        return False


def create_admin_data_or_use_current():
    try:
        admin_data = AdminData.objects.get(pk=1)
    except AdminData.DoesNotExist:
        admin_data = AdminData.objects.create()

    return admin_data


def check_candidate(request, form):
    if are_coinciding_candidates(request):
        switch_users_candidate_status(request.user, 'Application Draft')
        return notice_participate_candidate_already_exists(request)
    else:
        return change_group_by_button(request, form)
