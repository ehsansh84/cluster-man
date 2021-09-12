#git pull
docker rmi cman || true
docker build -t cman .
docker stop cman || true
docker rm cman || true
docker run --name cman -p 8101:8282 -d --restart always --network dockers_default -e MONGO=mongodb  cman

