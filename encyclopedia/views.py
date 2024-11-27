import markdown
import secrets
from difflib import get_close_matches
from django.shortcuts import render, redirect
from django import forms
from django.contrib import messages

from . import util

class SearchBar(forms.Form):
    q = forms.CharField(label="", widget=forms.TextInput(attrs={'placeholder': 'Search Encyclopedia', 'class': 'search'}))

class CreateForm(forms.Form):
    title = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'title_form'}))
    content = forms.CharField(label="", max_length=1000, widget=forms.Textarea(attrs={'class': 'form-control form-control-lg', 'id':'content_form'}))


def get_random_entry():
    return secrets.choice(util.list_entries())

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "search": SearchBar(),
        "random": get_random_entry()
    })

def entry(request, title):
    page = util.get_entry(title)

    if not page:
        return render(request, "encyclopedia/error.html", {
            "title": title.capitalize(),
            "random": get_random_entry()
        })

    return render(request, "encyclopedia/entry.html", {
        "title": title.capitalize(),
        "content": markdown.markdown(page),
        "search": SearchBar(),
        "random": get_random_entry()
    })

def search(request):
    if request.method == "POST":
        query = SearchBar(request.POST)
        if query.is_valid():
            final_query = query.cleaned_data["q"]
            page = util.get_entry(final_query)
            close_matches = get_close_matches(final_query.casefold(), [str.casefold() for str in util.list_entries()], n=5)
            if page:
                return render(request, "encyclopedia/entry.html", {
                    "title": final_query.capitalize(),
                    "content": markdown.markdown(page),
                    "random": get_random_entry(),
                })
            
            message = "No matches." if not close_matches else "Results"
            return render(request, "encyclopedia/search.html", {
                        "message": message,
                        "matches": map(str.capitalize, close_matches),
                        "random": get_random_entry(),
                        "search": SearchBar()
                    })
        
    return render(request, "encyclopedia/error.html", {
            "message": "You are trying to access the wrong page.",
            "random": get_random_entry(),
            "search": SearchBar()
        })

def new(request):
    if request.method == "POST":
        form = CreateForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            if title and title.casefold() not in [entry.casefold() for entry in util.list_entries()]:
                util.save_entry(title, content)
                page = util.get_entry(title)

                messages.success(request, f"The page '{title} has been created.") # Test
                return render(request, "encyclopedia/entry.html", {
                    "title": title.capitalize(),
                    "content": markdown.markdown(page),
                    "search": SearchBar(),
                    "random": get_random_entry()
                })
            else:
                return render(request, "encyclopedia/error.html", {
                    "message": "Page already exist.",
                    "random": get_random_entry(),
                    "search": SearchBar()
                })
            
    return render(request, "encyclopedia/new.html", {
        "form": CreateForm(),
        "search": SearchBar(),
        "random": get_random_entry()
    })

def edit(request, name):
    if request.method == "POST":
        form = CreateForm(request.POST)
        if form.is_valid():
            cleaned_title = form.cleaned_data["title"]
            cleaned_content = form.cleaned_data["content"]

            # !duplicate entries
            if cleaned_title.casefold() != name.casefold() and cleaned_title.casefold() in [entry.casefold() for entry in util.list_entries()]:
                return render(request, "encyclopedia/error.html", {
                    "message": "A page with the new title already exists.",
                    "random": get_random_entry(),
                    "search": SearchBar
                })
            
            util.save_entry(cleaned_title, cleaned_content)
            messages.add_message(request, messages.SUCCESS, "Entry changed.")
            return redirect("wiki:title", cleaned_title)

    content = util.get_entry(name)
    form = CreateForm({"title": name, "content": content})

    if not content:
        return render(request, "encyclopedia/error.html", {
            "message": f"The entry '{name}' does not exist.",
            "random": get_random_entry(),
            "search": SearchBar()
        })
    
    return render(request, "encyclopedia/edit.html", {
        "title": name,
        "form": form,
        "random": get_random_entry(),
        "search": SearchBar()
    })

def random(request, title):
    page = util.get_entry(title)
    if not page:
        return render(request, "encyclopedia/error.html", {
            "message": "Random entry not found.",
            "random": get_random_entry(),
            "search":SearchBar()
        })
        
    return render(request, "encyclopedia/entry.html", {
        "entry": title.capitalize(),
        "content": markdown.markdown(page),
    })