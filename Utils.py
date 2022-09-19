import re
import pytz
from datetime import datetime

acc_list = []
acc_list.append({'name': 'ada', "list":["825920479055671296", "4135644558"]})
acc_list.append({'name': 'luna', "list":[ "1022028994772910086"]})
acc_list.append({'name': 'eth', "list":["2312333412", "295218901"]})
acc_list.append({'name': 'near', "list":["1031949518609121280"]})
acc_list.append({'name': 'atom', "list": ["15223775"]})
acc_list.append({'name': 'avax', "list":["22325121"]})
acc_list.append({'name': 'ftm', "list":["977020204071792641"]})
acc_list.append({'name': 'one', "list":["1006055524666826754"]})
acc_list.append({'name': 'ksm', "list":["1141423436671201282"]})
acc_list.append({'name': 'matic', "list":["914738730740715521"]})
acc_list.append({'name': 'sol', "list":["951329744804392960"]})
acc_list.append({'name': 'inj', "list":["1062118922147659776"]})
acc_list.append({'name': 'vet', "list":["908576143975919616"]})
acc_list.append({'name': 'iota', "list":["3992601857"]})
acc_list.append({'name': 'theta', "list": ["918994376105197568"]})
acc_list.append({'name': 'enj', "list":["20356963"]})
acc_list.append({'name': 'dot', "list":["1595615893"]})
acc_list.append({'name': 'coti', "list":["913327957904695297"]})
acc_list.append({'name': '1inch', "list":["1137038394503114753"]})
acc_list.append({'name': 'axs', "list":["957716432430641152"]})
acc_list.append({'name': 'ankr', "list":["1010430329218371584"]})
acc_list.append({'name': 'algo', "list":["1090346259892838400" ]})
acc_list.append({'name': 'aave', "list":["867100084248469505"]})
acc_list.append({'name': 'audio', "list":[ "1019723274693926912"]})
acc_list.append({'name': 'ar', "list":["892752981736779776"]})
acc_list.append({'name': 'ant', "list":["828668619986964480"]})
acc_list.append({'name': 'bnb', "list":["877807935493033984", "1052454006537314306", "902926941413453824"]})
acc_list.append({'name': 'chz', "list":["2590633042"]})
acc_list.append({'name': 'eos', "list":["862675563693125632"]})
acc_list.append({'name': 'etc', "list":["759252279862104064"]})
acc_list.append({'name': 'egld', "list": ["986967941685153792"]})
acc_list.append({'name': 'fil', "list":["2653394250"]})
acc_list.append({'name': 'gala', "list":["1288572182444961793"]})
acc_list.append({'name': 'hot', "list":["806968755855224832"]})
acc_list.append({'name': 'icp', "list":["799071635231817729"]})
acc_list.append({'name': 'ltc', "list":["385562752",]})
acc_list.append({'name': 'mana', "list":["3291830170"]})
acc_list.append({'name': 'mir', "list":["1334427533064855552"]})
acc_list.append({'name': 'rvn', "list":["910233733265018880"]})
acc_list.append({'name': 'super', "list":["1350220454674329600"]})
acc_list.append({'name': 'sand', "list":["347831597"]})
acc_list.append({'name': 'uni', "list":["984188226826010624"]})
acc_list.append({'name': 'win', "list":["1384448886627049474"]})
acc_list.append({'name': 'xrp', "list":["1051053836", "1179233381126529025"]})
acc_list.append({'name': 'xmr', "list":["2478439963"]})
acc_list.append({'name': 'xlm', "list":["2460502890"]})
acc_list.append({'name': 'zil', "list":["872984298973941764"]})
acc_list.append({'name': 'ape', "list":["1381699264011771906", "1489018530511175681"]})


def fix_time():

    tz = pytz.timezone("Europe/Sofia")
    tim = tz.localize(datetime.now(), is_dst=None)
    tim = str(tim)
    tim = tim[:-7]
    tim = re.sub(':', '', tim)
    tim = re.sub('-', '', tim)
    tim = re.sub(' ', '', tim)

    return tim

def deEmojify(text):

    # text = re.sub('#', '', text)
    text = text.strip('\n')
    text = text.strip('\t')
    text = re.sub('\n', '', text)
    text = re.sub('\t', '', text)
    text = re.sub(r'http\S+', '', text)

    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               "]+", flags=re.UNICODE)

    return emoji_pattern.sub(r'',text)


def contains_help(w):
  return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search


def contains(words, text, strict):
    if strict:
        for word in words:
            if contains_help(word)(text):
                return True
        return False
    else:
        for word in words:
            if word in text:
                return True
        return False


def breaking_text(text):

    text = re.sub('#', '', text)
    text = re.sub('rt', '', text)
    text = text.strip('\n')
    text = text.strip('\t')
    text = re.sub('\n', '', text)
    text = re.sub('\t', '', text)
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'@\S+', '', text)
    text = re.sub(r'rt\S+', '', text)

    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               "]+", flags=re.UNICODE)

    return emoji_pattern.sub(r'',text)


