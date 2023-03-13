import logging

import borgmatic.borg.extract
import borgmatic.borg.rlist
import borgmatic.config.validate
import borgmatic.hooks.command
import borgmatic.hooks.dispatch
import borgmatic.hooks.prepare

logger = logging.getLogger(__name__)


def run_extract(
    config_filename,
    repository,
    location,
    storage,
    hooks,
    hook_context,
    local_borg_version,
    extract_arguments,
    global_arguments,
    local_path,
    remote_path,
):
    '''
    Run the "extract" action for the given repository.
    '''
    borgmatic.hooks.command.execute_hook(
        hooks.get('before_extract'),
        hooks.get('umask'),
        config_filename,
        'pre-extract',
        global_arguments.dry_run,
        **hook_context,
    )
    if extract_arguments.repository is None or borgmatic.config.validate.repositories_match(
        repository, extract_arguments.repository
    ):
        logger.info(
            f'{repository.get("label", repository["path"])}: Extracting archive {extract_arguments.archive}'
        )
        borgmatic.borg.extract.extract_archive(
            global_arguments.dry_run,
            repository['path'],
            borgmatic.borg.rlist.resolve_archive_name(
                repository['path'],
                extract_arguments.archive,
                storage,
                local_borg_version,
                global_arguments,
                local_path,
                remote_path,
            ),
            extract_arguments.paths,
            location,
            storage,
            local_borg_version,
            global_arguments,
            local_path=local_path,
            remote_path=remote_path,
            destination_path=extract_arguments.destination,
            strip_components=extract_arguments.strip_components,
            progress=extract_arguments.progress,
        )
    borgmatic.hooks.dispatch.call_hooks(
        'fix_extracted_dirs',
        hooks,
        repository,
        borgmatic.hooks.prepare.PREPARE_HOOK_NAMES,
        location['source_directories'],
        extract_arguments.destination,
    )
    borgmatic.hooks.command.execute_hook(
        hooks.get('after_extract'),
        hooks.get('umask'),
        config_filename,
        'post-extract',
        global_arguments.dry_run,
        **hook_context,
    )
