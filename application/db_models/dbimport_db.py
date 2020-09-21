from application.db_models.extenders_for_db_models import BaseExtended
from sqlalchemy import Column, Integer, String, Sequence, ForeignKey
from sqlalchemy.orm import relationship

class DBImport(BaseExtended):
    unique_search_field = 'import_date'

    __tablename__ = 'dbImports'
    id = Column(Integer, primary_key=True)
    import_date = Column(String(50), Sequence('dbimport_import_date_seq'), unique=True)  # update time in ms
    tracks = relationship('Track', lazy=True)
    num_tracks_added = Column(Integer)
    num_tracks_requested = Column(Integer)
    radio_name = Column(String(20), ForeignKey('radios.name'), nullable=False)

    def __repr__(self):
        return f"<dbImport({self.import_date}, {self.radio_name}, " \
               f"{self.num_tracks_added} vs {self.num_tracks_requested})>"

    @classmethod
    def get_imports_per_radio(cls, radio_name):
        res = (cls.session.query(cls).filter(cls.radio_name == radio_name)).all()
        cls.session.close()
        return cls.to_json(res)

    @classmethod
    def get_imports_per_radios(cls):
        imports = cls.session.query(cls).all()
        res = {}
        for db_import in imports:
            if db_import.radio_name in res.keys():
                res[db_import.radio_name].append(db_import)
            else:
                res[db_import.radio_name] = [db_import]
        cls.session.close()
        return res

    @classmethod
    def get_imports_num_per_radio(cls, radio_name):
        res = (cls.session.query(cls).filter(cls.radio_name == radio_name)).count()
        cls.session.close()
        return res

    @classmethod
    def get_imports_num_per_radios(cls):

        radios = [radio[0] for radio in cls.session.query(cls.radio_name).all()]
        res = {}
        for radio in radios:
            res[radio] = res[radio] + 1 if radio in res.keys() else 1

        cls.session.close()
        return res