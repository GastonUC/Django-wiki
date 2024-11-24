import markdown
import secrets
from difflib import get_close_matches
from django.shortcuts import render
from django import forms

from . import util

entries = util.list_entries()

class NewTaskForm(forms.Form):
    q = forms.CharField(label="", widget=forms.TextInput(attrs={'placeholder': 'Search Encyclopedia', 'class': 'search'}))

class CreateForm(forms.Form):
    title = forms.CharField(label="", max_length=150, widget=forms.Textarea(attrs={'class': 'title'}))
    content = forms.CharField(label="", max_length=250, widget=forms.Textarea(attrs={}))

def random_entry(e):
    return secrets.choice(e)

def index(request):
    # if request.method == "POST":
    #     query = NewTaskForm(request.POST)
    #     if query.is_valid():
    #         query = query.cleaned_data["q"]
    #         page = util.get_entry(query)
    #         capit = lambda x: [element.capitalize() for element in x]
    #         toLower = lambda x: [element.lower() for element in x]
    #         close_matches = get_close_matches(query, toLower(entries), n=5)
    return render(request, "encyclopedia/index.html", {
        "entries": entries,
        "random": random_entry(entries), #random.smaple(entries, 1)[0]
        "search": NewTaskForm()
    })

def entry(request, title):
    entries = util.list_entries()
    page = util.get_entry(title)

    if not page:
        return render(request, "encyclopedia/error.html", {
            "title": title.capitalize(),
            "random": random_entry(entries),
        })

    return render(request, "encyclopedia/entry.html", {
        "title": title.capitalize(),
        "content": markdown.markdown(page),
        "random": random_entry(entries),
    })

def new(request):
    if request.method == "POST":
        form = CreateForm(request.POST)
        if form.is_valid():
            # print("form is valid") #debug
            title = form.cleaned_data["title"].capitalize()
            content = form.cleaned_data["content"]
            # print(f"before checking in entries: {title}") #debug
            if not title in entries:
                # print("saving entry..") #debug
                util.save_entry(title, content)
                # print(f"after saving page: {title}") #debug
                # print("converting page..") #debug
                page = util.get_entry(title)
                # page_converted = markdown.markdown(page)

                return render(request, "encyclopedia/entry.html", {
                    "title": title.capitalize(),
                    "content": markdown.markdown(page),
                    "random": random_entry(entries)
                })
            else:
                return render(request, "encyclopedia/error.html", {
                    "message": "Page already exist."
                })
            
    return render(request, "encyclopedia/new.html", {
        "form": CreateForm(),
        "random": random_entry(entries)
    })

def search(request):
    if request.method == "POST":
        query = NewTaskForm(request.POST)
        if query.is_valid():
            final_query = query.cleaned_data["q"]
            page = util.get_entry(final_query)

            capitalize_titles = lambda x : [element.capitalize() for element in x]
            to_lowercase = lambda x: [element.lower() for element in x]
            close_matches = get_close_matches(final_query, to_lowercase(entries), n=5)
            # print(f"matches before:{close_matches}") #Debug
            if not page:
                if not close_matches:
                    # print("No matches for your search") #debug
                    return render(request, "encyclopedia/search.html", {
                        "message": "No matches.",
                        "random": random_entry(entries),
                    })
                else:
                    return render(request, "encyclopedia/search.html", {
                        "message": "Results",
                        "matches": capitalize_titles(close_matches),
                        "random": random_entry(entries),
                    })
            
            return render(request, "encyclopedia/entry.html", {
                "title": final_query.capitalize(),
                "content": markdown.markdown(page),
                "random": random_entry(entries),
            })
    return render(request, "encyclopedia/error.html", {
            "message": "You are trying to access the wrong page."
        })


def random(request, title):
    page = util.get_entry(title)
    return render(request, "encyclopedia/entry.html", {
        "entry": title.capitalize(),
        "content": markdown.markdown(page)
    })
def lower_entries(entries):
    return [element.lower() for element in entries]

    
lower_entries = lambda x: [element.lower() for element in x]
