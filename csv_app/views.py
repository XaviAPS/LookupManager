# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from csv_app.models import Document
from csv_app.forms import DocumentForm


def list(request):
    # Handle file upload
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        all_docs = Document.objects.all()
        repeated = False
        if form.is_valid():
            for doc in all_docs:
                if Document(docfile=request.FILES['docfile']).docfile == doc.docfile:
                    repeated = True
            if not repeated:
                newdoc = Document(docfile=request.FILES['docfile'])
                newdoc.save()

                # Redirect to the document list after POST
                return HttpResponseRedirect(reverse('list'))
    else:
        form = DocumentForm()  # A empty, unbound form

    # Load documents for the list page
    documents = Document.objects.all()

    # Render list page with the documents and the form
    return render(
        request,
        'list.html',
        {'documents': documents, 'form': form}
    )


"""
def remove_document(request):

    if request.method == 'POST':
        form = DocumentForm()
        document = request.POST.objects.get(docfile = ?????)
        document.delete()
        
        db_documents = Document.objects.all()
        
        for db_doc in db_documents:
            if db_doc = document:
                document.delete()
        
    return render(
            request,
            'list.html',
            {'documents': documents, 'form': form}
        )

        inventory = Inventory.objects.all()
        item_id = int(request.POST.get('item_id'))
        item = Inventory.objects.get(id=item_id)
        item.delete()
        return render_to_response('inventory.html', {
            'form':form, 'inventory':inventory,
            }, RequestContext(request))

"""