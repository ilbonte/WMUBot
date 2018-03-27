var TelegramBot = require('node-telegram-bot-api');
var moment = require('moment-timezone');
var request = require('request').defaults({
    encoding: null
});
var token = process.env.TOKEN;

// Setup polling way
var bot = new TelegramBot(token, {
    polling: true
});

var mense = {
    "povo": [{
        url: 'http://ftp.tn.ymir.eu/Povo02.jpg'
    }, {
        url: 'http://ftp.tn.ymir.eu/Povo01.jpg'
    }],
    "mesiano": [{
        url: 'http://ftp.tn.ymir.eu/mesiano01.jpg'
    }, {
        url: 'http://ftp.tn.ymir.eu/mesiano02.jpg'
    }],
    "lettere": [{
        url: 'http://ftp.tn.ymir.eu/tgar.jpg'
    }]
};

function mensaIsOpen() {
    var now = moment().tz("Europe/Rome");
    var openingTime = moment("1129", "Hmm").utcOffset(0, true);
    var closingTime = moment("1431", "Hmm").utcOffset(0, true);
    if (now.isBetween(openingTime, closingTime)) {
        return {
            result: true,
            time: now.format("HH.mm")
        };
    } else {
        return {
            result: false,
            time: now.format("HH.mm")
        };
    }
}

function sendWebcam(bot, chatId, location, force) {
    var checkMensa = mensaIsOpen();
    if (checkMensa.result || force) {
        mense[location].forEach(function (cam) {
            request.get(cam.url, function (err, res, body) {
                //process exif here
                if (err) {
                    bot.sendMessage(chatId, 'Error, please report to @ilbonte');
                } else {
                    if (res.statusCode !== 200) {
                        bot.sendMessage(chatId, 'Webcam not available. Check here: http://www.operauni.tn.it/servizi/ristorazione/webcam');
                    } else {
                        bot.sendPhoto(chatId, body);
                    }
                }
            });
        });
    } else {
        bot.sendMessage(chatId, 'Webcams are enabled from 11.45 to 14.30. (Now it\'s ' + checkMensa.time + ')');
    }
}


bot.onText(/\/povo/, function (msg, match) {
    sendWebcam(bot, msg.chat.id, 'povo');
});
bot.onText(/\/mesiano/, function (msg, match) {
    sendWebcam(bot, msg.chat.id, 'mesiano');
});
bot.onText(/\/lettere/, function (msg, match) {
    sendWebcam(bot, msg.chat.id, 'lettere');
});

bot.onText(/\/test/, function (msg, match) {
    bot.sendMessage(msg.chat.id, mensaIsOpen().time + '');
    sendWebcam(bot, msg.chat.id, 'povo', true);
    sendWebcam(bot, msg.chat.id, 'mesiano', true);
    sendWebcam(bot, msg.chat.id, 'lettere', true);
});
bot.onText(/\/sito/, function (msg, match) {
    bot.sendMessage(msg.from.id, 'http://www.operauni.tn.it/servizi/ristorazione/calendario\n');
});
bot.onText(/\/help/, function (msg, match) {
    bot.sendMessage(msg.from.id, '/povo - Mostra le Webcam delle mense di Povo\n/mesiano - Mostra le Webcam delle mense di Mesiano\n/lettere - Mostra le Webcam della mensa in via Tommaso Gar\n/sito - Invia il link del sito del sito per ulteriori info(menù, calendario, ecc)\n/help - Mostra sta roba qui');
    bot.sendMessage(msg.from.id, 'Se pensi che ci sia qualcosa di rotto contatta @ilbonte e magari manda uno screen\n');
    bot.sendMessage(msg.from.id, '@WMUBot supports PASTO LESTO https://www.youtube.com/watch?v=g9nur8G-hKw');
});

// povo - Mostra le webcam delle mense di Povo
// mesiano - Mostra le webcam delle mense di Mesiano
// lettere - Mostra le webcam della mensa in via Tommaso Gar
// sito - Invia il link del sito del sito per ulteriori info(menù, calendario, ecc)
// help - Mostra cosa posso fare