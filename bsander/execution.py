import os

from bsander.bsandr_utils.experiment_archive import extract_pbif_from_archive
from bsander.bsandr_utils.input_types import ProgramArguments, ContainerizationTypes, ContainerizationEngine
from bsander.pbic3g.containerization.container_constructor import build_dockerfile_for_necessary_env
from bsander.pbic3g.local_registry import load_local_modules


def execute_bsander(original_program_arguments: ProgramArguments):
    new_input_file_path: None | str = None
    input_is_archive = original_program_arguments.input_file_path.endswith(
        ".zip") or original_program_arguments.input_file_path.endswith(".omex")
    required_program_arguments: ProgramArguments
    try:
        if input_is_archive:
            new_input_file_path = extract_pbif_from_archive(original_program_arguments.input_file_path,
                                                            original_program_arguments.output_dir)
            required_program_arguments = ProgramArguments(new_input_file_path, original_program_arguments.output_dir,
                                                          original_program_arguments.containerization_type,
                                                          original_program_arguments.containerization_engine)
        else:
            new_input_file_path = None
            required_program_arguments = original_program_arguments

        load_local_modules()  # Collect Abstracts
        # TODO: Add feature - resolve abstracts

        if required_program_arguments.containerization_type != ContainerizationTypes.NONE:
            if required_program_arguments.containerization_type != ContainerizationTypes.SINGLE:
                raise NotImplementedError("Only single containerization is currently supported")
            if required_program_arguments.containerization_engine != ContainerizationEngine.DOCKER:
                raise NotImplementedError("Only dockerfile implementation is currently supported")
            else:
                container_file_path: str
                container_file_path = build_dockerfile_for_necessary_env(required_program_arguments)
            print(f"Container build file located at '{container_file_path}'")
    finally:
        # cleanup
        if new_input_file_path is not None:
            os.remove(new_input_file_path)
