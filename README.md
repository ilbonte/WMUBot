# WMUBot
Bot per telegram che mostra le foto delle webcam delle mense UNITN

## Webcam disponibili
- /povo Webcam del Polo Ferrari (Mensa veloce e normale)
- /mesiano Webcam ????
- /lettere Webcam di via Tommaso Gar

Il bot è pronto per essere deployato su Google App Engine. 

Una volta ottenuto il token da [Bot Father](https://telegram.me/botfather) è sufficiente inserirlo alla riga 20 di main.py.
Il Project ID scelto dalla [developer console](https://console.developers.google.com/project) va inserito nella prima riga nel file app.yaml

Se non hai mai usato Bot Father e/o Google App Engine potrebbe esserti utile questa guida: https://github.com/yukuku/telebot#instructions