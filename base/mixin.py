import time
import uuid
from typing import Any
from django.db import models
from django.core.files.base import ContentFile


class DeepDeleteMixin:
    def remove_image_files(self, field):
        storage, path = field.storage, field.path
        storage.delete(path)

    def remove_m2m_objects(self, field):
        for obj in field.all():
            obj.delete()

    def delete(
        self, using: Any = None, keep_parents: bool = False
    ) -> tuple[int, dict[str, int]]:
        fields = self.__class__._meta.get_fields()

        for field in fields:
            if isinstance(field, models.ImageField):
                field = getattr(self, field.name)
                try:
                    self.remove_image_files(field)
                except:
                    pass
            elif isinstance(field, models.ManyToManyField):
                field = getattr(self, field.name)
                self.remove_m2m_objects(field)

        return super().delete(using, keep_parents)


class ImageHandlerMixin:

    def generate_image_name(self, storage, image_field, image_name):
        while True:
            timestamp = int(time.time())
            # Generate a unique identifier
            unique_id = uuid.uuid4()  # Short unique identifier

            # Extract the file extension and generate a candidate file name
            old_name = image_field.name
            original_ext = old_name.split('.')[-1]
            if image_name:
                new_name = f"{image_name}-{timestamp}-{unique_id}.{original_ext}"
            else:
                base_name = old_name.rsplit('/', 1)[-1].rsplit('.', 1)[0]
                new_name = f"{base_name}-{timestamp}-{unique_id}.{original_ext}"

            # Check if the new name already exists in storage
            if not storage.exists(new_name):
                return new_name

    def rename_image(self, image_field, image_name=None):
        """
        Rename the image file to include a timestamp before saving.
        :param image_field: A Django ImageField
        :param image_name: New name for the image.
        """
        if image_field and image_field.name:
            old_name = image_field.name
            storage = image_field.storage
            new_name = self.generate_image_name(storage, image_field, image_name)

            # Check if the file exists in storage, or fallback to image_field.file
            try:
                # Try reading the existing file from storage
                if storage.exists(old_name):
                    file_content = storage.open(old_name).read()
                else:
                    # If the file is in memory (not yet saved), read it directly
                    file_content = image_field.file.read()
            except Exception as e:
                raise ValueError(f"Unable to process file '{old_name}': {e}")

            # Save the file with the new name in storage
            new_name = storage.save(new_name, ContentFile(file_content))

            # Update the ImageField with the new name
            image_field.name = new_name

            # Delete the old file if it exists in storage and the names differ
            if old_name != new_name and storage.exists(old_name):
                storage.delete(old_name)
            storage.delete(new_name)

    def delete_image(self, image_field, image_name):
        """
        Deletes the image associated with the given ImageField.
        :param image_field: A Django ImageField
        :param image_name: name of the image
        """
        if image_field and image_field.name:
            image_field.storage.delete(image_name)
        # if image_name:
        #     storage = self._meta.get_field(image_field.field.attname).storage
        #     if storage.exists(image_name):
        #         storage.delete(image_name)