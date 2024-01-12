#colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

if [ "$EUID" -eq 0 ]
  then printf "${RED}[!] Please do not run as root${NC}\n"
  exit
fi

printf "${YELLOW}[i] Getting Sudo Privileges${NC}\n"
sudo printf "${GREEN}[+] Sudo Privileges Acquired${NC}\n"

printf "${YELLOW}[i] Creating SharedData Directory${NC}\n"
mkdir SharedData > /dev/null 2>&1
sudo chown -R $USER:$USER SharedData
printf "${GREEN}[+] SharedData Directory Created${NC}\n"

#check if docker is installed

if ! [ -x "$(command -v docker)" ]; then
    printf "${YELLOW}[i] Installing Docker${NC}\n"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh ./get-docker.sh
    sudo groupadd docker
    sudo usermod -aG docker $USER
    sudo chmod 666 /var/run/docker.sock
    sudo systemctl enable docker
    sudo systemctl start docker
    printf "${GREEN}[+] Docker Installed${NC}\n"
else
    printf "${GREEN}[+] Docker Already Installed${NC}\n"
fi

printf "${YELLOW}[i] Building Docker Compose${NC}\n"
sudo docker-compose build
printf "${GREEN}[+] Docker Compose Built${NC}\n"