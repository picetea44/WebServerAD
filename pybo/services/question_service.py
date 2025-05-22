from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Q

from ..models import Question
from common.exceptions import ResourceNotFoundException, PermissionDeniedException


class QuestionService:

    @staticmethod
    def get_question_list(page=1, kw=''):

        if kw:
            question_list = Question.objects.filter(
                Q(subject__icontains=kw) |  # Subject contains keyword
                Q(content__icontains=kw) |  # Content contains keyword
                Q(author__username__icontains=kw) |  # Author username contains keyword
                Q(answer__content__icontains=kw)  # Answer content contains keyword
            ).distinct().order_by('-create_date')
        else:
            question_list = Question.objects.order_by('-create_date')

        # Apply pagination
        paginator = Paginator(question_list, 10, orphans=3)  # 10 items per page, combine last page if it has 3 or fewer items
        page_obj = paginator.get_page(page)

        # Log pagination info for debugging
        print(f"Page {page} of {paginator.num_pages}, {len(page_obj.object_list)} items")

        return page_obj

    @staticmethod
    def get_question(question_id):
        try:
            return Question.objects.get(pk=question_id)
        except Question.DoesNotExist:
            raise ResourceNotFoundException(f"Question with ID {question_id} not found")

    @staticmethod
    def create_question(subject, content, user, image=None):
        question = Question(
            subject=subject,
            content=content,
            create_date=timezone.now(),
            author=user,
            image=image
        )
        question.save()
        return question

    @staticmethod
    def modify_question(question_id, subject, content, user, image=None):

        question = QuestionService.get_question(question_id)

        if question.author != user:
            raise PermissionDeniedException("You are not the author of this question")

        question.subject = subject
        question.content = content
        if image is not None:
            question.image = image
        question.modify_date = timezone.now()
        question.save()
        return question

    @staticmethod
    def delete_question(question_id, user):

        question = QuestionService.get_question(question_id)

        if question.author != user:
            raise PermissionDeniedException("You are not the author of this question")

        question.delete()

    @staticmethod
    def vote_question(question_id, user):

        question = QuestionService.get_question(question_id)
        question.voter.add(user)
        return question
