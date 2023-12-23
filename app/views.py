from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.forms import model_to_dict
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.core.paginator import Paginator, EmptyPage
from .models import Question, QuestionTag, Answer, QuestionReaction, AnswerReaction, Tag
from .forms import LoginForm, RegisterForm, AskForm, AnswerForm, EditProfileForm

PER_PAGE = 6

def create_new_tags(tags):
    for tag_name in tags:
        if (not Tag.objects.filter(word=tag_name)):
            Tag.objects.create(word=tag_name)

def create_new_question(author, title, content, tags):
    question = Question.objects.create(author=author, title=title, content=content)
    question_tags = [QuestionTag(question=question, tag=Tag.objects.filter(word=tag_name).first()) for tag_name in tags]
    QuestionTag.objects.bulk_create(question_tags)

    return question.id

def redirect_to_previous(request):
    continue_url = request.GET.get('continue', '/')
    if continue_url == '/':
        continue_url = request.GET.get('next', '/')
    return redirect(continue_url)

def paginate(objects, page, per_page=PER_PAGE):
    paginator = Paginator(objects, per_page)
    number_of_pages = paginator.num_pages

    try:
        page = paginator.page(page)
        return {'page': page, 'number_of_pages': number_of_pages}
    except EmptyPage:
        return None

def handle_pagination(request, objects, context=None, need_tags=False):
    page_number = get_page_or_one(request)
    context = context or {}

    try:
        pagination = paginate(objects, page_number)
        page = pagination['page']

        if page is None:
            raise EmptyPage
        reactions = []
        number_of_pages = pagination['number_of_pages']
        if need_tags:
            reactions = [QuestionReaction.objects.get_reactions(question.id) for question in page]
            reaction_types = [QuestionReaction.objects.filter(question=question, user=request.user).first().type if  request.user.is_authenticated and QuestionReaction.objects.filter(question=question, user=request.user).exists() else 'None' for question in page]
            tags = get_tags_per_page(page)
            items_with_tags = tuple(zip(page, tags, reactions, reaction_types))
            context['items_with_reactions_tags'] = items_with_tags
        else:
            reactions = [AnswerReaction.objects.get_reactions(answer.id) for answer in page]
            reaction_types = [AnswerReaction.objects.filter(answer=answer, user=request.user).first().type if request.user.is_authenticated and AnswerReaction.objects.filter(answer=answer, user=request.user).exists() else 'None' for answer in page]
            context['items_with_reactions'] = tuple(zip(page, reactions, reaction_types))

    except EmptyPage:
        return redirect('not_found')
    
    context.update({'page': page, 'number_of_pages': number_of_pages})
    return context

def get_page_or_one(request):
    page_number = request.GET.get('page')
    if page_number == None: page_number = 1
    return page_number

def get_tags_per_page(page):
    tags = []
    for question in page.object_list:
        tags.append(QuestionTag.objects.get_tags_by_question(question))
    return tags

def index(request):
    questions = Question.objects.get_newest_questions()
    context = handle_pagination(request, questions, need_tags=True)

    return render(request, 'index.html', context)

def hot(request):
    questions = Question.objects.get_best_questions()
    context = handle_pagination(request, questions, {'questions_count': len(questions)}, need_tags=True)
    return render(request, 'index.html', context)

def tag_index(request, tag_name):
    questions = [question for question in QuestionTag.objects.get_question_by_tag_name(tag_name)]
    context = handle_pagination(request, questions,{'questions_count': len(questions), 'tag_name': tag_name}, need_tags=True)

    return render(request, 'tag.html', context)

