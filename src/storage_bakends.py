from storages.backends.s3boto3 import S3Boto3Storage

class MediaStorage(S3Boto3Storage):
    location = 'media'
    #default_acl = 'public-read'
    #default_acl = 'private'
    default_acl = 'bucket-owner-full-control'
    file_overwrite = False
    custom_domain = False

# https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-presigned-urls.html
# https://stackoverflow.com/questions/42185682/django-move-all-previously-uploaded-media-files-to-new-location-and-rename
    
