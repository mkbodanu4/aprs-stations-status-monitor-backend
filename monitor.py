import mysql.connector
import aprslib
import yaml
import logging
import time

with open("configuration.yaml", 'r') as stream:
    configuration = yaml.safe_load(stream)

logging.basicConfig(level=configuration['logging']['level'])

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
last_targets_update = 0


def update_targets():
    global target_call_signs, last_targets_update

    target_call_signs = []
    crs = db.cursor()
    crs.execute("SELECT `value` FROM `call_signs`;")
    result = crs.fetchall()
    for call_sign in result:
        target_call_signs.append(call_sign[0])
    crs.close()

    logging.info("Target call signs list updated")
    last_targets_update = time.time()


def callback(packet):
    global last_targets_update

    if (time.time() - last_targets_update) > 60:
        update_targets()

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
                # If packet From is equal to target call sign, then record beacons...
                if parsed.get('from') == call_sign:
                    if parsed.get('format') == 'uncompressed' or parsed.get('format') == 'compressed':
                        query = """
                            INSERT INTO
                                `positions` (
                                    `call_sign_id`,
                                    `date`,
                                    `from`,
                                    `path`,
                                    `symbol_table`,
                                    `symbol`,
                                    `latitude`,
                                    `longitude`,
                                    `comment`,
                                    `raw`
                                )
                            VALUES
                                (
                                    %s,
                                    UTC_TIMESTAMP(),
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s
                                )
                            ON DUPLICATE KEY
                                UPDATE
                                    `date`=UTC_TIMESTAMP(),
                                    `from` = %s,
                                    `path` = %s,
                                    `symbol_table` = %s,
                                    `symbol` = %s,
                                    `latitude` = %s,
                                    `longitude` = %s,
                                    `comment` = %s,
                                    `raw` = %s
                        ;"""
                        params = (
                            call_sign_db[0],
                            parsed.get('from'),
                            ','.join(parsed.get('path')),
                            parsed.get('symbol_table'),
                            parsed.get('symbol'),
                            parsed.get('latitude'),
                            parsed.get('longitude'),
                            parsed.get('comment'),
                            parsed.get('raw'),
                            parsed.get('from'),
                            ','.join(parsed.get('path')),
                            parsed.get('symbol_table'),
                            parsed.get('symbol'),
                            parsed.get('latitude'),
                            parsed.get('longitude'),
                            parsed.get('comment'),
                            parsed.get('raw')
                        )

                        crs = db.cursor()
                        crs.execute(query, params)
                        db.commit()
                        crs.close()
                        logging.info("Call sign " + call_sign + " position saved")
                    elif parsed.get('format') == 'telemetry-message':
                        query = """
                            INSERT INTO
                                `telemetry` (
                                    `call_sign_id`,
                                    `date`,
                                    `from`,
                                    `path`,
                                    `comment`,
                                    `raw`
                                )
                            VALUES
                                (
                                    %s,
                                    UTC_TIMESTAMP(),
                                    %s,
                                    %s,
                                    %s,
                                    %s
                                )
                            ON DUPLICATE KEY
                                UPDATE
                                    `date`=UTC_TIMESTAMP(),
                                    `from` = %s,
                                    `path` = %s,
                                    `comment` = %s,
                                    `raw` = %s
                        ;"""
                        params = (
                            call_sign_db[0],
                            parsed.get('from'),
                            ','.join(parsed.get('path')),
                            parsed.get('comment'),
                            parsed.get('raw'),
                            parsed.get('from'),
                            ','.join(parsed.get('path')),
                            parsed.get('comment'),
                            parsed.get('raw')
                        )

                        crs = db.cursor()
                        crs.execute(query, params)
                        db.commit()
                        crs.close()
                        logging.info("Call sign " + call_sign + " telemetry saved")
                    elif parsed.get('format') == 'wx':
                        query = """
                            INSERT INTO
                                `weather` (
                                    `call_sign_id`,
                                    `date`,
                                    `from`,
                                    `path`,
                                    `symbol_table`,
                                    `symbol`,
                                    `latitude`,
                                    `longitude`,
                                    `comment`,
                                    `raw`
                                )
                            VALUES
                                (
                                    %s,
                                    UTC_TIMESTAMP(),
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s
                                )
                            ON DUPLICATE KEY
                                UPDATE
                                    `date`=UTC_TIMESTAMP(),
                                    `from` = %s,
                                    `path` = %s,
                                    `symbol_table` = %s,
                                    `symbol` = %s,
                                    `latitude` = %s,
                                    `longitude` = %s,
                                    `comment` = %s,
                                    `raw` = %s
                        ;"""
                        params = (
                            call_sign_db[0],
                            parsed.get('from'),
                            ','.join(parsed.get('path')),
                            parsed.get('symbol_table'),
                            parsed.get('symbol'),
                            parsed.get('latitude'),
                            parsed.get('longitude'),
                            parsed.get('comment'),
                            parsed.get('raw'),
                            parsed.get('from'),
                            ','.join(parsed.get('path')),
                            parsed.get('symbol_table'),
                            parsed.get('symbol'),
                            parsed.get('latitude'),
                            parsed.get('longitude'),
                            parsed.get('comment'),
                            parsed.get('raw')
                        )

                        crs = db.cursor()
                        crs.execute(query, params)
                        db.commit()
                        crs.close()
                        logging.info("Call sign " + call_sign + " object saved")
                    elif parsed.get('format') == 'object':
                        query = """
                            INSERT INTO
                                `objects` (
                                    `call_sign_id`,
                                    `date`,
                                    `from`,
                                    `object`,
                                    `path`,
                                    `symbol_table`,
                                    `symbol`,
                                    `latitude`,
                                    `longitude`,
                                    `comment`,
                                    `raw`
                                )
                            VALUES
                                (
                                    %s,
                                    UTC_TIMESTAMP(),
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s
                                )
                            ON DUPLICATE KEY
                                UPDATE
                                    `date`=UTC_TIMESTAMP(),
                                    `from` = %s,
                                    `object` = %s,
                                    `path` = %s,
                                    `symbol_table` = %s,
                                    `symbol` = %s,
                                    `latitude` = %s,
                                    `longitude` = %s,
                                    `comment` = %s,
                                    `raw` = %s
                        ;"""
                        params = (
                            call_sign_db[0],
                            parsed.get('from'),
                            parsed.get('object_name'),
                            ','.join(parsed.get('path')),
                            parsed.get('symbol_table'),
                            parsed.get('symbol'),
                            parsed.get('latitude'),
                            parsed.get('longitude'),
                            parsed.get('comment'),
                            parsed.get('raw'),
                            parsed.get('from'),
                            parsed.get('object_name'),
                            ','.join(parsed.get('path')),
                            parsed.get('symbol_table'),
                            parsed.get('symbol'),
                            parsed.get('latitude'),
                            parsed.get('longitude'),
                            parsed.get('comment'),
                            parsed.get('raw')
                        )

                        crs = db.cursor()
                        crs.execute(query, params)
                        db.commit()
                        crs.close()
                        logging.info("Call sign " + call_sign + " object saved")
                    elif parsed.get('format') == 'status':
                        query = """
                            INSERT INTO
                                `status` (
                                    `call_sign_id`,
                                    `date`,
                                    `from`,
                                    `path`,
                                    `symbol_table`,
                                    `symbol`,
                                    `latitude`,
                                    `longitude`,
                                    `comment`,
                                    `raw`
                                )
                            VALUES
                                (
                                    %s,
                                    UTC_TIMESTAMP(),
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s
                                )
                            ON DUPLICATE KEY
                                UPDATE
                                    `date`=UTC_TIMESTAMP(),
                                    `from` = %s,
                                    `path` = %s,
                                    `symbol_table` = %s,
                                    `symbol` = %s,
                                    `latitude` = %s,
                                    `longitude` = %s,
                                    `comment` = %s,
                                    `raw` = %s
                        ;"""
                        params = (
                            call_sign_db[0],
                            parsed.get('from'),
                            ','.join(parsed.get('path')),
                            parsed.get('symbol_table'),
                            parsed.get('symbol'),
                            parsed.get('latitude'),
                            parsed.get('longitude'),
                            parsed.get('comment'),
                            parsed.get('raw'),
                            parsed.get('from'),
                            ','.join(parsed.get('path')),
                            parsed.get('symbol_table'),
                            parsed.get('symbol'),
                            parsed.get('latitude'),
                            parsed.get('longitude'),
                            parsed.get('comment'),
                            parsed.get('raw')
                        )

                        crs = db.cursor()
                        crs.execute(query, params)
                        db.commit()
                        crs.close()
                        logging.info("Call sign " + call_sign + " object saved")
                else:  # otherwise record IGate routing...
                    query = """
                        INSERT INTO
                            `routing` (
                                `call_sign_id`,
                                `date`,
                                `from`,
                                `path`,
                                `symbol_table`,
                                `symbol`,
                                `latitude`,
                                `longitude`,
                                `comment`,
                                `raw`
                            )
                        VALUES
                            (
                                %s,
                                UTC_TIMESTAMP(),
                                %s,
                                %s,
                                %s,
                                %s,
                                %s,
                                %s,
                                %s,
                                %s
                            )
                        ON DUPLICATE KEY
                            UPDATE
                                `date`=UTC_TIMESTAMP(),
                                `from` = %s,
                                `path` = %s,
                                `symbol_table` = %s,
                                `symbol` = %s,
                                `latitude` = %s,
                                `longitude` = %s,
                                `comment` = %s,
                                `raw` = %s
                    ;"""
                    params = (
                        call_sign_db[0],
                        parsed.get('from'),
                        ','.join(parsed.get('path')),
                        parsed.get('symbol_table'),
                        parsed.get('symbol'),
                        parsed.get('latitude'),
                        parsed.get('longitude'),
                        parsed.get('comment'),
                        parsed.get('raw'),
                        parsed.get('from'),
                        ','.join(parsed.get('path')),
                        parsed.get('symbol_table'),
                        parsed.get('symbol'),
                        parsed.get('latitude'),
                        parsed.get('longitude'),
                        parsed.get('comment'),
                        parsed.get('raw')
                    )

                    crs = db.cursor()
                    crs.execute(query, params)
                    db.commit()
                    crs.close()
                    logging.info("Call sign " + call_sign + " routing activity saved")
            else:
                logging.warning("Call sign " + call_sign + " not found in database")
    else:
        if len(parsed.get('path')) >= 2:
            q = parsed.get('path')[-2]
            if q in ['qAR', 'qAO', 'qAo']:
                query = """
                        INSERT INTO
                            `proposals` (
                                `call_sign`,
                                `date`,
                                `from`,
                                `path`,
                                `comment`
                            )
                        VALUES
                            (
                                %s,
                                UTC_TIMESTAMP(),
                                %s,
                                %s,
                                %s
                            )
                        ON DUPLICATE KEY
                            UPDATE
                                `from`= %s,
                                `path`= %s,
                                `comment`= %s
                    ;"""
                params = (
                    parsed.get('via'),
                    parsed.get('from'),
                    ','.join(parsed.get('path')),
                    parsed.get('comment'),
                    parsed.get('from'),
                    ','.join(parsed.get('path')),
                    parsed.get('comment')
                )

                crs = db.cursor()
                crs.execute(query, params)
                db.commit()
                crs.close()

                logging.info("Call sign " + parsed.get('via') + " saved to proposals")
            else:
                logging.info("Call sign " + ', '.join(test_call_signs) + " ignored")
        else:
            logging.info("Call signs " + ', '.join(test_call_signs) + " ignored")


AIS = aprslib.IS(configuration['aprs']['callsign'], passwd="-1", host=configuration['aprs']['host'], port=14580)
AIS.set_filter(configuration['aprs']['filter'])
AIS.connect()
AIS.consumer(callback, raw=True)
