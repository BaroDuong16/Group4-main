from django.db import models

class ModuleGroup(models.Model):
    group_name = models.CharField(max_length=255)
    
    def __str__(self):
        return self.group_name

class Module(models.Model):
    module_name = models.CharField(max_length=255)
    module_url = models.CharField(max_length=255)
    icon = models.CharField(max_length=255, blank=True, null=True)
    module_group = models.ForeignKey(ModuleGroup, related_name='modules', on_delete=models.CASCADE)

    def __str__(self):
        return self.module_name
