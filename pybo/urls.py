from django.urls import path

from .views import base_views, question_views, answer_views, comment_views, vote_views
from .views.base_views import IndexView, DetailView, SearchView
from .views.question_views import QuestionCreateView, QuestionModifyView, QuestionDeleteView
from .views.answer_views import AnswerCreateView, AnswerModifyView, AnswerDeleteView
from .views.comment_views import (
    CommentCreateQuestionView, CommentModifyQuestionView, CommentDeleteQuestionView,
    CommentCreateAnswerView, CommentModifyAnswerView, CommentDeleteAnswerView
)

app_name = 'pybo'

urlpatterns = [
    # base_views.py
    path('', IndexView.as_view(), name='index'),
    path('<int:question_id>/', DetailView.as_view(), name='detail'),
    path('search/', SearchView.as_view(), name='search'),

    # question_views.py
    path('question/create/', QuestionCreateView.as_view(), name='question_create'),
    path('question/modify/<int:question_id>/', QuestionModifyView.as_view(), name='question_modify'),
    path('question/delete/<int:question_id>/', QuestionDeleteView.as_view(), name='question_delete'),

    # answer_views.py
    path('answer/create/<int:question_id>/', AnswerCreateView.as_view(), name='answer_create'),
    path('answer/modify/<int:answer_id>/', AnswerModifyView.as_view(), name='answer_modify'),
    path('answer/delete/<int:answer_id>/', AnswerDeleteView.as_view(), name='answer_delete'),

    # comment_views.py
    path('comment/create/question/<int:question_id>/', CommentCreateQuestionView.as_view(), name='comment_create_question'),
    path('comment/modify/question/<int:comment_id>/', CommentModifyQuestionView.as_view(), name='comment_modify_question'),
    path('comment/delete/question/<int:comment_id>/', CommentDeleteQuestionView.as_view(), name='comment_delete_question'),
    path('comment/create/answer/<int:answer_id>/', CommentCreateAnswerView.as_view(), name='comment_create_answer'),
    path('comment/modify/answer/<int:comment_id>/', CommentModifyAnswerView.as_view(), name='comment_modify_answer'),
    path('comment/delete/answer/<int:comment_id>/', CommentDeleteAnswerView.as_view(), name='comment_delete_answer'),

    # vote_views.py
    path('vote/question/<int:question_id>/', vote_views.vote_question, name='vote_question'),
    path('vote/answer/<int:answer_id>/', vote_views.vote_answer, name='vote_answer'),
]
