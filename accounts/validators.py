from django.core.exceptions import ValidationError
import os


def allow_only_images_validator(value):

    valid_extensions = ['.png', '.jpg', '.jpeg']
    # Get file extension and convert to lowercase
    extension = os.path.splitext(value.name)[1].lower()
    if extension not in valid_extensions:
        # Improving the error message for accuracy
        raise ValidationError(
            f'Unsupported file extension. Allowed extensions: {", ".join(valid_extensions)}')
