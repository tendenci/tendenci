from haystack import indexes
from haystack import site

from tendenci.core.perms.indexes import TendenciBaseSearchIndex

from tendenci.apps.architecture_projects.models import ArchitectureProject, Image

class ArchitectureProjectIndex(TendenciBaseSearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    client = indexes.CharField(model_attr='client')
    category = indexes.CharField(model_attr='categories')
    building_type = indexes.CharField(model_attr='building_types')

site.register(ArchitectureProject, ArchitectureProjectIndex)
site.register(Image)
