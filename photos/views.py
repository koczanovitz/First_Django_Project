from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, Q, Prefetch
from django.http.response import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.views.generic import (
    ListView,
    DetailView,
    FormView,
    CreateView,
    UpdateView,
    DeleteView
)
from django.urls import reverse_lazy, reverse

from .forms import UserCreationForm
from .models import Post, User, Comment, Like


class RegisterView(FormView):
    form_class = UserCreationForm
    template_name = "registration/register.html"
    success_url = reverse_lazy('photos:feed')

    def form_valid(self, form):
        form.save()  # creates a user in DB

        email = form.cleaned_data["email"]
        password = form.cleaned_data["password1"]
        user = authenticate(self.request, email=email, password=password)
        if user is not None:
            login(self.request, user)
            return super().form_valid(form)


def index(request):
    if request.user.is_authenticated:
        return redirect('photos:feed')
    else:
        context = {}
        return render(request, 'photos/index.html', context)


class FeedView(LoginRequiredMixin, ListView):
    template_name = 'photos/feed.html'
    context_object_name = 'post_list'
    extra_context = {
        'title': 'feed',
    }
    # model = Post

    def get_queryset(self):
        return Post.objects.filter(
            user__in=self.request.user.following.all()
        ).order_by("-created_timestamp")  # -: ASC -> DESC


class PostView(DetailView):
    template_name = "photos/post.html"
    context_object_name = "post"

    def get_queryset(self):
        q = (
            Q(like__user=self.request.user)
            & Q(like__like=True)
        )
        return Post.objects.select_related("user").annotate(
            like_count=Count('like', filter=Q(like__like=True)),
            liked_by_user=Count("like", filter=q),
        ).prefetch_related(
            Prefetch("comment_set", queryset=Comment.objects.select_related("user")))

    def get_context_data(self, **kwargs):
        context = {
            "title": f"{self.object.user}: {self.object.content}",
        }
        return super().get_context_data(**context)


class UserView(DetailView):
    template_name = "photos/user.html"
    context_object_name = "user"
    queryset = User.objects.all().prefetch_related(
        Prefetch("post_set", queryset=Post.objects.select_related("user")))

    def get_context_data(self, **kwargs):
        context = {
            "title": self.object
        }
        return super().get_context_data(**context)


class SearchView(ListView):
    context_object_name = "users"
    template_name = "photos/search.html"
    extra_context = {
        "title": "Wyszukiwarka",
    }

    def get_queryset(self):
        # nie rzuci błędu tak jak GET['q]; zwróci None jeżeli 'q' nie bedzie istniec
        phrase = self.request.GET.get('q')
        if phrase is None:
            return User.objects.none()  # pusty zbiór wyników
        # rozbuduj za pomocą Q()

        q = (
            Q(email__icontains=phrase)
            | Q(firstname__icontains=phrase)
            | Q(lastname__icontains=phrase)
        )
        return User.objects.filter(q)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["phrase"] = self.request.GET.get('q')
        return context


@login_required
@require_POST
def like(request, post_pk):
    if request.method == "POST":
        post = get_object_or_404(Post, pk=post_pk)

        # przypadek 1: użytkownik pierwszy raz lajkuje post,
        #               trzeba utworzyć obiekt Like

        # przypadek 2: użytkownik już kiedyś polubił dany post,
        #               później odlubił , teraz ponownie chc polubic
        #               trzeba ustawić like.like = True

        like, created = Like.objects.get_or_create(
            user=request.user,
            post=post,
            defaults={"like": True},
        )

        if not created:
            like.like = True
            like.save()
            return HttpResponse(status=200)  # 200 OK

        return HttpResponse(status=201)  # 201 Created


@login_required
@require_POST
def dislike(request, post_pk):
    post = get_object_or_404(Post, pk=post_pk)
    like = get_object_or_404(Like, post=post, user=request.user)
    like.like = False
    like.save()
    return HttpResponse(status=200)  # 200 OK

# operacje na postach


class CreatePost(LoginRequiredMixin, CreateView):
    model = Post
    template_name = "photos/create_post.html"
    fields = [
        "content",
        "image",
    ]

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class UpdatePost(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    template_name = "photos/update_post.html"
    extra_content = {
        'title': "Edytuj wpis"
    }
    fields = [
        "content",
        "image",
    ]

    def test_func(self):
        self.object = super().get_object()
        return self.object.user == self.request.user
        # or self.request.user.is_superuser pomaga edytowac obce wpisy


class DeletePost(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post

    def get_success_url(self):
        return self.request.user.get_absolute_url()

    def test_func(self):
        self.object = super().get_object()
        return self.object.user == self.request.user
        # or self.request.user.is_superuser pomaga edytowac obce wpisy

# operacje na komentarzach


class CreateComment(LoginRequiredMixin, CreateView):
    model = Comment
    template_name = "photos/create_comment.html"
    extra_content = {
        "title": "Dodaj Komentarz",
    }
    fields = [
        "content",
    ]

    def get_success_url(self):
        return self.object.post.get_absolute_url()

    def form_valid(self, form):
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_pk'])
        form.instance.user = self.request.user
        return super().form_valid(form)


class UpdateComment(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment
    template_name = "photos/update_comment.html"
    extra_content = {
        "title": "Edytuj Komentarz",
    }
    fields = [
        "content",
    ]

    def get_success_url(self):
        return self.object.post.get_absolute_url()

    def test_func(self):
        self.object = super().get_object()
        return self.object.user == self.request.user or self.request.is_superuser


class DeleteComment(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment

    def get_success_url(self):
        return self.object.post.get_absolute_url()

    def test_func(self):
        self.object = super().get_object()
        return self.object.user == self.request.user
        # or self.request.user.is_superuser pomaga edytowac obce wpisy
