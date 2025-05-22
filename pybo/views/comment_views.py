from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views import View
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse

from ..forms import CommentForm
from ..models import Question, Answer, Comment
from ..services.comment_service import CommentService
from ..services.question_service import QuestionService
from ..services.answer_service import AnswerService
from common.exceptions import ResourceNotFoundException, PermissionDeniedException


@method_decorator(login_required(login_url='common:login'), name='dispatch')
class CommentCreateQuestionView(View):
    """
    pybo 질문댓글등록 뷰
    """
    template_name = 'pybo/comment_form.html'

    def get(self, request, question_id):
        form = CommentForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, question_id):
        form = CommentForm(request.POST)
        if form.is_valid():
            try:
                # 서비스 레이어를 통해 댓글 생성
                comment = CommentService.create_question_comment(
                    question_id=question_id,
                    content=form.cleaned_data['content'],
                    user=request.user
                )
                return redirect('pybo:detail', question_id=question_id)
            except ResourceNotFoundException:
                # 질문이 존재하지 않는 경우
                question = get_object_or_404(Question, pk=question_id)

                # 기존 방식으로 댓글 생성
                comment = form.save(commit=False)
                comment.author = request.user
                comment.create_date = timezone.now()
                comment.question = question
                comment.save()
                return redirect('pybo:detail', question_id=question.id)

        return render(request, self.template_name, {'form': form})


@method_decorator(login_required(login_url='common:login'), name='dispatch')
class CommentModifyQuestionView(View):
    """
    pybo 질문댓글수정 뷰
    """
    template_name = 'pybo/comment_form.html'

    def get(self, request, comment_id):
        try:
            # 서비스 레이어를 통해 댓글 조회
            comment = CommentService.get_comment(comment_id)

            # 권한 확인
            if request.user != comment.author:
                messages.error(request, '댓글수정권한이 없습니다')
                return redirect('pybo:detail', question_id=comment.question.id)

            form = CommentForm(instance=comment)
            return render(request, self.template_name, {'form': form})
        except ResourceNotFoundException:
            return get_object_or_404(Comment, pk=comment_id)

    def post(self, request, comment_id):
        try:
            # 서비스 레이어를 통해 댓글 수정
            try:
                comment = CommentService.get_comment(comment_id)
                question_id = comment.question.id

                comment = CommentService.modify_comment(
                    comment_id=comment_id,
                    content=request.POST.get('content'),
                    user=request.user
                )
                return redirect('pybo:detail', question_id=question_id)
            except PermissionDeniedException:
                comment = CommentService.get_comment(comment_id)
                messages.error(request, '댓글수정권한이 없습니다')
                return redirect('pybo:detail', question_id=comment.question.id)
        except ResourceNotFoundException:
            return get_object_or_404(Comment, pk=comment_id)


@method_decorator(login_required(login_url='common:login'), name='dispatch')
class CommentDeleteQuestionView(View):
    """
    pybo 질문댓글삭제 뷰
    """
    def get(self, request, comment_id):
        try:
            # 서비스 레이어를 통해 댓글 조회 및 삭제
            try:
                comment = CommentService.get_comment(comment_id)
                question_id = comment.question.id

                CommentService.delete_comment(
                    comment_id=comment_id,
                    user=request.user
                )
                return redirect('pybo:detail', question_id=question_id)
            except PermissionDeniedException:
                comment = CommentService.get_comment(comment_id)
                messages.error(request, '댓글삭제권한이 없습니다')
                return redirect('pybo:detail', question_id=comment.question.id)
        except ResourceNotFoundException:
            comment = get_object_or_404(Comment, pk=comment_id)
            if request.user != comment.author:
                messages.error(request, '댓글삭제권한이 없습니다')
                return redirect('pybo:detail', question_id=comment.question_id)
            else:
                comment.delete()
                return redirect('pybo:detail', question_id=comment.question_id)


@method_decorator(login_required(login_url='common:login'), name='dispatch')
class CommentCreateAnswerView(View):
    """
    pybo 답글댓글등록 뷰
    """
    template_name = 'pybo/comment_form.html'

    def get(self, request, answer_id):
        form = CommentForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, answer_id):
        form = CommentForm(request.POST)
        if form.is_valid():
            try:
                # 서비스 레이어를 통해 댓글 생성
                comment = CommentService.create_answer_comment(
                    answer_id=answer_id,
                    content=form.cleaned_data['content'],
                    user=request.user
                )

                # 답변의 질문 ID 조회
                answer = AnswerService.get_answer(answer_id)
                return redirect('pybo:detail', question_id=answer.question.id)
            except ResourceNotFoundException:
                # 답변이 존재하지 않는 경우
                answer = get_object_or_404(Answer, pk=answer_id)

                # 기존 방식으로 댓글 생성
                comment = form.save(commit=False)
                comment.author = request.user
                comment.create_date = timezone.now()
                comment.answer = answer
                comment.save()
                return redirect('pybo:detail', question_id=answer.question.id)

        return render(request, self.template_name, {'form': form})


