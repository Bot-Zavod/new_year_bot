# use dev arg to use pre-commit

RED="\033[0;31m"
GREEN="\033[0;32m"
ENDCOLOR="\033[0m"


echo -e "\n${RED}Deleting old environment${ENDCOLOR}\n"
deactivate
rm -rf venv

echo -e "\n${RED}Installing package manager${ENDCOLOR}\n"
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -

echo -e "\n${RED}Updating packages${ENDCOLOR}\n"
poetry --version
poetry self update

# check if command line argument is dev or empty
if [[ "$1" = "--dev" || "$1" = "-d" ]]
	then
	echo -e "\n${GREEN}Installing dependencies for development${ENDCOLOR}\n"
	poetry install
else
	echo -e "\n${GREEN}Installing dependencies${ENDCOLOR}\n"
	poetry install --no-dev
fi

poetry shell
echo -e "\n${RED}Installed${ENDCOLOR}\n"
poetry show --tree
