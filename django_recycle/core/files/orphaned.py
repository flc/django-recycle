import os
import logging


logger = logging.getLogger(__name__)


def get_paths(model, field_name, dirname):
    storage = model._meta.get_field(field_name).storage
    dirpath = storage.path(dirname)
    for (dirpath, dirs, files) in os.walk(dirpath):
        for file in files:
            path = os.path.join(dirpath, file)
            rel_file_path = os.path.join(dirname, path.split(os.path.join(dirname, ""))[-1])
            yield path, rel_file_path


def get_orphaned_files_generator(model, field_name, dirname, extra_filter_kwargs=None):
    if extra_filter_kwargs is None:
        extra_filter_kwargs = {}

    paths = get_paths(model, field_name, dirname)
    for path, rel_file_path in paths:
        filter_kwargs = {field_name: rel_file_path}
        extra_filter_kwargs.update(filter_kwargs)
        if not model._default_manager.filter(**extra_filter_kwargs).exists():
            yield rel_file_path, path


def delete_orphaned_files(model, field_name, dirname):
    deleted_files = []
    for rel_file_path, path in get_orphaned_files_generator(model, field_name, dirname):
        if os.path.isfile(path):
            logger.info("deleting orphaned file: %s (field: %s.%s)", path, model.__name__, field_name)
            os.remove(path)
            deleted_files.append(path)

    return deleted_files
