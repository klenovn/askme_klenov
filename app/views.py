from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage
from .models import Question, QuestionTag, Answer

PER_PAGE = 6

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
        number_of_pages = pagination['number_of_pages']
        if need_tags:
            tags = get_tags_per_page(page)
            items_with_tags = tuple(zip(page, tags))
            context['items_with_tags'] = items_with_tags
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
    questions = Question.objects.get_newest_questions()
    question_item = questions[question_id - 1]
    answers = Answer.objects.get_answers_by_question(question_item)

    return handle_pagination(request, answers, 'question.html', {'answers_count': len(answers), 'question': question_item})

def login(request):
    return render(request, 'login.html')

def signup(request):
    return render(request, 'signup.html')

def ask(request):
    return render(request, 'ask.html')

def settings(request):
    return render(request, 'settings.html')

def not_found(request):
    return render(request, 'not-found.html')