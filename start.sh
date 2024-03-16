#colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

printf "${YELLOW}[i] Starting Docker Containers${NC}\n"
docker-compose up -d
printf "${GREEN}[+] Docker Containers Started${NC}\n"