import importlib
import inspect
from django.db import models
from django.core.exceptions import ValidationError
from datetime import datetime, time
from django.utils import timezone

# from properties.models.property import Property
import random
#
# def get_property_instance(obj):
#     if obj:
#         if obj.property:
#             property_obj = Property.objects.filter(pk=obj.property.id).first()
#             if property_obj:
#                 return property_obj
#     raise ValidationError({"property": "Property does not exist"})
#

def get_models_from_files(app_name, files):
    """
    Get all model classes defined in the specified files.
    :param app_name: name of the app
    :param files: List of file paths (relative to the models folder) without `.py` extension.
                  Example: ["file1", "file2"]
    :return: Dictionary with file names as keys and a list of model classes as values.
    """
    model_list = []
    for file in files:
        try:
            # Dynamically import the module
            module = importlib.import_module(f"{app_name}.models.{file}")

            # Retrieve all classes in the module that inherit from models.Model
            file_models = [
                member for name, member in inspect.getmembers(module, inspect.isclass)
                if issubclass(member, models.Model) and member._meta.app_label == app_name
            ]

            model_list.extend(file_models)
        except ModuleNotFoundError as e:
            print(f"Module {file} not found: {e}")
        except Exception as e:
            print(f"Error processing {file}: {e}")

    return model_list

def calculate_seconds_until_end_of_day():
    now = timezone.now()
    # Create a timezone-aware datetime for the end of the day
    end_of_day = timezone.make_aware(
        datetime.combine(now.date(), time(23, 59, 59)),
        timezone=now.tzinfo  # Use the same timezone as 'now'
    )
    time_difference = end_of_day - now
    return int(time_difference.total_seconds())

def generate_otp():
    return random.randint(100000, 999999)

def convert_to_bool(value):
    if value:
        if value.lower() in ["yes", "true", "1", "True", 1, True]:
            return True
        elif value.lower() in ["no", "false", "0", "False", 0, False]:
            return False
    return False

