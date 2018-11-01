from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = (
            'title',
            'photo',
            'ingredient',
            'recipe_list'
        )
        widgets = {
            'ingredient' : forms.Textarea(
                attrs={
                    'class' : 'ingredient',
                    'placeholder' : '''요리 재료를 입력해주세요...

ex) 1. 버터,올리브오일
        2. 스파게티 면''',
                }
            ),
            'recipe_list' : forms.Textarea(
                attrs = {
                    'class' : 'recipe_list',
                    'placeholder' : '''요리 조리법을 입력해주세요...

ex) 1. 쌀을 씻는다.
        2. 물을 끓인다.''',
                }
            )
        }



class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = (
            'content',
        )
        widgets = {
            'content': forms.TextInput(
                attrs={
                    'class': 'content',
                    'placeholder': '댓글 달기...',
                }
            )
        }

    def clean_content(self):
        data = self.cleaned_data['content']
        errors = []
        if data == '':
            errors.append(forms.ValidationError('댓글 내용을 입력해주세요'))
        elif len(data) > 50:
            errors.append(forms.ValidationError('댓글 내용은 50자 이하로 입력해주세요'))
        if errors:
            raise forms.ValidationError(errors)
        return data