def question(request, question_id):
    try:
        question_item = Question.objects.get(id=question_id)
    except:
        return redirect('not_found')
    if request.user.is_authenticated and QuestionReaction.objects.filter(question=Question.objects.get(pk=question_id), user=request.user).exists():
        question_reaction_type = QuestionReaction.objects.get(question=Question.objects.get(pk=question_id), user = request.user).type
    else:
        question_reaction_type = 'None'
    question_reactions = QuestionReaction.objects.get_reactions(question_id)
    answers = Answer.objects.get_answers_by_question(question_item)
    question_tags = QuestionTag.objects.get_tags_by_question(Question.objects.get(id=question_id))
    context = handle_pagination(request, answers, {'answers_count': len(answers), 'question': question_item, 'question_reactions': question_reactions, 'question_tags': question_tags, 'question_reaction_type': question_reaction_type})
    if request.method == 'GET':
        answer_form = AnswerForm()
    if request.method == 'POST':
        answer_form = AnswerForm(request.POST)
        if answer_form.is_valid():
            content = answer_form.cleaned_data['content']
            user = request.user
            if user.is_authenticated:
                Answer.objects.create(content=content, question=question_item, author=user)
                answers = Answer.objects.get_answers_by_question(question_item)
                last_page = Paginator(answers, PER_PAGE).num_pages
                redirect_url = reverse('question', args=[question_id]) + f'?page={last_page}'

                return redirect(redirect_url)
            else:
                answer_form.add_error(None, 'Login first')

    context.update({'form': answer_form})
    return render(request, 'question.html', context)

def log_in(request):
    if request.method == 'GET':
        login_form = LoginForm()
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user = authenticate(request, **login_form.cleaned_data)
            if user is not None:
                login(request, user)
                messages.success(request, 'You have successfully logged in.')
                return redirect_to_previous(request)
            else:
                login_form.add_error(None, "Wrong username or password")
    else:
        login_form = LoginForm()
    return render(request, 'login.html', {'form': login_form})

def sign_up(request):
    if request.method == 'GET':
        user_form = RegisterForm()
    if request.method == 'POST':
        user_form = RegisterForm(request.POST)
        if user_form.is_valid():
            try:
                user = user_form.save()
                if user:
                    login(request, user)
                    messages.success(request, 'Congratulations! You have successfully created an account.')
                    return redirect(reverse('index'))
                else:
                    user_form.add_error(None, 'An error occured while creating new account!')
            except:
                user_form.add_error(None, 'Username is already taken')
    return render(request, 'signup.html', {'form': user_form})

def log_out(request):
    logout(request)
    messages.success(request, 'You have logged out!')
    return redirect_to_previous(request)

@login_required
def ask(request):
    if request.method == 'GET':
        ask_form = AskForm()
    if request.method == 'POST':
        ask_form = AskForm(request.POST)
        if ask_form.is_valid():
            tags = request.POST.get('tags')
            if tags.find(',') != -1:
                ask_form.add_error(None, 'Enter tags via space')
            else:
                tags = tags.lower().split(" ")
                title = request.POST.get('title')
                content = request.POST.get('content')
                user = request.user
                create_new_tags(tags)
                question_id = create_new_question(user, title, content, tags)

                return redirect(reverse('question', args=[question_id]))
        
    return render(request, 'ask.html', {'form': ask_form})

@login_required()
def settings(request):
    if request.method == 'GET':
        edit_profile_form = EditProfileForm(initial=model_to_dict(request.user))
    if request.method == 'POST':
        edit_profile_form = EditProfileForm(request.POST, request.FILES, instance=request.user, initial=model_to_dict(request.user))
        if edit_profile_form.is_valid():
            edit_profile_form.save()
            messages.success(request, 'Your account has been updated successfully.')

    return render(request, 'settings.html', {'form': edit_profile_form})

def not_found(request):
    return render(request, 'not-found.html')

@login_required
@csrf_exempt
def reaction(request):
    content_type = request.POST.get('content_type')
    type = request.POST.get('reaction_type')
    if content_type == 'question':
        id = request.POST.get('id')
        question = get_object_or_404(Question, pk=id)
        QuestionReaction.objects.toggle_reaction(user=request.user, question=question, type=type)
        count = QuestionReaction.objects.get_reactions(question_id=id)
    elif content_type == 'answer':
        id = request.POST.get('id')
        answer = get_object_or_404(Answer, pk=id)
        AnswerReaction.objects.toggle_reaction(user=request.user, answer=answer, type=type)
        count = AnswerReaction.objects.get_reactions(answer_id=id)

    return JsonResponse({'counter': count})

@csrf_exempt
def correct_answer(request):
    answer_id = request.POST.get('id')
    answer = Answer.objects.get(pk=answer_id)
    if request.user == answer.question.author:
        if answer.is_correct == False:
            answer.is_correct = True
            answer.save()
        elif answer.is_correct == True:
            answer.is_correct = False
            answer.save()

    return JsonResponse({'Correct': True})