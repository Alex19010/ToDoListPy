from sqlalchemy import Engine, text

class DBManager():

    def __init__(self, engine: Engine):
        self.engine = engine


    def _create_user(self):
        with self.engine.connect() as connecion:
            user = """
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY auto_increment NOT NULL, 
                username VARCHAR(100), 
                email VARCHAR(100) UNIQUE, 
                first_name VARCHAR(100),
                last_name VARCHAR(100),
                phone_number VARCHAR(100),
                is_active BOOL DEFAULT true,
                registered DATETIME DEFAULT now()
            );
            """
            connecion.execute(text(user))


    def _create_data(self):
        with self.engine.connect() as connection:
            data = """
            CREATE TABLE IF NOT EXISTS data (
                id INTEGER PRIMARY KEY auto_increment,
                user_id INTEGER NOT NULL,
                name VARCHAR(100) NOT NULL,
                note TEXT NOT NULL,
                is_completed BOOL DEFAULT false,
                FOREIGN KEY (user_id) REFERENCES user(id)
            );
            """
            connection.execute(text(data))


    def create_table(self):
        self._create_user()
        self._create_data()


    def reg_user(self, user_id):
        with self.engine.connect() as connection:
            request = f"SELECT id FROM user WHERE id = {user_id};"
            result = connection.execute(text(request))
        return result

    
    def insert_user(self, data:dict):
        with self.engine.connect() as connection:
            keys_ = ", ".join(data.keys())
            values_ = ", ".join(data.values())
            request = f"INSERT INTO user ({keys_}) VALUES ({values_});"
            connection.execute(text(request))
            connection.commit()

    
    def insert_new_note(self, data:dict):
        with self.engine.connect() as connection:
            keys_ = ", ".join(data.keys())
            values_ = ", ".join(data.values())
            request = f"INSERT INTO data ({keys_}) VALUES ({values_});"
            connection.execute(text(request))
            connection.commit()


    def select_datas(self, *params):
        with self.engine.connect() as connection:
            if not params:
                request = "SELECT * FROM data;"
            else:
                params = ", ".join(params)
                request = f"SELECT {params} FROM data;"
            result = connection.execute(text(request))
        return result
    

    def select_data(self, data_id, *params):
        with self.engine.connect() as connection:
            if not params:
                request = f"SELECT * FROM data WHERE id={data_id};"
            else:
                params = ", ".join(params)
                request = f"SELECT {params} FROM data WHERE id={data_id};"
            result = connection.execute(text(request))
        return result
    

    def delate_data(self, data_id):
        with self.engine.connect() as connection:
            request = f"DELETE FROM data WHERE id = {data_id};"
            connection.execute(text(request))
            connection.commit()