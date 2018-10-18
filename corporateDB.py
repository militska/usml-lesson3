class corporateDB:
    def __init__(self, url_in):
        self.connection = dbModule.Connection("login/password")
        self.cursor = self.connection.cursor()
        self.cursor.execute('''BEGIN
                            some_initial_procedure(%s);
                            END;''' % url_in)

    def telegram_procedure_exec(self, group, message):
        self.cursor.execute("""BEGIN
                        another_plsql_procedure(%s);
                        COMMIT;
                        END;""" % message, group=int(group), result_out=result_out, message_out=message_out)
        self.cursor.close()
        self.connection.commit()
        self.connection.close()
        return result_out.getvalue(), message_out.getvalue()