# acc_list = []
# acc_list.append({'name': 'ada', "list":["825920479055671296", "4135644558", "1393007027698298881", "7838552", "1056517943117398018", "1257557583335796736", "1376161898", "868997091871215616","1429577698687557633"]})
# acc_list.append({'name': 'luna', "list":["1406995344483704832", "1022028994772910086", "1352473582438395906", "960068923759751168", "357317524", "1491939578323906564"]})
# acc_list.append({'name': 'eth', "list":["2312333412", "295218901", "202806809"]})
# acc_list.append({'name': 'near', "list":["1031949518609121280", "1387456369398140931"]})
# acc_list.append({'name': 'atom', "list": ["15223775", "1334653878940393477", "1445457674305347584", "1218624618904182789", "64954849"]})
# acc_list.append({'name': 'avax', "list":["22325121", "1390321458140778499", "1419074643277885444", "995834351316324352", "399412477", "1275068809699708931", "1055894724245155841"]})
# acc_list.append({'name': 'ftm', "list":["977020204071792641", "392138654", "332315952"]})
# acc_list.append({'name': 'one', "list":["1006055524666826754", "14086060"]})
# acc_list.append({'name': 'ksm', "list":["1141423436671201282", "33962758"]})
# acc_list.append({'name': 'matic', "list":["914738730740715521", "1321398370104004608", "100798845", "1399547419658919937", "1400489811211915268"]})
# acc_list.append({'name': 'sol', "list":["951329744804392960", "1407411848446611459", "1419653495611875330", "2327407569"]})
# acc_list.append({'name': 'inj', "list":["1062118922147659776", "2220273336"]})
# acc_list.append({'name': 'vet', "list":["908576143975919616", "281349131", "945998026392424448", "1163459866473771009","1182882288645787648"]})
# acc_list.append({'name': 'iota', "list":["3992601857", "1020946242967408640", "2394950336","2739265466","822438166992945152"]})
# acc_list.append({'name': 'theta', "list": ["918994376105197568", "762701130325299200", "283425089", "14074187"]})
# acc_list.append({'name': 'enj', "list":["20356963", "1402179580371341317", "197839140", "963935404784107520"]})
# acc_list.append({'name': 'dot', "list":["1595615893", "1169145165531013120", "33962758", "1256574541884723200", "1345029651673079810"]})
# acc_list.append({'name': 'coti', "list":["913327957904695297", "32860795"]})
# acc_list.append({'name': '1inch', "list":["1137038394503114753", "20413564", "62759320"]})
# acc_list.append({'name': 'axs', "list":["957716432430641152", "1395394948158033923", "2731277064"]})
# acc_list.append({'name': 'ankr', "list":["1010430329218371584", "192941516"]})
# acc_list.append({'name': 'algo', "list":["1090346259892838400", "1451240967277735939", "960898464497459200", "1462848840902586374"]})
# acc_list.append({'name': 'aave', "list":["867100084248469505", "952921795316912133"]})
# acc_list.append({'name': 'audio', "list":["372120119", "1019723274693926912"]})
# acc_list.append({'name': 'ar', "list":["892752981736779776", "1346968828849348609", "409642632"]})
# acc_list.append({'name': 'alice', "list":["1329587028632219648"]})
# acc_list.append({'name': 'ant', "list":["828668619986964480"]})
# acc_list.append({'name': 'bnb', "list":["877807935493033984", "1052454006537314306", "902926941413453824"]})
# acc_list.append({'name': 'chz', "list":["2590633042", "1001022572186820608", "33939145"]})
# acc_list.append({'name': 'eos', "list":["862675563693125632", "1356561007313702912", "1074128622083104768", "289093913"]})
# acc_list.append({'name': 'etc', "list":["759252279862104064", "999916823964368896"]})
# acc_list.append({'name': 'egld', "list": ["986967941685153792", "1269619435343687682", "287309941", "1305072919635283968", "1337319763563982854", "1392307531"]})
# acc_list.append({'name': 'fil', "list":["2653394250", "1302398882186366976", "1382776886544248833", "15461779"]})
# acc_list.append({'name': 'gala', "list":["1288572182444961793"]})
# acc_list.append({'name': 'hot', "list":["806968755855224832", "14205457"]})
# acc_list.append({'name': 'icp', "list":["799071635231817729", "5663192"]})
# acc_list.append({'name': 'ltc', "list":["385562752", "1393174363", "1656328279", "14338147"]})
# acc_list.append({'name': 'mana', "list":["3291830170", "30473929", "1210170414"]})
# acc_list.append({'name': 'mir', "list":["1334427533064855552"]})
# acc_list.append({'name': 'rvn', "list":["910233733265018880", "1346392219780063234", "111729807", "260767065"]})
# acc_list.append({'name': 'super', "list":["1350220454674329600"]})
# acc_list.append({'name': 'sand', "list":["347831597", "913705727360868352", "6718432"]})
# acc_list.append({'name': 'uni', "list":["984188226826010624", "702654540387127296"]})
# acc_list.append({'name': 'win', "list":["1384448886627049474", "1320992865141411840"]})
# acc_list.append({'name': 'xrp', "list":["1051053836", "35749949", "1179233381126529025", "28582680", "23137860"]})
# acc_list.append({'name': 'xmr', "list":["2478439963", "386728215"]})
# acc_list.append({'name': 'xlm', "list":["2460502890", "3194838079"]})
# acc_list.append({'name': 'zil', "list":["872984298973941764"]})
# acc_list.append({'name': 'ape', "list":["1381699264011771906", "1489018530511175681"]})