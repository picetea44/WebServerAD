from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views import View
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse

from ..forms import AnswerForm
from ..models import Question, Answer
from ..services.answer_service import AnswerService
from ..services.question_service import QuestionService
from common.exceptions import ResourceNotFoundException, PermissionDeniedException


@method_decorator(login_required(login_url='common:login'), name='dispatch')
class AnswerCreateView(View):
    """
    pybo 답변등록 뷰
    """
    def post(self, request, question_id):
        try:
            # 서비스 레이어를 통해 질문 조회
            question = QuestionService.get_question(question_id)

            form = AnswerForm(request.POST)
            if form.is_valid():
                # 서비스 레이어를 통해 답변 생성
                answer = AnswerService.create_answer(
                    question_id=question_id,
                    content=form.cleaned_data['content'],
                    user=request.user
                )
                return redirect('pybo:detail', question_id=question_id)
        except ResourceNotFoundException:
            question = get_object_or_404(Question, pk=question_id)

        form = AnswerForm()
        context = {'question': question, 'form': form}
        return render(request, 'pybo/question_detail.html', context)

    def get(self, request, question_id):
        try:
            # 서비스 레이어를 통해 질문 조회
            question = QuestionService.get_question(question_id)
        except ResourceNotFoundException:
            question = get_object_or_404(Question, pk=question_id)

        form = AnswerForm()
        context = {'question': question, 'form': form}
        return render(request, 'pybo/question_detail.html', context)


@method_decorator(login_required(login_url='common:login'), name='dispatch')
class AnswerModifyView(View):
    """
    pybo 답변수정 뷰
    """
    template_name = 'pybo/answer_form.html'

    def get(self, request, answer_id):
        try:
            # 서비스 레이어를 통해 답변 조회
            answer = AnswerService.get_answer(answer_id)

            # 권한 확인
            if request.user != answer.author:
                messages.error(request, '수정권한이 없습니다')
                return redirect('pybo:detail', question_id=answer.question.id)

            form = AnswerForm(instance=answer)
            return render(request, self.template_name, {'answer': answer, 'form': form})
        except ResourceNotFoundException:
            return get_object_or_404(Answer, pk=answer_id)

    def post(self, request, answer_id):
        try:
            # 서비스 레이어를 통해 답변 수정
            try:
                answer = AnswerService.get_answer(answer_id)
                question_id = answer.question.id

                answer = AnswerService.modify_answer(
                    answer_id=answer_id,
                    content=request.POST.get('content'),
                    user=request.user
                )
                return redirect('pybo:detail', question_id=question_id)
            except PermissionDeniedException:
                answer = AnswerService.get_answer(answer_id)
                messages.error(request, '수정권한이 없습니다')
                return redirect('pybo:detail', question_id=answer.question.id)
        except ResourceNotFoundException:
            return get_object_or_404(Answer, pk=answer_id)


@method_decorator(login_required(login_url='common:login'), name='dispatch')
class AnswerDeleteView(View):
    """
    pybo 답변삭제 뷰
    """
    def get(self, request, answer_id):
        try:
            # 서비스 레이어를 통해 답변 조회 및 삭제
            try:
                answer = AnswerService.get_answer(answer_id)
                question_id = answer.question.id

                AnswerService.delete_answer(
                    answer_id=answer_id,
                    user=request.user
                )
            except PermissionDeniedException:
                answer = AnswerService.get_answer(answer_id)
                messages.error(request, '삭제권한이 없습니다')

            return redirect('pybo:detail', question_id=question_id)
        except ResourceNotFoundException:
            answer = get_object_or_404(Answer, pk=answer_id)
            if request.user != answer.author:
                messages.error(request, '삭제권한이 없습니다')
            else:
                answer.delete()
            return redirect('pybo:detail', question_id=answer.question.id)


# For backwards compatibility
@login_required(login_url='common:login')
def answer_create(request, question_id):
    """
    pybo 답변등록 (함수 기반 뷰 - 하위 호환성 유지)
    """
    view = AnswerCreateView.as_view()
    return view(request, question_id=question_id)


@login_required(login_url='common:login')
def answer_modify(request, answer_id):
    """
    pybo 답변수정 (함수 기반 뷰 - 하위 호환성 유지)
    """
    view = AnswerModifyView.as_view()
    return view(request, answer_id=answer_id)


@login_required(login_url='common:login')
def answer_delete(request, answer_id):
    """
    pybo 답변삭제 (함수 기반 뷰 - 하위 호환성 유지)
    """
    view = AnswerDeleteView.as_view()
    return view(request, answer_id=answer_id)
