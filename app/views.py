from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage
from .models import Question, QuestionTag

PER_PAGE = 6

questions = []
answers = []
for i in range(1, 300):
    questions.append({
        'title': 'Title ' + str(i),
        'id': i,
        'text': 'Text ' + str(i)
    })
    answers.append({
        'title': 'Title ' + str(i),
        'id': i,
        'text': 'Text ' + str(i)
    })

def get_page_or_one(request):
    page_number = request.GET.get('page')
    if page_number == None: page_number = 1
    return page_number

def paginate(objects, page, per_page=PER_PAGE):
    paginator = Paginator(objects, per_page)

    return paginator.page(page)

def get_number_of_pages(objects, per_page=PER_PAGE):
    paginator = Paginator(objects, per_page)
    number_of_pages = paginator.num_pages

    return number_of_pages

def get_tags_per_page(page):
    tags_per_question = []
    for question in page:
        tags_per_question.append(QuestionTag.objects.get_tags_by_question(question))
    return tags_per_question

def index(request):
    questions = Question.objects.get_newest_questions()
    page_number = get_page_or_one(request)

    try:
        page = paginate(questions, page_number)
        number_of_pages = get_number_of_pages(questions)
    except:
        return redirect('not_found')
    
    context = {'page': page, 'number_of_pages': number_of_pages, 'questions_count': len(questions)}
    print(page)
    return render(request, 'index.html', context)


def question(request, question_id):
    page_number = get_page_or_one(request)
    questions = Question.objects.get_newest_questions()
    question_item = questions[question_id]
    try:
        page = paginate(answers, page_number)
        number_of_pages = get_number_of_pages(answers)
    except:
        return redirect('not_found')

    context = {'question': question_item, 'page': page, 'number_of_pages': number_of_pages, }

    return render(request, 'question.html', context)

def login(request):
    return render(request, 'login.html')

def signup(request):
    return render(request, 'signup.html')

def ask(request):
    return render(request, 'ask.html')

def hot(request):
    questions = Question.objects.get_best_questions()

    page_number = get_page_or_one(request)

    try:
        page = paginate(questions, page_number)
        number_of_pages = get_number_of_pages(questions)
    except:
        return redirect('not_found')
    
    context = {'page': page, 'number_of_pages': number_of_pages, 'questions_count': len(questions)}
    print(page)
    return render(request, 'index.html', context)

def tag(request, tag_name):
    page_number = get_page_or_one(request)

    try:
        page = paginate(questions, page_number)
        number_of_pages = get_number_of_pages(questions)
    except:
        return redirect('not_found')
    
    context = {'page': page, 'number_of_pages': number_of_pages, 'questions_count': len(questions), 'tag': tag_name}
    print(page)
    return render(request, 'tag.html', context)

def not_found(request):
    return render(request, 'not-found.html')