from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from utils.decorators import login_required
from .forms import CommentForm, PostForm
from .models import Post
from member.models import User
import operator
from web3 import Web3, HTTPProvider
import os
from solc import compile_files


rpc_url = 'http://10.10.20.100:8545'
w3 = Web3(HTTPProvider(rpc_url))

## deploy_contract
class mytoken:
    # contract_file_name(solidty의 파일 명) , contract_name(solidity 내 Contract 명) 생성자  초기화
    def __init__(self,contract_file_name,contract_name):
        compiled_sol = compile_files([contract_file_name])
        contract_interface = compiled_sol['{}:{}'.format(contract_file_name,contract_name)]

        contract = w3.eth.contract(abi= contract_interface['abi'],
                                   bytecode= contract_interface['bin'],
                                   bytecode_runtime= contract_interface['bin-runtime'])
        tx_hash = contract.deploy(transaction={'from': w3.eth.accounts[0]})
        self.mining(2)
        tx_recepit = w3.eth.getTransactionReceipt(tx_hash)
        contract_address = tx_recepit['contractAddress']
        self.contract_instance = contract(contract_address)

    # 토큰 전송
    def send_token(self,sender,to,value):
        self.contract_instance.functions.transfer(to,value).transact({'from':sender})


    # user의 토큰 잔액 조회
    def show_token(self,addr):
        return self.contract_instance.call().balanceOf(addr)

    # 토큰의 총 유통량
    def show_total_token(self):
        return self.contract_instance.call().totalSupply()

    # 채굴
    def mining(self,thread):
        n_blockNumber = w3.eth.blockNumber
        while True:
            if w3.eth.blockNumber == n_blockNumber+1:
                w3.miner.stop()
                break
            else:
                w3.miner.start(thread)

cookie = mytoken('post/MyBasicToken.sol','MyBasicToken')




def profile(request):
    name = request.user
    gender = request.user.gender
    user_classification = request.user.user_classification
    posts = Post.objects.all().filter(author = request.user)
    wallet = request.user.wallet_address
    total_like = 0
    total_views = 0
    total_token = 0
    for post in posts:
        total_views += post.post_views
        total_like += post.like
    for i,j in enumerate(w3.eth.accounts):
        if j == wallet:
            total_token += cookie.show_token(w3.eth.accounts[i])
            print(cookie.show_token(w3.eth.accounts[i]))
        else:
            continue
    context = {
        'name' : name,
        'gender' : gender,
        'user_classification' : user_classification,
        'posts' : posts,
        'wallet' : wallet,
        'total_like' : total_like,
        'total_views' : total_views,
        'total_token' : total_token,

    }
    return render(request, 'post/profile.html', context)

def post_list(request):
    posts = Post.objects.all()
    comment_form = CommentForm()
    context = {
        'posts': posts,
        'comment_form': comment_form,
    }
    return render(request, 'post/post_list.html', context)

def post_detail(request, post_pk):
    post = get_object_or_404(Post, pk=post_pk)
    comment_form = CommentForm()
    post.up_post_views
    context = {
        'post': post,
        'comment_form': comment_form,
    }
    return render(request, 'post/post_detail.html', context)

@login_required
def post_create(request):
    if request.method == 'POST':
        # PostForm은 파일을 처리하므로 request.FILES도 함께 바인딩
        post_form = PostForm(request.POST, request.FILES)
        if post_form.is_valid():
            # author필드를 채우기 위해 인스턴스만 생성
            post = post_form.save(commit=False)
            # author필드를 채운 후 DB에 저장
            post.author = request.user
            post.ingredient = post.ingredient
            post.recipe_list = post.recipe_list
            post.save()
            # 성공 알림을 messages에 추가 후 post_list뷰로 이동
            messages.success(request, '글이 등록되었습니다')
            return redirect('post:post_list')
    else:
        post_form = PostForm()

    context = {
        'post_form': post_form,
    }
    return render(request, 'post/post_create.html', context)

