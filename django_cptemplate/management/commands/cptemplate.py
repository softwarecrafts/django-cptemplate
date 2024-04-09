from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from pathlib import Path
from shutil import copy2

from django.apps import apps

from django.template import loader


def get_template_absolute_path(template_path):
    try:
        template = loader.get_template(template_path)
        return template.origin.name
    except Exception as e:
        print(f"Error occurred while getting template path: {e}")
        return None


class Command(BaseCommand):
    help = "Copies a template from a package into your project"

    def add_arguments(self, parser):
        parser.add_argument("source", type=str)
        parser.add_argument("destination", type=str, nargs="?")

    def handle(self, *args, **options):
        print(options)
        # 1. extract the options
        source = options["source"]
        destination = options.get("destination")
        # 2. Check that the source file exists - use template loaders for this
        source_file = get_template_absolute_path(source)
        if source_file is None:
            self.stdout.write(self.style.ERROR("Source Template doesn’t exist"))
            return
        # 4. if destination, then create Path object and copy
        if destination is not None:
            app_config = apps.get_app_config(destination)
            destination_path = (
                settings.BASE_DIR / app_config.path / "templates" / source
            )
        # 5/ else inspect TEMPLATES[DIRS] setting and use first option if avaiable
        else:
            try:
                destination_path = settings.TEMPLATES[0]["DIRS"][0] / source
            except IndexError:
                # 6/ otherwise create project level template directory and dump file there.
                destination_path = settings.BASE_DIR / "templates" / source
                # PRINT what settings need to be modified
                self.stdout.write(
                    self.style.WARNING(
                        'Update TEMPLATES["DIRS"] to include the follow entry "BASE_DIR / "templates","'
                    )
                )
        destination_path.parent.mkdir(parents=True)
        copy2(source_file, destination_path)
