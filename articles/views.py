from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views import View  
from django.views.generic import ListView, DetailView, FormView  
from django.views.generic.detail import SingleObjectMixin  
from django.views.generic.edit import UpdateView, DeleteView, CreateView
from django.urls import reverse_lazy
from django.urls import reverse_lazy, reverse  
from .forms import CommentForm
from .models import Article

import random # new
from django.http import HttpResponseRedirect # new
from django.contrib import messages # new

class CommentGet(DetailView): 
    model = Article
    template_name = "article_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Generate and store captcha in the session
        captcha_number = random.randint(1000, 9999) # new
        self.request.session['captcha'] = captcha_number # new
        # Include the captcha number in the context
        context["form"] = CommentForm()
        context["captcha_number"] = captcha_number # new
        return context


class CommentPost(SingleObjectMixin, FormView):  
    model = Article
    form_class = CommentForm
    template_name = "article_detail.html"

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        # Check captcha
        entered_captcha = form.cleaned_data['captcha']  # new
        stored_captcha = self.request.session.get('captcha', '')  # new

        # Convert stored_captcha to string for comparison
        #print('entered_captcha',entered_captcha)
        #print('stored_captcha',stored_captcha)
        #print (entered_captcha == stored_captcha)
        if entered_captcha == stored_captcha: # new
            comment = form.save(commit=False)
            comment.article = self.object
            comment.author = self.request.user
            comment.save()
            # Clear the captcha from the session
            self.request.session['captcha'] = None # new
            messages.success(self.request, 'Comment submitted successfully!') # new
            return super().form_valid(form) 
        else: # new
            # Captcha is incorrect
            return self.form_invalid(form) # new
        
    def form_invalid(self, form): # new
        # Captcha is incorrect
        messages.error(self.request, 'Invalid captcha. Please try again.')
        # Clear the captcha from the session
        captcha_number = random.randint(1000, 9999) # new
        self.request.session['captcha'] = captcha_number
        return super().form_invalid(form) 

        
    def get_context_data(self, **kwargs): # new
        context = super().get_context_data(**kwargs)
        # Pass the captcha number to the template
        print(self.request.session.get('captcha', ''))
        context['captcha_number'] = self.request.session.get('captcha', '')
        return context

    def get_success_url(self):
        article = self.object
        return reverse("article_detail", kwargs={"pk": article.pk})


class ArticleListView(LoginRequiredMixin, ListView):
    model = Article
    template_name = "article_list.html"


class ArticleDetailView(LoginRequiredMixin, View):  
    def get(self, request, *args, **kwargs):
        view = CommentGet.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = CommentPost.as_view()
        return view(request, *args, **kwargs)


class ArticleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Article
    fields = (
        "title",
        "body",
    )
    template_name = "article_edit.html"

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user


class ArticleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Article
    template_name = "article_delete.html"
    success_url = reverse_lazy("article_list")

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user


class ArticleCreateView(LoginRequiredMixin, CreateView):
    model = Article
    template_name = "article_new.html"
    fields = ("title", "body")

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)