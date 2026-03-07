TO create a new project, simply

```
    mkdir myapp
    cd myapp
    if [ ! -d ".venv" ]; then
        python3.13 -m venv .venv
    fi
    source .venv/bin/activate

    git clone https://github.com/django-ui/djangoui.git
    mv djangoui djangoui-framework
    cd djangoui-framework
    pip install .
    cd ..

    cp -R djangoui-framework/example_project/* .
    pip install -r requirements.txt
    #EDIT my_config.py
    python manage.py migrate
    ./run.sh
```
