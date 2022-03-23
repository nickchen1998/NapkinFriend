## 若要部屬到 Heroku 要加入以下檔案
1. Porcfile (無副檔名)
2. requirements.txt
3. runtime.txt

## Procfile
```
web: gunicorn main:app
clock: python clock.py
```


## runtime.txt
```
python-3.9.2
```
