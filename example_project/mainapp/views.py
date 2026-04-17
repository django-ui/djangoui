from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
import datetime
import json
import os

# ---------------------------------------------------------------------------
# App catalog helpers
# ---------------------------------------------------------------------------
_ICON_DEFAULTS = {
    'lmapp':   'home',
    'ontviz':  'graph',
    'mainapp': 'grid',
    'chatapp': 'chat',
}
_COLOR_DEFAULTS = {
    'lmapp':   '#0071e3',
    'ontviz':  '#7c3aed',
    'mainapp': '#059669',
    'chatapp': '#db2777',
}

def _parse_app_md(app_name):
    """Read {app}/app.md front-matter (--- key: value ---) and return a dict."""
    project_root = os.getcwd()
    md_path = os.path.join(project_root, app_name, 'app.md')
    meta = {
        'name':        app_name,
        'title':       app_name.replace('app', ' App').title().strip(),
        'description': f'The {app_name} application.',
        'icon':        _ICON_DEFAULTS.get(app_name, 'app'),
        'url':         f'/{app_name}/',
        'color':       _COLOR_DEFAULTS.get(app_name, '#6e6e73'),
        'badge':       '',
        'body':        '',
        'has_md':      False,
    }
    if not os.path.exists(md_path):
        return meta
    try:
        with open(md_path, encoding='utf-8') as f:
            content = f.read()
        meta['has_md'] = True
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 2:
                for line in parts[1].strip().splitlines():
                    if ':' in line:
                        k, _, v = line.partition(':')
                        meta[k.strip().lower()] = v.strip()
                if len(parts) == 3:
                    meta['body'] = parts[2].strip()
    except Exception:
        pass
    return meta

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


_HIDDEN_APPS = {'mainapp'}  # remove from catalog for now

def applications(request):
    from django.conf import settings
    include_apps = getattr(settings, 'INCLUDE_APPS', [])
    apps = [_parse_app_md(a) for a in include_apps if a not in _HIDDEN_APPS]
    return render(request, 'mainapp/applications.html', {'apps': apps})


def app_launch(request):
    app_name = request.GET.get('app', '').strip()
    if not app_name:
        return redirect('/mainapp/applications/')
    meta = _parse_app_md(app_name)
    # Permission check — everyone allowed by default.
    # Replace this block with real ACL logic when needed.
    has_access = True
    if not has_access:
        return render(request, 'mainapp/applications.html', {
            'apps': [],
            'error': f'You do not have permission to access {meta["title"]}.',
        }, status=403)
    target_url = meta.get('url') or f'/{app_name}/'
    if target_url.startswith('#'):
        return redirect(f'/lmapp/#chat')
    return redirect(target_url)

