from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView
from django.db.models import Q

from ..models import Question
from ..services.question_service import QuestionService
from common.exceptions import ResourceNotFoundException


class IndexView(ListView):
    """
    pybo 목록 출력 뷰
    """
    template_name = 'pybo/question_list.html'
    context_object_name = 'question_list'
    paginate_by = 9

    def get_queryset(self):
        # 검색어
        kw = self.request.GET.get('kw', '')  # 검색어

        # 검색어에 따른 질문 목록 조회 (페이지네이션은 ListView가 처리)
        if kw:
            question_list = Question.objects.filter(
                Q(subject__icontains=kw) |  # Subject contains keyword
                Q(content__icontains=kw) |  # Content contains keyword
                Q(author__username__icontains=kw) |  # Author username contains keyword
                Q(answer__content__icontains=kw)  # Answer content contains keyword
            ).distinct().order_by('-create_date')
        else:
            question_list = Question.objects.order_by('-create_date')

        # Debug: Print the number of questions
        print(f"Total questions: {question_list.count()}")

        return question_list

    def get_context_data(self, **kwargs):
        # 기본 컨텍스트 데이터 가져오기
        context = super().get_context_data(**kwargs)
        # 검색어 추가
        context['kw'] = self.request.GET.get('kw', '')

        # Debug: Print pagination info
        if 'page_obj' in context:
            print(f"Page {context['page_obj'].number} of {context['page_obj'].paginator.num_pages}")
            print(f"Has previous: {context['page_obj'].has_previous()}, Has next: {context['page_obj'].has_next()}")
            print(f"Page range: {list(context['page_obj'].paginator.page_range)}")
        else:
            print("No page_obj in context")

        return context


class DetailView(DetailView):
    """
    pybo 내용 출력 뷰
    """
    model = Question
    template_name = 'pybo/question_detail.html'
    context_object_name = 'question'
    pk_url_kwarg = 'question_id'

    def get_object(self, queryset=None):
        # 서비스 레이어를 통해 질문 조회
        try:
            return QuestionService.get_question(self.kwargs.get(self.pk_url_kwarg))
        except ResourceNotFoundException:
            # Django's get_object_or_404 equivalent
            return get_object_or_404(Question, pk=self.kwargs.get(self.pk_url_kwarg))


class SearchView(IndexView):
    """
    검색 결과 출력 뷰
    """
    template_name = 'pybo/search_results.html'

    def get_queryset(self):
        # 검색어
        kw = self.request.GET.get('kw', '')

        # 검색어가 없으면 빈 쿼리셋 반환
        if not kw:
            return Question.objects.none()

        # 검색어에 따른 질문 목록 조회
        question_list = Question.objects.filter(
            Q(subject__icontains=kw) |  # Subject contains keyword
            Q(content__icontains=kw) |  # Content contains keyword
            Q(author__username__icontains=kw) |  # Author username contains keyword
            Q(answer__content__icontains=kw)  # Answer content contains keyword
        ).distinct().order_by('-create_date')

        return question_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_search'] = True
        return context


# For backwards compatibility
def index(request):
    """
    pybo 목록 출력 (함수 기반 뷰 - 하위 호환성 유지)
    """
    view = IndexView.as_view()
    return view(request)


def detail(request, question_id):
    """
    pybo 내용 출력 (함수 기반 뷰 - 하위 호환성 유지)
    """
    view = DetailView.as_view()
    return view(request, question_id=question_id)


def search(request):
    """
    검색 결과 출력 (함수 기반 뷰)
    """
    view = SearchView.as_view()
    return view(request)
