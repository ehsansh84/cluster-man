#git pull
docker rmi cman 
docker build -t cman .
docker stop cman
docker rm cman
docker run --name cman -p 8101:8282 -d --restart always --network dockers_default -e MONGO=mongodb  cman

