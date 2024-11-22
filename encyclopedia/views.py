import markdown
import secrets
from django.shortcuts import render
from django import forms

from . import util

entries = util.list_entries()

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": entries,
        "random": secrets.choice(entries), #random.smaple(entries, 1)[0]
        "form": NewTaskForm()
    })

def entry(request, title):
    entries = util.list_entries()
    page = util.get_entry(title)

    if not page:
        return render(request, "encyclopedia/error.html", {
            "title": title.capitalize(),
            "random": secrets.choice(entries),
        })

    return render(request, "encyclopedia/entry.html", {
        "title": title.capitalize(),
        "content": markdown.markdown(page),
        "random": secrets.choice(entries),
    })

def new(request):
    return render(request, "encyclopedia/new.html", {
        "random": secrets.choice(entries),
    })

def search(request):
    if request.method == "POST":
        query = NewTaskForm(request.POST)
        if query.is_valid():
            final_query = query.cleaned_data["q"]
            page = util.get_entry(final_query)

            if not page:
                return render(request, "encyclopedia/search.html", {
                    "entries": entries,
                    "random": secrets.choice(entries),
                })
            
            return render(request, "encyclopedia/entry.html", {
                "title": final_query.capitalize(),
                "content": markdown.markdown(page),
                "random": secrets.choice(entries),
            })
    return render(request, "encyclopedia/index.html")

class NewTaskForm(forms.Form):
    q = forms.CharField(label="", widget=forms.TextInput(attrs={'placeholder': 'Search Encyclopedia', 'class': 'search'}))


def random(request, title):
    page = util.get_entry(title)
    return render(request, "encyclopedia/entry.html", {
        "entry": title.capitalize(),
        "content": markdown.markdown(page)
    })