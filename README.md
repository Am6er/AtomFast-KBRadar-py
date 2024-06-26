   
# Отправляем данные на NarodMon раз в 5 минут после запуска.
Перед запуском нужно прописать свой MAC адрес.

```
.\venv\Scripts\activate.ps1
.\venv\Scripts\python.exe AtomFast-KBRadar-Win.py 
2024-06-26 16:58:18.811749 Post data to narodmon AVG Intesity: 0.11425374493002892 μSv/h. Result: <Response [200]>
2024-06-26 17:03:19.068444 Post data to narodmon AVG Intesity: 0.11868042484024502 μSv/h. Result: <Response [200]>
```

# Считываем данные с портативного дозиметра AtomFast (Bluetooth Low Energy)

```
$ ./AtomFast-KBRadar.py
Connecting...
Intencity AVG:0.18 μSv/h CURRENT:0.18 μSv/h
Temperature: 23℃
Battery: 65%
---
```
 
```
$ sudo hcitool lescan 
$ gatttool -I -b 38:d2:69:b9:84:01
[LE]> connect
[LE]> char-write-cmd 0x0027 0100
Notification handle = 0x0025 value: 00 06 bc bf 3e 66 13 34 3e 10 00 41 1a 
Notification handle = 0x0025 value: 00 0a bc bf 3e 1e d8 1d 3e 11 00 41 1a 
Notification handle = 0x0025 value: 00 0b bc bf 3e 9d b9 0a 3e 0f 00 41 1b 
Notification handle = 0x0025 value: 00 10 bc bf 3e 4e 2c 13 3e 14 00 41 1a 
```
