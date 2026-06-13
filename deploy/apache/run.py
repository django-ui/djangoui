#!/usr/bin/env python3
import subprocess
import sys
import os

CONTAINER_NAME = "apache"
IMAGE_NAME = "apache-ssl-local"
NW="--network demonet"

def run_cmd(cmd):
    print(f"\n>>> {cmd}\n")
    subprocess.run(cmd, shell=True)

def do_run():
    run_cmd(f"docker run -d --rm -p 443:443 -p 80:80 {NW} --name {CONTAINER_NAME} {IMAGE_NAME}")

def do_build():
    run_cmd(f"docker build --platform linux/amd64,linux/arm64 --no-cache -t {IMAGE_NAME} .")

def do_build_cached():
    run_cmd(f"docker build linux/amd64,linux/arm64 -t {IMAGE_NAME} .")

def do_stop():
    run_cmd(f"docker stop {CONTAINER_NAME}")

def do_login():
    run_cmd(f"docker exec -it {CONTAINER_NAME} bash")

def menu():
    print("\n===== Apache SSL Docker =====")
    print(f"1. Run in background (docker run -d --rm -p443:443 -p80:80 {NW} --name {CONTAINER_NAME} {IMAGE_NAME})")
    print(f"2. Build image --no-cache (docker build --no-cache -t {IMAGE_NAME} .)")
    print(f"3. Build image           (docker build -t {IMAGE_NAME} .)")
    print(f"4. Stop container")
    print(f"5. Login to container (docker exec -it {CONTAINER_NAME} bash)")
    print(f"q. Quit")
    return input("\nChoice: ").strip()

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # No arguments => run the container directly
    if len(sys.argv) == 1:
        do_run()
    elif sys.argv[1] in ("-h", "--help"):
        print("Usage: python run.py [command]")
        print()
        print("Commands:")
        print("  (no args)  Run the container (docker run -it --rm -p 443:443)")
        print("  build      Build the Docker image")
        print("  stop       Stop the running container")
        print("  login      Login to running container (docker exec -it bash)")
        print("  menu       Interactive menu")
        print("  -h, --help Show this help message")
    elif sys.argv[1] == "build":
        do_build()
    elif sys.argv[1] == "stop":
        do_stop()
    elif sys.argv[1] == "login":
        do_login()
    elif sys.argv[1] == "menu":
        while True:
            choice = menu()
            if choice == "1":
                do_run()
            elif choice == "2":
                do_build()
            elif choice == "3":
                do_build_cached()
            elif choice == "4":
                do_stop()
            elif choice == "5":
                do_login()
            elif choice.lower() == "q":
                break
            else:
                print("Invalid choice")
    else:
        print(f"Unknown command: {sys.argv[1]}")
        print("Run 'python run.py -h' for help")
