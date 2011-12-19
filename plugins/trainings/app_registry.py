from registry import site
from registry.base import PluginRegistry, lazy_reverse
from trainings.models import Training


class TrainingRegistry(PluginRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Create trainings type of content'

site.register(Training, TrainingRegistry)
