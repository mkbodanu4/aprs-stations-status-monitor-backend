import mysql.connector
import aprslib
import yaml

with open("configuration.yaml", 'r') as stream:
    configuration = yaml.safe_load(stream)

if configuration['mysql']['unix_socket']:
    db = mysql.connector.connect(
        unix_socket=configuration['mysql']['unix_socket'],
        user=configuration['mysql']['username'],
        password=configuration['mysql']['password'],
        database=configuration['mysql']['database'],
    )
else:
    db = mysql.connector.connect(
        host=configuration['mysql']['hostname'],
        user=configuration['mysql']['username'],
        password=configuration['mysql']['password'],
        database=configuration['mysql']['database'],
    )

target_call_signs = []
crs = db.cursor()
crs.execute("SELECT * FROM `call_signs`;")
result = crs.fetchall()
for call_sign in result:
    target_call_signs.append(call_sign[1])
crs.close()


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
            crs.close()

            if call_sign_db:
                crs = db.cursor()
                crs.execute(
                    "INSERT INTO `status`(`call_sign_id`, `date_last_heard`, `path`, `date_refreshed`) VALUES(%s, UTC_TIMESTAMP(), %s, UTC_TIMESTAMP()) ON DUPLICATE KEY UPDATE `date_last_heard`=UTC_TIMESTAMP(), `path` = %s, `date_refreshed` = UTC_TIMESTAMP();",
                    (call_sign_db[0], ','.join(parsed.get('path')), ','.join(parsed.get('path'))))
                db.commit()
                crs.close()

                print(call_sign + " saved")
            else:
                print(call_sign + " ignored")
    else:
        print(parsed.get('from') + " ignored")


AIS = aprslib.IS(configuration['aprs']['callsign'], passwd="-1", host=configuration['aprs']['host'], port=14580)
AIS.set_filter(configuration['aprs']['filter'])
AIS.connect()
AIS.consumer(callback, raw=True)
