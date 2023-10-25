from django.core.exceptions import ValidationError
import os


def allow_only_images_validator(value):
    extension = os.path.splitext(value.name)[1]  # [0] coverimage. [1]jpg
    print(extension)
    valid_extensions = ['.png', '.jpg', '.jpeg']
    if not extension.lower() in valid_extensions:
        raise ValidationError(
            'Unsuppoerted file extension. Allowed extension: ' + str(valid_extensions))
