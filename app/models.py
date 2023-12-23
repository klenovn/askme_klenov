from django.db import models
from django.contrib.auth.models import User
from django.db.models import F, ExpressionWrapper, fields


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(default='avatars/user_avatar_placeholder.jpeg', upload_to='avatars/', null=True, blank=True)
    registration_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Tag(models.Model):
    word = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.word


class QuestionManager(models.Manager):
    def get_best_questions(self):
        annotated_qs = self.annotate(
            like_count=models.Count('questionreaction', filter=models.Q(questionreaction__type='Like')),
            dislike_count=models.Count('questionreaction', filter=models.Q(questionreaction__type='Dislike'))
        )

        annotated_qs = annotated_qs.annotate(
            popularity=ExpressionWrapper(
                F('like_count') - F('dislike_count'),
                output_field=fields.IntegerField()
            )
        )

        sorted_qs = annotated_qs.order_by('-popularity')

        return sorted_qs

    def get_newest_questions(self):
        return self.order_by('-created_at')
    

class Question(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = QuestionManager()

    def __str__(self):
        return self.title
    

class AnswerManager(models.Manager):

    def count_answers(self, question):
        return self.filter(question=question).count()
    
    def get_answers_by_question(self, question):
        answers = self.filter(question=question)

        return answers
      

class Answer(models.Model):
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"Answer to '{self.question.title}'"
    
    objects = AnswerManager()


class Reaction(models.Model):
    TYPE_CHOICES = [
        ('Like', 'Like'),
        ('Dislike', 'Dislike')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f"Reaction by {self.user.username} on {self.question.title if self.question else self.answer.question.title}"


class QuestionReactionManager(models.Manager):

    def get_reactions(self, question_id):
        return self.filter(question=Question.objects.get(id=question_id), type='Like').count() - self.filter(question=Question.objects.get(id=question_id), type='Dislike').count()
    
    def toggle_reaction(self, user, question, type):
        if type == 'Like':
            neg_type = 'Dislike'
        elif type == 'Dislike':
            neg_type = 'Like'

        if self.filter(user=user, question=question, type=type).exists():
            self.filter(user=user, question=question, type=type).delete()
        elif self.filter(user=user, question=question, type=neg_type).exists():
            self.filter(user=user, question=question, type=neg_type).delete()
            self.create(user=user, question=question, type=type)
        else:
            self.create(user=user, question=question, type=type)

    
class QuestionReaction(Reaction):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    objects = QuestionReactionManager()


class AnswerReactionManager(models.Manager):

    def get_reactions(self, answer_id):
        return self.filter(answer=Answer.objects.get(id=answer_id), type='Like').count() - self.filter(answer=Answer.objects.get(id=answer_id), type='Dislike').count()
    
    def toggle_reaction(self, user, answer, type):
        if type == 'Like':
            neg_type = 'Dislike'
        elif type == 'Dislike':
            neg_type = 'Like'

        if self.filter(user=user, answer=answer, type=type).exists():
            self.filter(user=user, answer=answer, type=type).delete()
        elif self.filter(user=user, answer=answer, type=neg_type).exists():
            self.filter(user=user, answer=answer, type=neg_type).delete()
            self.create(user=user, answer=answer, type=type)
        else:
            self.create(user=user, answer=answer, type=type)
    

class AnswerReaction(Reaction):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)

    objects = AnswerReactionManager()


class QuestionTagManager(models.Manager):

    def get_tags_by_question(self, question):
        return [elem.tag.word for elem in self.filter(question=question)]
    
    def get_question_by_tag_name(self, tag_name):
        try:
            tag = Tag.objects.get(word=tag_name)
            return [elem.question for elem in self.filter(tag=tag)]
        except Tag.DoesNotExist:
            return []
    

class QuestionTag(models.Model):
    question = question = models.ForeignKey(Question, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    objects = QuestionTagManager()