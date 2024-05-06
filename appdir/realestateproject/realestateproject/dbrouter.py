""" 
File to direct database operations for each model to the appropriate database.
"""
class DatabaseAppsRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'clientsApp':
            return 'clientDatadb'
        elif model._meta.app_label == 'listings':
            return 'listingsdb'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'clientsApp':
            return 'clientDatadb'
        elif model._meta.app_label == 'listings':
            return 'listingsdb'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'clientsApp':
            return db == 'clientDatadb'
        elif app_label == 'listings':
            return db == 'listingsdb'
        return None