@login_required
def comment_create(request, post_pk):
    # GET파라미터로 전달된 작업 완료 후 이동할 URL값
    next_path = request.GET.get('next')
    # 요청 메서드가 POST방식 일 때만 처리
    if request.method == 'POST':
        # Post인스턴스를 가져오거나 404 Response를 돌려줌
        post = get_object_or_404(Post, pk=post_pk)
        # request.POST데이터를 이용한 Bounded Form생성
        comment_form = CommentForm(request.POST)
        # 올바른 데이터가 Form인스턴스에 바인딩 되어있는지 유효성 검사
        if comment_form.is_valid():
            # 유효성 검사에 통과하면 ModelForm의 save()호출로 인스턴스 생성
            # DB에 저장하지 않고 인스턴스만 생성하기 위해 commit=False옵션 지정
            comment = comment_form.save(commit=False)
            # CommentForm에 지정되지 않았으나 필수요소인 author와 post속성을 지정
            comment.post = post
            comment.author = request.user
            # DB에 저장
            comment.save()
            # 성공 메시지를 다음 request의 결과로 전달하도록 지정
            messages.success(request, '댓글이 등록되었습니다')
        else:
            # 유효성 검사에 실패한 경우
            # 에러 목록을 순회하며 에러메시지를 작성, messages의 error레벨로 추가
            error_msg = '댓글 등록에 실패했습니다\n{}'.format(
                '\n'.join(
                    [f'- {error}'
                     for key, value in comment_form.errors.items()
                     for error in value]))
            messages.error(request, error_msg)
        # next parameter에 값이 담겨 온 경우, 해당 경로로 이동

        if next_path:
            return redirect(next_path)
        # next parameter가 빈 경우 post_list뷰로 이동
        return redirect('post:post_list')

@login_required
def post_like_toggle(request, post_pk):
    # GET파라미터로 전달된 이동할 URL
    next_path = request.GET.get('next')
    # post_pk에 해당하는 Post객체
    post = get_object_or_404(Post, pk=post_pk)
    # 요청한 사용자
    user = request.user
    # 사용자의 like_posts목록에서 like_toggle할 Post가 있는지 확인
    filtered_like_posts = user.like_posts.filter(pk=post.pk)

    # 존재할경우, like_posts목록에서 해당 Post를 삭제
    if filtered_like_posts.exists():
        user.like_posts.remove(post)
        post.down_counter

    # 없을 경우, like_posts목록에 해당 Post를 추가
    else:
        user.like_posts.add(post)
        post.up_counter

    # 이동할 path가 존재할 경우 해당 위치로, 없을 경우 Post상세페이지로 이동
    if next_path:
        return redirect(next_path)

    return redirect('post:post_detail', post_pk=post_pk)


def reward_list(request):
    users = User.objects.all()
    posts = Post.objects.all()
    score_list = {}
    for user in users:
        posts = Post.objects.all().filter(author=user)
        score = 0
        if posts:
            for post in posts:
                score += post.like * 4 + post.post_views*1
        score_list[user.username] = score
    top5_user = sorted(score_list.items(), key=operator.itemgetter(1), reverse=True)[:5]
    context = {
        'top5_user' : top5_user
    }

    return render(request, 'post/reward_list.html', context)


def reward(request):
    if request.method=='POST':
            users = User.objects.all()
            posts = Post.objects.all()
            for user in users:
                posts = Post.objects.all().filter(author=user)
                score = 0
                if posts:
                    for post in posts:
                        score += post.like * 4 + post.post_views*1

                for i,j in enumerate(w3.eth.accounts):
                    if j == user.wallet_address:
                        cookie.send_token(w3.eth.accounts[0],w3.eth.accounts[i],score)
                    else:
                        continue

            cookie.mining(2)

    return render(request, 'post/reward.html')
