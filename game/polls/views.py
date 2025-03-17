from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render
from .models import Question
from django.shortcuts import get_object_or_404
from .models import Question
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Question, Choice
from django.shortcuts import render

def index(request):
    return HttpResponse("Merhaba, Ben Selin! Bu anket uygulamamın başlangıcı!")



def index(request):
    latest_question_list = Question.objects.order_by('-pub_date')[:5]
    context = {'latest_question_list': latest_question_list}
    return render(request, 'polls/index.html', context)



def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/detail.html', {'question': question})



def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "Bir seçim yapmadınız.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))




def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/results.html', {'question': question})

