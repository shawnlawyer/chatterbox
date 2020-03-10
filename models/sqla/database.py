from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from envs import env

engine = create_engine('mysql+pymysql://{user}:{password}@{host}/{database}'.format(user=env('MYSQL_USER'),
                                                                                    password=env('MYSQL_PASSWORD'),
                                                                                    host=env('MYSQL_HOST'),
                                                                                    database=env('MYSQL_DATABASE')), convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()
