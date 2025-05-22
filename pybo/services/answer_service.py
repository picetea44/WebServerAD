
from django.utils import timezone

from ..models import Question, Answer
from common.exceptions import ResourceNotFoundException, PermissionDeniedException


class AnswerService:

    @staticmethod
    def create_answer(question_id, content, user):

        try:
            question = Question.objects.get(pk=question_id)
        except Question.DoesNotExist:
            raise ResourceNotFoundException(f"Question with ID {question_id} not found")
        
        answer = Answer(
            question=question,
            content=content,
            create_date=timezone.now(),
            author=user
        )
        answer.save()
        return answer

    @staticmethod
    def get_answer(answer_id):

        try:
            return Answer.objects.get(pk=answer_id)
        except Answer.DoesNotExist:
            raise ResourceNotFoundException(f"Answer with ID {answer_id} not found")

    @staticmethod
    def modify_answer(answer_id, content, user):

        answer = AnswerService.get_answer(answer_id)
        
        if answer.author != user:
            raise PermissionDeniedException("You are not the author of this answer")
        
        answer.content = content
        answer.modify_date = timezone.now()
        answer.save()
        return answer

    @staticmethod
    def delete_answer(answer_id, user):

        answer = AnswerService.get_answer(answer_id)
        
        if answer.author != user:
            raise PermissionDeniedException("You are not the author of this answer")
        
        answer.delete()

    @staticmethod
    def vote_answer(answer_id, user):

        answer = AnswerService.get_answer(answer_id)
        answer.voter.add(user)
        return answer