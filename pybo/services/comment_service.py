
from django.utils import timezone

from ..models import Question, Answer, Comment
from common.exceptions import ResourceNotFoundException, PermissionDeniedException


class CommentService:

    @staticmethod
    def create_question_comment(question_id, content, user):

        try:
            question = Question.objects.get(pk=question_id)
        except Question.DoesNotExist:
            raise ResourceNotFoundException(f"Question with ID {question_id} not found")
        
        comment = Comment(
            question=question,
            content=content,
            create_date=timezone.now(),
            author=user
        )
        comment.save()
        return comment

    @staticmethod
    def create_answer_comment(answer_id, content, user):

        try:
            answer = Answer.objects.get(pk=answer_id)
        except Answer.DoesNotExist:
            raise ResourceNotFoundException(f"Answer with ID {answer_id} not found")
        
        comment = Comment(
            answer=answer,
            content=content,
            create_date=timezone.now(),
            author=user
        )
        comment.save()
        return comment

    @staticmethod
    def get_comment(comment_id):

        try:
            return Comment.objects.get(pk=comment_id)
        except Comment.DoesNotExist:
            raise ResourceNotFoundException(f"Comment with ID {comment_id} not found")

    @staticmethod
    def modify_comment(comment_id, content, user):

        comment = CommentService.get_comment(comment_id)
        
        if comment.author != user:
            raise PermissionDeniedException("You are not the author of this comment")
        
        comment.content = content
        comment.modify_date = timezone.now()
        comment.save()
        return comment

    @staticmethod
    def delete_comment(comment_id, user):

        comment = CommentService.get_comment(comment_id)
        
        if comment.author != user:
            raise PermissionDeniedException("You are not the author of this comment")
        
        comment.delete()