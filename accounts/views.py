from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model


def login_view(request):
    if request.user.is_authenticated:
        return redirect('main')

    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        # DEBUG: 로그인 디버깅
        User = get_user_model()
        all_users = list(User.objects.values_list('username', flat=True))
        user_exists = User.objects.filter(username=username).exists()
        print(f'[LOGIN DEBUG] attempt: "{username}", pw_len={len(password)}, user_exists={user_exists}, all_users={all_users}', flush=True)

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'main')
            return redirect(next_url)
        else:
            print(f'[LOGIN DEBUG] authenticate() returned None for "{username}"', flush=True)
            error = '아이디 또는 비밀번호가 올바르지 않습니다.'

    return render(request, 'accounts/login.html', {'error': error})


def logout_view(request):
    logout(request)
    return redirect('main')
