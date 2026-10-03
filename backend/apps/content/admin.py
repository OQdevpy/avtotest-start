from django.contrib import admin

from .models import Answer, Category, Question, Stage, Variant, VariantQuestion


@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
    list_display = ["number", "title_uz"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["title_uz", "stage", "order"]
    list_filter = ["stage"]
    list_editable = ["order"]
    search_fields = ["title_uz", "title_ru", "title_kr"]


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 3
    fields = ["order", "text_uz", "text_kr", "text_ru", "is_correct"]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ["__str__", "category", "order", "is_published"]
    list_filter = ["category__stage", "category", "is_published"]
    search_fields = ["text_uz", "text_ru", "text_kr"]
    inlines = [AnswerInline]


class VariantQuestionInline(admin.TabularInline):
    model = VariantQuestion
    extra = 1
    autocomplete_fields = ["question"]


@admin.register(Variant)
class VariantAdmin(admin.ModelAdmin):
    list_display = ["__str__", "stage", "number"]
    list_filter = ["stage"]
    inlines = [VariantQuestionInline]
