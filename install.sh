python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
cd src

echo "creating config"
python3 config_init.py $1 $2

echo "downloading dataset"
python3 downloadDB.py

echo "inicializing databases"
python3 db_init.py