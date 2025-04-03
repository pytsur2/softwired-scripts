# SSH kulcsgeneráló és alias konfiguráló script

Ez a script SSH kulcsokat generál, konfigurálja az SSH config fájlt alias alapján, 
és feltölti a publikus kulcsot a távoli szerverre.

## Használat

```bash
python3 ssh_key_set.py
```

## Figyelmeztetés
Ez a script módosítja a `~/.ssh/config` fájlt és létrehoz kulcsfájlokat. 
Minden művelet előtt megerősítést kér.

## Licence
MIT
