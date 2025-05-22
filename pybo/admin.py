from django.contrib import admin
from .models import Question, Answer, Comment


class QuestionAdmin(admin.ModelAdmin):
    search_fields = ['subject', 'content']
    list_display = ['subject', 'author', 'create_date', 'modify_date']
    list_filter = ['create_date', 'modify_date']
    raw_id_fields = ['author', 'voter']


class AnswerAdmin(admin.ModelAdmin):
    search_fields = ['content']
    list_display = ['question', 'author', 'create_date', 'modify_date']
    list_filter = ['create_date', 'modify_date']
    raw_id_fields = ['author', 'question', 'voter']


class CommentAdmin(admin.ModelAdmin):
    search_fields = ['content']
    list_display = ['content', 'author', 'create_date', 'modify_date']
    list_filter = ['create_date', 'modify_date']
    raw_id_fields = ['author', 'question', 'answer']


admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(Comment, CommentAdmin)
