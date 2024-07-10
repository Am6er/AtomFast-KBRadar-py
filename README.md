   
# Отправляем данные на NarodMon раз в 5 минут после запуска.
Перед запуском нужно прописать свой MAC адрес.

```
.\venv\Scripts\activate.bat
.\venv\Scripts\python.exe AtomFast-KBRadar-Win.py 
2024-06-26 16:58:18.811749 Post data to narodmon AVG Intesity: 0.11425374493002892 μSv/h. Result: <Response [200]>
2024-06-26 17:03:19.068444 Post data to narodmon AVG Intesity: 0.11868042484024502 μSv/h. Result: <Response [200]>
```

# Поиск устройств 60 секунд

```
.\venv\Scripts\activate.bat
.\venv\Scripts\python.exe SearchDevices.py 
Found device MAC A8:10:87:22:40:40, Name AtomFast 
```
