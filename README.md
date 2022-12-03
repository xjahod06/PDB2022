# PDB projekt 2022
vytvořili jsme api, které pomocí principu CQRS synchronizuje SQL a noSQL data pro lepší přístupnost

## Potřebné nástroje
Python3
docker
docker compose

## Instalace
Prvně za zapotřebí spustit docker v separátním okně pomocí příkazu `docker-compose up`.
Následně stačí spustit script `install.sh` s argumety vašeho přihlášení do školní oracle SQL, tyto údaje budou uloženy v configuračním souboru API. Dále se stáhnou data, které se importují do oracle DB a zároveň do monga.
`bash install.sh name password`

## Spuštění
jelikož máme api rozdělené pro přímání dat a pro odesílání dat tak se musí spouštět jako 2 rozdílné processy toto by v reálném nasazení fungovalo pomocí reversní proxy a tvářilo se jako jeden přístupový bod.
lze spustit pomocí
```
cd src
uvicorn api_oracle:app --reload --port 8000
```
a
```
cd src
uvicorn api_mongo:app --reload --port 8001
```

které budou po spuštění dostupné na adresách `http://localhost:8000/` a `http://localhost:8001/` případně je možné přejít na dokumentaci na endpointu `/docs`


## Testy
testy sú implementované pomocou nástroja `pytest`, stačí zo zložky `/src` zavolať skript `run_tests.sh` a vykonajú sa všetky dostupné testy. Upozornenie: celá množina testov môže bežať v radoch minút.
