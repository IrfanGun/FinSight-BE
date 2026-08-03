class UnitOfWork:
    def __init__(self, repository):
        self.repository = repository

    def commit(self):
        self.repository.commit()

    def rollback(self):
        self.repository.db.rollback()