@method_decorator(login_required(login_url='common:login'), name='dispatch')
class CommentModifyAnswerView(View):
    """
    pybo 답글댓글수정 뷰
    """
    template_name = 'pybo/comment_form.html'

    def get(self, request, comment_id):
        try:
            # 서비스 레이어를 통해 댓글 조회
            comment = CommentService.get_comment(comment_id)

            # 권한 확인
            if request.user != comment.author:
                messages.error(request, '댓글수정권한이 없습니다')
                return redirect('pybo:detail', question_id=comment.answer.question.id)

            form = CommentForm(instance=comment)
            return render(request, self.template_name, {'form': form})
        except ResourceNotFoundException:
            return get_object_or_404(Comment, pk=comment_id)

    def post(self, request, comment_id):
        try:
            # 서비스 레이어를 통해 댓글 수정
            try:
                comment = CommentService.get_comment(comment_id)
                question_id = comment.answer.question.id

                comment = CommentService.modify_comment(
                    comment_id=comment_id,
                    content=request.POST.get('content'),
                    user=request.user
                )
                return redirect('pybo:detail', question_id=question_id)
            except PermissionDeniedException:
                comment = CommentService.get_comment(comment_id)
                messages.error(request, '댓글수정권한이 없습니다')
                return redirect('pybo:detail', question_id=comment.answer.question.id)
        except ResourceNotFoundException:
            return get_object_or_404(Comment, pk=comment_id)


@method_decorator(login_required(login_url='common:login'), name='dispatch')
class CommentDeleteAnswerView(View):
    """
    pybo 답글댓글삭제 뷰
    """
    def get(self, request, comment_id):
        try:
            # 서비스 레이어를 통해 댓글 조회 및 삭제
            try:
                comment = CommentService.get_comment(comment_id)
                question_id = comment.answer.question.id

                CommentService.delete_comment(
                    comment_id=comment_id,
                    user=request.user
                )
                return redirect('pybo:detail', question_id=question_id)
            except PermissionDeniedException:
                comment = CommentService.get_comment(comment_id)
                messages.error(request, '댓글삭제권한이 없습니다')
                return redirect('pybo:detail', question_id=comment.answer.question.id)
        except ResourceNotFoundException:
            comment = get_object_or_404(Comment, pk=comment_id)
            if request.user != comment.author:
                messages.error(request, '댓글삭제권한이 없습니다')
                return redirect('pybo:detail', question_id=comment.answer.question.id)
            else:
                comment.delete()
                return redirect('pybo:detail', question_id=comment.answer.question.id)


# For backwards compatibility
@login_required(login_url='common:login')
def comment_create_question(request, question_id):
    """
    pybo 질문댓글등록 (함수 기반 뷰 - 하위 호환성 유지)
    """
    view = CommentCreateQuestionView.as_view()
    return view(request, question_id=question_id)


@login_required(login_url='common:login')
def comment_modify_question(request, comment_id):
    """
    pybo 질문댓글수정 (함수 기반 뷰 - 하위 호환성 유지)
    """
    view = CommentModifyQuestionView.as_view()
    return view(request, comment_id=comment_id)


@login_required(login_url='common:login')
def comment_delete_question(request, comment_id):
    """
    pybo 질문댓글삭제 (함수 기반 뷰 - 하위 호환성 유지)
    """
    view = CommentDeleteQuestionView.as_view()
    return view(request, comment_id=comment_id)


@login_required(login_url='common:login')
def comment_create_answer(request, answer_id):
    """
    pybo 답글댓글등록 (함수 기반 뷰 - 하위 호환성 유지)
    """
    view = CommentCreateAnswerView.as_view()
    return view(request, answer_id=answer_id)


@login_required(login_url='common:login')
def comment_modify_answer(request, comment_id):
    """
    pybo 답글댓글수정 (함수 기반 뷰 - 하위 호환성 유지)
    """
    view = CommentModifyAnswerView.as_view()
    return view(request, comment_id=comment_id)


@login_required(login_url='common:login')
def comment_delete_answer(request, comment_id):
    """
    pybo 답글댓글삭제 (함수 기반 뷰 - 하위 호환성 유지)
    """
    view = CommentDeleteAnswerView.as_view()
    return view(request, comment_id=comment_id)
