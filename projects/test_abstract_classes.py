from django.db import connection
from django.test import TestCase
from django.db.models.base import ModelBase


class ModelMixinTestCase(TestCase):
    '''
    Base class for tests of model mixins. To use, subclass and specify the
    mixin class variable. A model using the mixin will be made available in
    self.model
    '''
    @classmethod
    def setUpClass(cls):
        # Create a dummy model which extends the mixin
        cls.model = ModelBase('__TestModel__' +
            cls.mixin.__name__, (cls.mixin,),
            {'__module__': cls.mixin.__module__}
        )

        # Create the schema for  our test model
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(cls.model)
        super(ModelMixinTestCase, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        # Delete the schema for the test model
        with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(cls.model)
        super(ModelMixinTestCase, cls).tearDownClass()
