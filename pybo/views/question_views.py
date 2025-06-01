from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views import View
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse

from ..forms import QuestionForm
from ..models import Question
from ..services.question_service import QuestionService
from common.exceptions import ResourceNotFoundException, PermissionDeniedException


@method_decorator(login_required(login_url='common:login'), name='dispatch')
class QuestionCreateView(CreateView):
    """
    pybo 질문등록 뷰
    """
    model = Question
    form_class = QuestionForm
    template_name = 'pybo/question_form.html'
    success_url = reverse_lazy('pybo:index')

    def form_valid(self, form):
        # 서비스 레이어를 통해 질문 생성
        question = QuestionService.create_question(
            subject=form.cleaned_data['subject'],
            content=form.cleaned_data['content'],
            user=self.request.user,
            image=form.cleaned_data.get('image')
        )
        return redirect(self.success_url)


@method_decorator(login_required(login_url='common:login'), name='dispatch')
class QuestionModifyView(View):
    """
    pybo 질문수정 뷰
    """
    template_name = 'pybo/question_form.html'

    def get(self, request, question_id):
        try:
            # 서비스 레이어를 통해 질문 조회
            question = QuestionService.get_question(question_id)

            # 권한 확인
            if request.user != question.author:
                messages.error(request, '수정권한이 없습니다')
                return redirect('pybo:detail', question_id=question.id)

            form = QuestionForm(instance=question)
            return render(request, self.template_name, {'form': form})
        except ResourceNotFoundException:
            return get_object_or_404(Question, pk=question_id)

    def post(self, request, question_id):
        try:
            # 서비스 레이어를 통해 질문 수정
            try:
                form = QuestionForm(request.POST, request.FILES, instance=QuestionService.get_question(question_id))
                if form.is_valid():
                    question = QuestionService.modify_question(
                        question_id=question_id,
                        subject=form.cleaned_data['subject'],
                        content=form.cleaned_data['content'],
                        user=request.user,
                        image=form.cleaned_data.get('image')
                    )
                    return redirect('pybo:detail', question_id=question.id)
                else:
                    return render(request, self.template_name, {'form': form})
            except PermissionDeniedException:
                messages.error(request, '수정권한이 없습니다')
                return redirect('pybo:detail', question_id=question_id)
        except ResourceNotFoundException:
            return get_object_or_404(Question, pk=question_id)


@method_decorator(login_required(login_url='common:login'), name='dispatch')
class QuestionDeleteView(View):
    """
    pybo 질문삭제 뷰
    """
    def get(self, request, question_id):
        try:
            # 서비스 레이어를 통해 질문 삭제
            try:
                QuestionService.delete_question(
                    question_id=question_id,
                    user=request.user
                )
                return redirect('pybo:index')
            except PermissionDeniedException:
                messages.error(request, '삭제권한이 없습니다')
                return redirect('pybo:detail', question_id=question_id)
        except ResourceNotFoundException:
            return get_object_or_404(Question, pk=question_id)


# For backwards compatibility
@login_required(login_url='common:login')
def question_create(request):
    """
    pybo 질문등록 (함수 기반 뷰 - 하위 호환성 유지)
    """
    view = QuestionCreateView.as_view()
    return view(request)


@login_required(login_url='common:login')
def question_modify(request, question_id):
    """
    pybo 질문수정 (함수 기반 뷰 - 하위 호환성 유지)
    """
    view = QuestionModifyView.as_view()
    return view(request, question_id=question_id)


@login_required(login_url='common:login')
def question_delete(request, question_id):
    """
    pybo 질문삭제 (함수 기반 뷰 - 하위 호환성 유지)
    """
    view = QuestionDeleteView.as_view()
    return view(request, question_id=question_id)

@login_required(login_url='common:login')
def question_create(request):
    """
    pybo 질문등록
    """
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.author = request.user  # 추가한 속성 author 적용
            question.create_date = timezone.now()
            question.save()
            return redirect('pybo:index')
    else:
        form = QuestionForm()
    context = {'form': form}
    return render(request, 'pybo/question_form.html', context)
