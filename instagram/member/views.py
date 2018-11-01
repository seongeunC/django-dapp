from django.contrib.auth import (
    login as django_login,
    logout as django_logout,
)
from django.shortcuts import render, redirect
from web3 import Web3, HTTPProvider
from .forms import LoginForm, SignupForm
from .models import User

rpc_url = 'http://10.10.20.100:8545'
w3 = Web3(HTTPProvider(rpc_url))



def login(request):
    if request.method == 'POST':
        # 로그인 성공 후 이동할 URL. 주어지지 않으면 None
        next = request.GET.get('next')
        # Data bounded form인스턴스 생성
        # AuthenticationForm의 첫 번째 인수는 해당 request가 되어야 한다
        login_form = LoginForm(request=request, data=request.POST)
        # 유효성 검증에 성공할 경우
        # AuthenticationForm을 사용하면 authenticate과정까지 완료되어야 유효성 검증을 통과한다
        if login_form.is_valid():
            # AuthenticatonForm에서 인증(authenticate)에 성공한 유저를 가져오려면 이 메서드를 사용한다
            user = login_form.get_user()
            # Django의 auth앱에서 제공하는 login함수를 실행해 앞으로의 요청/응답에 세션을 유지한다
            django_login(request, user)
            # next가 존재하면 해당 위치로, 없으면 Post목록 화면으로 이동
            return redirect(next if next else 'post:post_list')
        # 인증에 실패하면 login_form에 non_field_error를 추가한다
        login_form.add_error(None, '아이디 또는 비밀번호가 올바르지 않습니다')
    else:
        login_form = LoginForm()

    context = {
        'login_form': login_form,
    }
    return render(request, 'member/login.html', context)


def logout(request):
    django_logout(request)
    return redirect('post:post_list')


def signup(request):
    if request.method == 'POST':
        signup_form = SignupForm(request.POST)
        # 유효성 검증에 통과한 경우 (username의 중복과 password1, 2의 일치 여부)
        if signup_form.is_valid():
            # 유저를 생성 후 해당 User를 로그인 시킨다
            user = signup_form.save()
            django_login(request, user)
            wallet = User.objects.get(username=request.POST['username'])
            wallet.wallet_address = w3.personal.newAccount(request.POST['password2'])
            wallet.save()
            return redirect('post:post_list')
    else:
        signup_form = SignupForm()

    context = {
        'signup_form': signup_form,
    }

    return render(request, 'member/signup.html', context)
