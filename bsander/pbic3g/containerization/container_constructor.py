import os.path
import re

from bsander.bsandr_utils.input_types import ProgramArguments
from bsander.pbic3g.containerization.container_file import get_generic_dockerfile_template, pull_substitution_keys_from_document

def build_dockerfile_for_necessary_env(program_arguments: ProgramArguments) -> str:
    docker_template: str = get_generic_dockerfile_template()
    pb_document_str: str
    with open(program_arguments.input_file_path, "r") as pb_document_file:
        pb_document_str = pb_document_file.read()
    for desired_field in generate_necessary_values():
        pypi_deps, conda_deps = determine_dependencies(pb_document_str)
        match_target: str = "$${#" + desired_field + "}"
        if "PYPI_DEPENDENCIES" == desired_field:
            if len(pypi_deps) == 0:
                docker_template = docker_template.replace(match_target, "# No PyPI dependencies!")
                continue
            pypi_section = \
"""
RUN echo "$${#DEPENDENCIES}" >> requirements.txt
RUN python3 -m pip install -r requirements.txt
""".strip()
            dependency_str = convert_dependencies_to_installation_string_representation(pypi_deps)
            filled_section = pypi_section.replace("$${#DEPENDENCIES}", dependency_str)
            docker_template = docker_template.replace(match_target, filled_section)
        elif "CONDA_FORGE_DEPENDENCIES" == desired_field:
            if len(conda_deps) == 0:
                docker_template = docker_template.replace(match_target, "# No conda dependencies!")
                continue
            conda_section = \
"""
RUN mkdir /micromamba
RUN curl -Ls https://micro.mamba.pm/api/micromamba/linux-64/latest | tar -xvj bin/micromamba
RUN mv bin/micromamba /usr/local/bin/
RUN micromamba create -y -p /opt/conda -c conda-forge $${#DEPENDENCIES} python=3.12
ENV PATH=/opt/conda/bin:$PATH
""".strip()
            dependency_str = " ".join(conda_deps)
            filled_section = conda_section.replace("$${#DEPENDENCIES}", dependency_str)
            docker_template = docker_template.replace(match_target, filled_section)
        else:
            raise ValueError(f"unknown field in template dockerfile: {desired_field}")

    dockerfile_path: str = os.path.join(program_arguments.output_dir, "Dockerfile")
    with open(dockerfile_path, "w") as docker_file:
        docker_file.write(docker_template)
    return dockerfile_path


def generate_necessary_values() -> list[str]:
    return pull_substitution_keys_from_document()

# Due to an assumption that we can not have all dependencies included
# in the same python environment, we need a solid address protocol to assume.
# going with: `pypi:<package_name>[<version_statement>]@<python_module_path_to_class_def>`
#         ex: "pypi:copasi-basico[~0.8]@basico.model_io.load_model" (if this was a class, and not a function)
def determine_dependencies(search_string: str) -> tuple[list[str],list[str]]:
    pypi_dependencies: list[str] = []
    conda_dependencies: list[str] = []
    package_name_legal_syntax = r"[\w\-.]+" # Alphanumeric plus '-' and '.'; must be one or more characters total
    version_string_legal_syntax = r"\[([\w><=~!*\-.]+)]" # hard brackets around alphanumeric plus standard python version contraint characters
    import_name_legal_syntax = r"[A-Za-z_]\w*(\.[A-Za-z_]\w*)*" # stricter pattern of only legal python module names (letters and underscore first character, alphanumeric and underscore for remainder); must be at least 1 char long
    for match in re.findall(f"pypi:({package_name_legal_syntax})({version_string_legal_syntax})?@({import_name_legal_syntax})", search_string):
        package_name = match[0]
        package_version = match[2]
        pypi_dependencies.append(f"{package_name}{package_version}".strip())
    for match in re.findall(f"conda:({package_name_legal_syntax})({version_string_legal_syntax})?@({import_name_legal_syntax})", search_string):
        package_name = match[0]
        package_version = match[2]
        conda_dependencies.append(f"{package_name}{package_version}".strip())
    return pypi_dependencies, conda_dependencies

def convert_dependencies_to_installation_string_representation(dependencies: list[str]) -> str:
    return "'"+ "' '".join(dependencies) + "'"
