from django.db import models
from base.mixin import DeepDeleteMixin, ImageHandlerMixin


class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class InActivateManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=False)



class BaseModel(DeepDeleteMixin, ImageHandlerMixin, models.Model):

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    is_active = models.BooleanField(default=True)

    objects = models.Manager()
    active_objects = ActiveManager()
    inactive_objects = InActivateManager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """
        Override the save method to handle image changes, renaming, and deletion.
        """
        # Track old image paths
        old_images = {}
        if self.pk:  # If the object already exists
            try:
                existing_instance = self.__class__.objects.get(pk=self.pk)
                for field in self._meta.fields:
                    if isinstance(field, models.ImageField):
                        old_image_field = getattr(existing_instance, field.name)
                        old_images[field.attname] = (
                            old_image_field.name if old_image_field and old_image_field.name else None
                        )
            except self.__class__.DoesNotExist:
                pass  # Object does not exist yet

        # Process images before saving
        new_name = None
        if hasattr(self.__class__, "get_image_name"):
            new_name = getattr(self, "get_image_name")
        for field in self._meta.fields:
            if isinstance(field, models.ImageField):
                image_field = getattr(self, field.name)
                if image_field and image_field.name:  # A new image is uploaded
                    if field.name in old_images:
                        # Case 1: Image changed
                        if old_images[field.attname] != image_field.name:
                            # Delete the old image
                            if old_images[field.attname]:
                                self.delete_image(image_field, old_images[field.name])
                            # Rename the new image
                            self.rename_image(image_field, new_name)
                    else:
                        # Case 3: Image uploaded for the first time
                        self.rename_image(image_field, new_name)

                elif field.name in old_images:
                    # Case 2: Image not changed (keep as is)
                    setattr(self, field.name, old_images[field.name])

        super().save(*args, **kwargs)  # Save the instance

    def delete(self, *args, **kwargs):
        """
        Override the delete method to handle cleanup of related files such as images.
        """
        # Loop through all fields in the model
        for field in self._meta.fields:
            # Check if the field is an ImageField
            if isinstance(field, models.ImageField):
                image_field = getattr(self, field.name)  # Get the field's value (file object)
                if image_field and image_field.name:  # Check if an image exists
                    try:
                        # Delete the associated file using the ImageHandlerMixin method
                        self.delete_image(image_field, image_field.name)
                    except Exception as e:
                        print(f"Error deleting image '{image_field.name}': {e}")

        # Call the superclass delete method to delete the database record
        super().delete(*args, **kwargs)