docker build -t dockertesting:latest . -f docker/DockerfileAuth

docker run -d --name AuthServer -p 5000:5000 dockertesting:latest