from django.forms import ModelForm
from forum.models import Post, Forum
from django.utils.html import strip_tags

class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ["message"]
        
    def clean_message(self):
        message = self.cleaned_data["message"]
        return strip_tags(message)
    
class ForumForm(ModelForm):
    class Meta:
        model = Forum
        fields = ["nama"]
    
    def clean_nama(self):
        nama = self.cleaned_data["nama"]
        return strip_tags(nama)