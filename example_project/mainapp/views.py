from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
import datetime
import json
import os

def index(request):
    rpaths = [c for c in request.path.split("/") if (c) ];
    template = f"{rpaths[0]}/index.html"
    if ( len(rpaths) > 0 ):
        try:
            loader.get_template(template)
            return render(request, template)
        except:
            pass

    return HttpResponse(f"{template} not found");

VERSION= f"version 1.1 {datetime.datetime.now()}"

def info(request):
    import os

    keys = "VARIABLE1 VARIABLE2 SECRET1 SECRET2 PORT DEAFAULT_APP".split()
    ctxt = {k:os.environ.get(k, "NOT-SET") for k in keys}
    
    ctxt['version'] = VERSION
    ctxt['podname'] = f"{request.META.get('REMOTE_ADDR')}"
    
        
    return render(request, "mainapp/info.html", ctxt)

def feedback(request):
    return render(request, "mainapp/feedback.html")

def submit_feedback(request ):
    from django.conf import settings
    
    par = dict(request.GET)
    par.update(request.POST)

    print(par)
    
    feedback_data = {
        'timestamp': datetime.datetime.now().isoformat(),
        'url'       : par.get('url', ''),
        'type'      : par.get('feedback_type', ''),
        'subject'   : par.get('subject', ''),
        'message'   : par.get('message', ''),
        'user'      : par.get('user', ''),
        'username'  : par.get('username', ''),
        'email'     : par.get('useremail', ''),
        'user_ip'   : request.META.get('REMOTE_ADDR', 'unknown'),
        'user_agent': request.META.get('HTTP_USER_AGENT', 'unknown'),
        'files': []
    }
    
    feedback_dir = getattr(settings, 'FEEDBACK_DIR', '/tmp/feedback_submissions/')
    os.makedirs(feedback_dir, exist_ok=True)
    
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    
    for key in request.FILES:
        uploaded_file = request.FILES[key]
        file_path = os.path.join(feedback_dir, f"{timestamp}_{uploaded_file.name}")
        
        with open(file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        
        feedback_data['files'].append({
            'name': uploaded_file.name,
            'size': uploaded_file.size,
            'path': file_path
        })
    
    feedback_file = os.path.join(feedback_dir, f"feedback_{timestamp}.json")
    with open(feedback_file, 'w') as f:
        json.dump(feedback_data, f, indent=2)
    
    return JsonResponse({
        'status': 'success',
        'message': 'Feedback submitted successfully',
        'feedback_id': timestamp
    })
        
    
