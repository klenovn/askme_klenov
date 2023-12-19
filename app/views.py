from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
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

def handle_pagination(request, objects, template_name, context=None, need_tags=False):
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
            tags = get_tags_per_page(page)
            items_with_tags = tuple(zip(page, tags, reactions))
            context['items_with_reactions_tags'] = items_with_tags
        else:
            reactions = [AnswerReaction.objects.get_reactions(answer.id) for answer in page]
            context['items_with_reactions'] = tuple(zip(page, reactions))

    except EmptyPage:
        return redirect('not_found')
    
    context.update({'page': page, 'number_of_pages': number_of_pages})
    return render(request, template_name, context)

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
    return handle_pagination(request, questions, 'index.html', need_tags=True)

def hot(request):
    questions = Question.objects.get_best_questions()
    return handle_pagination(request, questions, 'index.html', {'questions_count': len(questions)}, need_tags=True)

def tag_index(request, tag_name):
    questions = [question for question in QuestionTag.objects.get_question_by_tag_name(tag_name)]
    return handle_pagination(request, questions, 'tag.html', {'questions_count': len(questions), 'tag_name': tag_name}, need_tags=True)

def question(request, question_id):
    question_item = Question.objects.get(id=question_id)
    question_reactions = QuestionReaction.objects.get_reactions(question_id)
    answers = Answer.objects.get_answers_by_question(question_item)
    question_tags = QuestionTag.objects.get_tags_by_question(Question.objects.get(id=question_id))

    if request.method == 'GET':
        answer_form = AnswerForm()
    if request.method == 'POST':
        answer_form = AnswerForm(request.POST)
        if answer_form.is_valid():
            content = answer_form.cleaned_data['content']
            user = request.user
            if user.is_authenticated:
                Answer.objects.create(content=content, question=question_item, author=user)
            else:
                answer_form.add_error(None, 'Login first')
            

    return handle_pagination(request, answers, 'question.html', {'answers_count': len(answers), 'question': question_item, 'question_reactions': question_reactions, 'question_tags': question_tags, 'form': answer_form})

def log_in(request):
    if request.method == 'GET':
        login_form = LoginForm()
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user = authenticate(request, **login_form.cleaned_data)
            if user is not None:
                login(request, user)
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
                    return redirect(reverse('index'))
                else:
                    user_form.add_error(None, 'An error occured while creating new account!')
            except:
                user_form.add_error(None, 'Username is already taken')
    return render(request, 'signup.html', {'form': user_form})

def log_out(request):
    logout(request)
    return redirect_to_previous(request)

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
        edit_profile_form = EditProfileForm(initial={'username': request.user.username, 'email': request.user.email})
    if request.method == 'POST':
        edit_profile_form = EditProfileForm(request.POST, initial={'username': request.user.username, 'email': request.user.email})
        if edit_profile_form.is_valid():
            user = request.user
            new_username = edit_profile_form.cleaned_data['username']
            new_password = edit_profile_form.cleaned_data['password']
            new_email = edit_profile_form.cleaned_data['email']
            old_password = edit_profile_form.cleaned_data['old_password']
    
            if user.check_password(old_password):
                if new_username and new_username != user.username:
                    user.username = new_username
                if new_email and new_email != user.email:
                    user.email = new_email
                if new_password and not (user.check_password(new_password)):
                    user.set_password(new_password)
                user.save()
                messages.success(request, 'Your account has been updated successfully.')
            else:
                edit_profile_form.add_error(None, 'Your wrote incorrect password')

    return render(request, 'settings.html', {'form': edit_profile_form})

def not_found(request):
    return render(request, 'not-found.html')