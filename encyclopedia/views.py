import markdown
import secrets
from difflib import get_close_matches
from django.shortcuts import render, redirect
from django import forms

from . import util

def entries():
    return util.list_entries()
# entries = util.list_entries()

class search_bar(forms.Form):
    q = forms.CharField(label="", widget=forms.TextInput(attrs={'placeholder': 'Search Encyclopedia', 'class': 'search'}))

class CreateForm(forms.Form):
    title = forms.CharField(label="", max_length=1000, widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'title_form'})) #CHANGE TEXTAREA TO INPUT
    content = forms.CharField(label="", max_length=1000, widget=forms.Textarea(attrs={'class': 'form-control form-control-lg', 'id':'content_form'}))

def random_entry(e):
    return secrets.choice(e)

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": entries(),
        "search": search_bar(),
        "random": random_entry(entries()) #random.sample(entries, 1)[0]
    })

def entry(request, title):
    page = util.get_entry(title)

    if not page:
        return render(request, "encyclopedia/error.html", {
            "title": title.capitalize(),
            "random": random_entry(entries())
        })

    return render(request, "encyclopedia/entry.html", {
        "title": title.capitalize(),
        "content": markdown.markdown(page),
        "search": search_bar(),
        "random": random_entry(entries())
    })

def new(request):
    if request.method == "POST":
        form = CreateForm(request.POST)
        if form.is_valid():
            # print("form is valid") #debug
            title = form.cleaned_data["title"].capitalize()
            content = form.cleaned_data["content"]
            # print(f"before checking in entries: {title}") #debug
            if title and not title in entries():
                # print("saving entry..") #debug
                util.save_entry(title, content)
                # print(f"after saving page: {title}") #debug
                # print("converting page..") #debug
                page = util.get_entry(title)
                # page_converted = markdown.markdown(page)

                return render(request, "encyclopedia/entry.html", {
                    "title": title.capitalize(),
                    "content": markdown.markdown(page),
                    "search": search_bar(),
                    "random": random_entry(entries())
                })
            else:
                return render(request, "encyclopedia/error.html", {
                    "message": "Page already exist.",
                    "random": random_entry(entries()),
                    "search": search_bar()
                })
            
    return render(request, "encyclopedia/new.html", {
        "form": CreateForm(),
        "search": search_bar(),
        "random": random_entry(entries())
    })

def search(request):
    if request.method == "POST":
        query = search_bar(request.POST)
        if query.is_valid():
            final_query = query.cleaned_data["q"]
            page = util.get_entry(final_query)

            capitalize_titles = lambda x : [element.capitalize() for element in x]
            to_lowercase = lambda x: [element.lower() for element in x]
            close_matches = get_close_matches(final_query, to_lowercase(entries()), n=5)
            # print(f"matches before:{close_matches}") #Debug
            if not page:
                if not close_matches:
                    # print("No matches for your search") #debug
                    return render(request, "encyclopedia/search.html", {
                        "message": "No matches.",
                        "random": random_entry(entries()),
                    })
                else:
                    return render(request, "encyclopedia/search.html", {
                        "message": "Results",
                        "matches": capitalize_titles(close_matches),
                        "random": random_entry(entries()),
                    })
            
            return render(request, "encyclopedia/entry.html", {
                "title": final_query.capitalize(),
                "content": markdown.markdown(page),
                "random": random_entry(entries()),
            })
    return render(request, "encyclopedia/error.html", {
            "message": "You are trying to access the wrong page."
        })


def random(request, title):
    page = util.get_entry(title)
    return render(request, "encyclopedia/entry.html", {
        "entry": title.capitalize(),
        "content": markdown.markdown(page),
    })

def edit(request, name):
    if request.method == "POST":
        form = CreateForm(request.POST)
        if form.is_valid():
            cleaned_title = form.cleaned_data["title"]
            cleaned_content = form.cleaned_data["content"]

            util.save_entry(cleaned_title, cleaned_content)
            # return redirect("title", cleaned_title)
            return redirect(f"../wiki/{cleaned_title}") # hardcoded because doesn't find view or the name of the url

    title = name
    content = util.get_entry(name)
    form = CreateForm({"title": title, "content": content})

    return render(request, "encyclopedia/edit.html", {
        "title": title,
        "form": form,
        "random": random_entry(entries())
    })
