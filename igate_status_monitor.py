import mysql.connector
import aprslib
import yaml

with open("configuration.yaml", 'r') as stream:
    configuration = yaml.safe_load(stream)

db = mysql.connector.connect(
    host=configuration['mysql']['hostname'],
    user=configuration['mysql']['username'],
    password=configuration['mysql']['password'],
    database=configuration['mysql']['database']
)

target_call_signs = []
crs = db.cursor()
crs.execute("SELECT * FROM `call_signs`;")
result = crs.fetchall()
for call_sign in result:
    target_call_signs.append(call_sign[1])


def callback(packet):
    try:
        parsed = aprslib.parse(packet)
    except (aprslib.ParseError, aprslib.UnknownFormat) as exp:
        return

    test_call_signs = list()
    test_call_signs.append(parsed.get('from'))
    test_call_signs = [*test_call_signs, *parsed.get('path')]
    intersection = list(set(test_call_signs) & set(target_call_signs))
    if len(intersection) > 0:
        for call_sign in intersection:
            crs = db.cursor()
            crs.execute("SELECT * FROM `call_signs` WHERE `value` = %s;", (call_sign,))
            call_sign_db = crs.fetchone()

            if call_sign_db:
                crs = db.cursor()
                crs.execute(
                    "INSERT INTO `status`(`call_sign_id`, `date_last_heard`, `path`, `date_refreshed`) VALUES(%s, NOW(), %s, NOW()) ON DUPLICATE KEY UPDATE `date_last_heard`=NOW(), `path` = %s, `date_refreshed` = NOW();",
                    (call_sign_db[0], ','.join(parsed.get('path')), ','.join(parsed.get('path'))))

                #print(call_sign + " saved")


AIS = aprslib.IS(configuration['aprs']['callsign'], passwd="-1", host=configuration['aprs']['host'], port=14580)
AIS.set_filter(configuration['aprs']['filter'])
AIS.connect()
AIS.consumer(callback, raw=True)
