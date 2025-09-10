sudo docker stop AuthServer
sudo docker rm AuthServer
sudo docker build -t dockertesting:latest . -f DockerfileAuth
sudo docker run -d --name AuthServer -p 5000:5000 dockertesting:latest
