from django.db import models

class TestManager(models.Manager):

    def create_test(self, *args, **kwargs):
        new_test = self.model(gr='GRRRR')
        return new_test



class Test(models.Model):
    source = models.CharField(max_length=10)
    gr = models.CharField(max_length=10)

    @property
    def objects(self):
        if self.source == 'ha':
            print('hahahahah')
            return  TestManager()

