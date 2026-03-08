from django.contrib import admin

from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("file_name", "upload_date", "num_pages")
    search_fields = ("file_name", "extracted_text", "human_tags")
    list_filter = ("upload_date",)
    readonly_fields = ("upload_date", "num_pages", "extracted_text")

