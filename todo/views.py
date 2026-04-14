from django.shortcuts import render

from django.http import HttpResponse  #agregado
from django.shortcuts import get_object_or_404, redirect #agregado
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Task


# templates, cada app tiene su dir 'templates' al agregar la app en 'settings' se agregan sus dirs
# no es necesario: 'mainapp/templates' en TEMPLATES DIRs

# Create your views here.
def todo(request):
    tasks = Task.objects.all().order_by('-updated_at')  # '-' ordenamiento inverso o mas recientes
    #tasks = Task.objects.filter(is_completed=False)
    # 'filter' condicional multiples registros
    #tasks = Task.objects.get(id=task_id)
    # 'get' condicional solo 1 registro 
    
    context = {
        'title': 'Por hacer|▲▼AnyDev7',
        'tasks': tasks,
    }
    return render(request, 'home-todo.html', context)

def done_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)  # en lugar de 'try:'
    task.is_completed = True
    task.save()
    return redirect('todo') # más simple usar 'redirect' con el nombre de la ruta name='home'

def undone_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)  # en lugar de 'try:'
    task.is_completed = False
    task.save()
    return redirect('todo') # más simple usar 'redirect' con el nombre de la ruta name='home'

    """ # Mas lineas más complejo
    tasks = Task.objects.all()    
    return render(request, 'mainapp/home-todo.html', {   #Impresion simple en html return HttpResponse('<h2> Pagina inicio</h2')
        'title': '|▲▼AnyDev7',
        'tasks': tasks,
    })
    """   

@login_required(login_url='login')
def add_task(request):
    
    if request.method == 'POST':
        user = request.user
        name = request.POST['name']
        task = request.POST['task']
        deadline = request.POST['deadline']
        
        try:
            if Task.objects.create(user=user, name=name, task=task, deadline=deadline):
                #agregar mensaje de exito
                success = f"Se ha creado con éxito la tarea: {name}"
                messages.success(request=request, message=success)
                #messages.add_message(request=request, level=messages.SUCCESS, message=success)
            else:
                warning = f"No se pudo crear la tarea: {name}"
                messages.warning(request=request, message=warning)
                #messages.add_message(request=request, level=messages.WARNING, message=warning)
        except Exception as e:
            raise e
    tasks = Task.objects.all().order_by('-updated_at')  # '-' ordenamiento inverso o mas recientes

    context = {
        'title': 'Por hacer|▲▼AnyDev7',
        'tasks': tasks,
    }
    #return redirect('todo') # más simple usar 'redirect' con el nombre de la ruta name='home'
    return render(request, 'home-todo.html', context)

    """ # Mas lineas más complejo
    tasks = Task.objects.all()    
    return render(request, 'mainapp/home-todo.html', {   #Impresion simple en html return HttpResponse('<h2> Pagina inicio</h2')
        'title': '|▲▼AnyDev7',
        'tasks': tasks,
    })
    """


@login_required(login_url='login')  
def edit_task(request, task_id):
    get_task = get_object_or_404(Task, id=task_id)
    
    if request.method == 'POST':
        try:
            user = request.user
            name = request.POST['name']
            task = request.POST['task']
            deadline = request.POST['deadline']

            get_task.user = user
            get_task.name = name
            get_task.task = task
            get_task.deadline = deadline
            get_task.save()
            success = f"Se cambio con éxito la tarea: {name}"
            messages.success(request=request, message=success)
        except:
            pass
        #update() solo sirve para cambiar el Modelo, if record_task.objects.update(name=name, task=task, deadline=deadline):
        
        #agregar mensaje de exito
        #HttpResponse(f'<p>{name}</p>')

        # usar 'redirect' con el nombre de la ruta name='home'
        return redirect('todo') 
    else:
        context = {
            'title': 'Cambiar tarea|▲▼AnyDev7',
            'task': get_task,
        }
        return render(request, 'edit_task.html', context)
   
    #template = loader.get_template('mainapp/update_task.html')
    #return HttpResponse(template.render(context, request))

def delete_task(request, task_id):
  task = get_object_or_404(Task, id=task_id)
  task.delete()
  return redirect('todo')

# CON FORMS
"""
def addview(request, id):
    obj = mytable.objects.get(id=id)
    if request.method == 'POST':
        form = MyForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect('success')
    else:
        form = MyForm(instance=obj)
    return render(request, 'add/add.html', {'form': form})
"""


