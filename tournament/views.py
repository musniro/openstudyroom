from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

def index(request):
	template = loader.get_template('tournament/results.html')
	context = {
		"test": 3
	}
	return HttpResponse(template.render(context,request))
	#return HttpResponse("yow")
