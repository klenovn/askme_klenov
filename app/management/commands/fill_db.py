from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from faker import Faker
from django.db import transaction
import random
import string

from app.models import Tag, Answer, Like, Question, QuestionTag

Faker.seed(random.Random)
fake = Faker()


class Command(BaseCommand):
    help = "Fills database with fake data"

    def add_arguments(self, parser):
        parser.add_argument("num", type=int)

    def handle(self, *args, **kwargs):
        num = kwargs['num']
        fake_password = 'TestPass1234!'
        users = [User(
            username=(fake.simple_profile()['username']+fake.first_name()+fake.word()),
            email=fake.simple_profile()['mail']+str(i),
            password=fake_password
        ) for i in range(num)]

        User.objects.bulk_create(users)

        created_users = User.objects.all()
        tags=[Tag(word=(fake.words(nb=5, unique=True)[random.randint(-3, -1)].capitalize()+str(random.choice(string.ascii_letters))+str(random.choice(string.ascii_letters))+str(i))) for i in range(num)]
        Tag.objects.bulk_create(tags)

        questions = [Question(
                title=fake.sentence()[:-1]+'?',
                content=fake.paragraph(),
                author=random.choice(created_users),
                rating=random.randint(0, 10) * random.random()
            ) for i in range(10*num)]
        Question.objects.bulk_create(questions)

        
        answers = []
        for question in questions:
            for i in range(random.randint(0, 5)):
                answer = Answer(
                    content=fake.paragraph(),
                    author=random.choice(created_users),
                    question=question,
                    rating=random.randint(0, 10) * random.random()
                )
                answer.save()
                answers.append(answer)
        

        for i in range(100 * num):
            user = random.choice(created_users)
            like_type = random.choice(["question", "answer"])
            if like_type == "question":
                obj = random.choice(questions)
            else:
                obj = random.choice(answers)
            Like.objects.create(
                user=user,
                question=obj if like_type == "question" else None,
                answer=obj if like_type == "answer" else None,
                is_like=random.choice([True, False])
            )


            questionTags = []
            for question in questions:
                questionTags.extend([QuestionTag(question=question, tag=Tag.objects.order_by('?').first()) for i in range(random.randint(0, 3))])
            QuestionTag.objects.bulk_create(questionTags)
        self.stdout.write(self.style.SUCCESS(f'Successfully created {num} fake users'))

