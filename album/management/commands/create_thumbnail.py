from album.models import Photo

def run(verbose=True):
    """
    Create thumbnails. 
    """
    
    photos = Photo.objects.all()
    
    for img in photos:
        print(img.image)
        img.thumbnail = img.image 
        img.save()