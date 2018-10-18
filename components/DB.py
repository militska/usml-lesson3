class DB:

    def db_process_one(row):
        if not row:
            return False
        zhost = row[7]

        try:
            connection = dbModule.Connection("db_login/db_pass")
        except dbModule.DatabaseError as exc:
            syslog.syslog("DB connection error: %s" % exc)
            return False

        try:
            cursor = connection.cursor()
            statTT = cursor.var(dbModule.STRING, 255)
            result = cursor.var(dbModule.NUMBER, 255)
            numTT = cursor.var(dbModule.NUMBER, 255)
            cursor.prepare("""BEGIN;
                procedure_one(:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11);
            ); END;""")
            row.append(result)
            row.append(numTT)
            row.append(statTT)
            cursor.execute(None, row)
            connection.commit()
            cursor.close()
            syslog.syslog("Insert data to db: %s" % row[0])
        except Exception as exc:
            syslog.syslog("Error while inserting to db: %s" % exc)
            return False

        event_num = re.search("\s*([0-9]+)", row[6]).group(1)
        resultTT = (int(row[-3].getvalue()),
                    int(row[-2].getvalue()), str(row[-1].getvalue()))

        syslog.syslog("Prepare ack one: %s" % row)
        return (zhost, event_num, resultTT)


    def db_process_two(row):
        if not row:
            return False
        zhost = row[7]
        try:
            connection = dbModule.Connection("db_login/db_pass")
        except dbModule.DatabaseError as exc:
            syslog.syslog("DB connection error: %s" % exc)
            return False

        try:
            cursor = connection.cursor()
            statTT = cursor.var(dbModule.STRING, 255)
            result = cursor.var(dbModule.NUMBER, 255)
            numTT = cursor.var(dbModule.NUMBER, 255)
            cursor.prepare("""BEGIN
            procedure_two(:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11);
            END;""")
            row.append(result)
            row.append(numTT)
            row.append(statTT)
            cursor.execute(None, row)
            connection.commit()
            cursor.close()
            syslog.syslog("Insert data to db: %s" % row[0])
        except Exception as exc:
            syslog.syslog("Error while inserting to db: %s" % exc)
            return False

        syslog.syslog(str(row))
        event_num = re.search("\s*([0-9]+)", row[3]).group(1)
        event_reg_num = row[-2].getvalue()
        if event_reg_num == None:
            event_reg_num = 0
        event_reg_status = str(row[-1].getvalue())
        resultTT = (int(event_reg_num), event_reg_status)
        syslog.syslog("Prepare ack two: %s" % row)
        return (zhost, event_num, resultTT)


    def db_process_three(row):
        if not row:
            return False
        try:
            connection = dbModule.Connection("db_login/db_pass")
        except dbModule.DatabaseError as exc:
            syslog.syslog("DB connection error: %s" % exc)
            return False

        try:
            cursor = connection.cursor()
            cursor.prepare("""BEGIN;
                procedure_three(:1, :2, :3);
                END;""")
            cursor.execute(None, row)
            connection.commit()
            syslog.syslog("Insert data to db: %s" % row[0])
        except Exception as exc:
            syslog.syslog("Error while inserting to db: %s" % exc)
            return False

        return True
