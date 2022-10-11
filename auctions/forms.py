from django import forms
from .models import Auction, Bid, Comment


class AuctionForm(forms.ModelForm):
    class Meta:
        model = Auction
        fields = ['title', 'description', 'starting_bid', 'image', 'category']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Enter name', 'class': "form-control"}),
            'description': forms.Textarea(attrs={'placeholder': 'Enter description', 'class': "form-control", 'rows': 5}),
            'starting_bid': forms.NumberInput(attrs={'placeholder': 'Enter price', 'class': "form-control"}),
            # 'image': forms.TextInput(attrs={'placeholder': 'Enter image URL', 'class': "form-control"}),
            'category': forms.Select(attrs={'class': "form-select"})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].empty_label = 'not selected'


class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['amount']
        widgets = {
            'amount': forms.NumberInput(attrs={'placeholder': 'Enter bid', 'class': "form-control"},),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']
        widgets = {
            'comment': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Add a comment',
            })
        }

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['comment'].label = ''
        self.visible_fields()[0].field.widget.attrs['class'] = 'form-control w-75 h-75'