#sed -i '1s/^/nameserver 185.51.200.2\nnameserver 178.22.122.100\n /' /etc/resolv.conf
docker-compose -f mongo.yml up -d
sh build.sh
docker exec -it cman python /app/scripts/init_project.py
docker exec -it cman python /app/scripts/permissions.py

