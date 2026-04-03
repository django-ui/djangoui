import sys
import subprocess
import argparse
import os
import shutil
from pathlib import Path

def print_help():
    """Print help information for djangoui CLI"""
    help_text = """
DjangoUI CLI - Django UI Framework Command Line Interface

Usage:
    djangoui [OPTIONS] [PORT]

Arguments:
    PORT                    Port number for the development server (default: 8000)

Options:
    -h, --help             Show this help message and exit
    -s, --setup            Create a new DjangoUI project template
    -c, --create_template NAME
                           Copy example_project template with given name

Examples:
    djangoui               Run server on default port 8000
    djangoui 3000          Run server on port 3000
    djangoui --setup       Create a new project template
    djangoui -c myproject  Copy example_project as 'myproject'
"""
    print(help_text)

def create_template(project_name):
    """Copy example_project from installed djangoui package"""
    try:
        import djangoui
        djangoui_path = Path(djangoui.__file__).parent
        example_project_path = djangoui_path.parent / 'example_project'
        
        if not example_project_path.exists():
            print(f"Error: example_project not found at {example_project_path}")
            return
        
        target_path = Path.cwd() / project_name
        
        if target_path.exists():
            print(f"Error: Directory '{project_name}' already exists")
            return
        
        print(f"Copying example_project to '{project_name}'...")
        shutil.copytree(example_project_path, target_path)
        print(f"Successfully created project template at: {target_path}")
        
    except ImportError:
        print("Error: djangoui package not found")
    except Exception as e:
        print(f"Error creating template: {e}")

def main():
    parser = argparse.ArgumentParser(
        description='DjangoUI CLI - Django UI Framework Command Line Interface',
        add_help=False
    )
    parser.add_argument('-h', '--help', action='store_true', help='Show help message')
    parser.add_argument('-c', '--create_template', metavar='NAME', type=str, help='Copy example_project template with given name')
    parser.add_argument('port', nargs='?', type=int, default=8000, help='Port number for the development server')
    
    args = parser.parse_args()
    
    if args.help:
        print_help()
        return
    
    if args.create_template:
        create_template(args.create_template)
        return
    
    port = args.port
    
    print(f"Running migrations...")
    subprocess.run([sys.executable, "-m", "djangoui.manage", "migrate"], check=True)
    
    print(f"Starting development server on port {port}...")
    subprocess.run([sys.executable, "-m", "djangoui.manage", "runserver", f"0:{port}"], check=True)

if __name__ == "__main__":
    main()
