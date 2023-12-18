from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from faker import Faker
from english_words import get_english_words_set
import random

from app.models import Tag, Answer, QuestionReaction, Question, QuestionTag, AnswerReaction

Faker.seed(random.Random)
fake = Faker()


class Command(BaseCommand):
    help = "Fills database with fake data"

    def add_arguments(self, parser):
        parser.add_argument("num", type=int)

    def handle(self, *args, **kwargs):
        print("Started")


        num = kwargs['num']
        fake_password = 'TestPass1234!'
        words = list(get_english_words_set(['web2'], lower=True))[::10]

        usernames = list(set([fake.simple_profile()['username'] for _ in range(num)]))
        users = [User(
            username=i,
            email=str(i) + "@fakemail.com",
            password=fake_password
        ) for i in usernames]
        User.objects.bulk_create(users)
        print("Created users")

        tags=[Tag(word=word) for word in words]
        Tag.objects.bulk_create(tags)
        print("Created tags")

        authors = User.objects.order_by('?')
        questions = [Question(title=fake.sentence()[:-1]+'?', content=fake.paragraph(), author=authors[i]) for _ in range(random.randint(0, 24)) for i in range(len(authors))]
        Question.objects.bulk_create(questions)
        print("Created question")

        def new_answer(content, author, question, i):
            if i % 100 == 0:
                print(i)
            return Answer(content=content, author=author, question=question)
        users_number = User.objects.all().count()
        questions = Question.objects.all()
        answers = [new_answer(content=fake.paragraph(), author=User.objects.get(id=random.randint(2, users_number - 1)), question=questions[i], i=i) for i in range(2, len(questions)-1) for _ in range(random.randint(0, 16))]
        Answer.objects.bulk_create(answers)

        tags = Tag.objects.all()
        questions = Question.objects.all()
        questionTags = [QuestionTag(question=question, tag=random.choice(tags)) for _ in range(1, 5) for question in questions]
        QuestionTag.objects.bulk_create(questionTags)
        print("Added tags to questions")

        questions = Question.objects.all()
        users = User.objects.all()
        question_reactions = [QuestionReaction(
            question=question,
            user=random.choice(users),
            type=random.choice(['Like', 'Like', 'Like', 'Like', 'Dislike'])
        ) for question in questions for _ in range(random.randint(0, 15))]
        QuestionReaction.objects.bulk_create(question_reactions)
        print("Created question reactions")

        answers = Answer.objects.all()
        users = User.objects.all()
        answer_reactions = [AnswerReaction(
            answer=answer,
            user=random.choice(users),
            type=random.choice(['Like', 'Like', 'Like', 'Like', 'Dislike'])
        ) for answer in answers for _ in range(random.choice([0, 0, 0, 1, 2, 3]))]
        AnswerReaction.objects.bulk_create(answer_reactions)
        print("Created answer reactions")

        self.stdout.write(self.style.SUCCESS(f'Successfully created {num} fake users'))

