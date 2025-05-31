from django.contrib import admin
from django.conf import settings
from django.apps import apps
from django.db import models


# Register your models here.

custom_apps = settings.CUSTOM_APPS

for app in custom_apps:
    app_name = app.split('.')[-1]
    app_models = apps.all_models[app_name]
    for model_name, model_class in app_models.items():
        exclude_list = ["slug", "group", "permission"]
        filter_set = ['name', "title", 'full_name']
        exclude_list.extend(field.name for field in model_class._meta.fields if isinstance(field, models.ImageField))
        # if model_class == User:  # Check if the model is User
        #     exclude_list.extend(['password'])
        try:
            @admin.register(model_class)
            class ModelClassAdmin(admin.ModelAdmin):
                list_display = ['id'] + [field.name for field in model_class._meta.fields if
                                         field.name not in exclude_list and field.name != 'id']
                search_fields = [field.name for field in model_class._meta.fields if field.name in filter_set]
                list_filter = [field.name for field in model_class._meta.fields if field.name in filter_set]
                list_display_links = ['id']  # Display links will use 'id'
                readonly_fields = []
                # if model_class == User:  # Check if the model is User
                #     readonly_fields.extend(['password'])

                # Set ordering based on existence of fields
                ordering = ['-date_joined'] if 'date_joined' in [field.name for field in
                                                                 model_class._meta.fields] else [
                    '-created_at'] if 'created_at' in [field.name for field in model_class._meta.fields] else ['id']

        except admin.sites.AlreadyRegistered:
            pass