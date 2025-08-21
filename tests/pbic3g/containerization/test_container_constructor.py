import tempfile

from bsander.bsandr_utils.input_types import ContainerizationTypes, ContainerizationEngine
from bsander.pbic3g.containerization.container_constructor import *


def test_generate_necessary_values() -> None:
    results = generate_necessary_values()
    correct_answer = [ # update this as we add more fields!
        'CONDA_FORGE_DEPENDENCIES', 'PYPI_DEPENDENCIES'
    ]
    assert set(results) == set(correct_answer)

def test_determine_dependencies():
    mock_list = """
    `pypi:numpy[>=2.0.0]@numpy.random.rand`
    `pypi:process-bigraph[<1.0]@process_bigraph.processes.ParameterScan`
    `pypi:importlib@importlib.metadata.distribution`
    `conda:readdy@readdy.ReactionDiffusionSystem`
    """.strip()
    correct_answer = [
        'numpy>=2.0.0',
        'process-bigraph<1.0',
        'importlib',
    ], [ 'readdy' ]
    results = determine_dependencies(mock_list)
    assert results == correct_answer

def test_convert_dependencies_to_installation_string_representation():
    dependencies = [
        'numpy>=2.0.0',
        'process-bigraph<1.0',
        'importlib',
    ]
    results = convert_dependencies_to_installation_string_representation(dependencies)
    correct_answer = "'numpy>=2.0.0' 'process-bigraph<1.0' 'importlib'".strip()
    assert results == correct_answer

def _build_dockerfile_for_necessary_env_exec(correct_answer: str, fake_input_file: str):
    with tempfile.TemporaryDirectory() as tmpdir:
        with tempfile.NamedTemporaryFile(mode="w", dir=tmpdir, delete=False) as fake_target_file:
            fake_target_file.write(fake_input_file)
        test_args = ProgramArguments(fake_target_file.name, tmpdir, ContainerizationTypes.SINGLE, ContainerizationEngine.DOCKER)
        results_file_location = build_dockerfile_for_necessary_env(test_args)
        with open(results_file_location, "r") as results_file:
            results = results_file.read()
        assert results == correct_answer


def test_build_dockerfile_for_necessary_env_pypi_only() -> None:
    correct_answer = \
"""
FROM --platform=linux/amd64 ghcr.io/astral-sh/uv:python3.12-bookworm
SHELL ["bash", "-c"]

RUN apt update
RUN apt upgrade -y
RUN apt install -y git curl

## Dependency Installs
### Conda
# No conda dependencies!

### PyPI
RUN echo "'numpy>=2.0.0' 'process-bigraph<1.0'" >> requirements.txt
RUN python3 -m pip install -r requirements.txt

##
RUN mkdir /runtime
WORKDIR /runtime
RUN git clone https://github.com/biosimulators/bsew.git  /runtime
RUN python3 -m pip install -e /runtime

ENTRYPOINT ["python3", "/runtime/main.py"]
""".strip()
    fake_input_file = \
"""
"pypi:numpy[>=2.0.0]@numpy.random.rand"
"pypi:process-bigraph[<1.0]@process_bigraph.processes.ParameterScan"
""".strip()
    _build_dockerfile_for_necessary_env_exec(correct_answer, fake_input_file)

def test_build_dockerfile_for_necessary_env_both() -> None:
    correct_answer = \
"""
FROM --platform=linux/amd64 ghcr.io/astral-sh/uv:python3.12-bookworm
SHELL ["bash", "-c"]

RUN apt update
RUN apt upgrade -y
RUN apt install -y git curl

## Dependency Installs
### Conda
RUN mkdir /micromamba
RUN curl -Ls https://micro.mamba.pm/api/micromamba/linux-64/latest | tar -xvj bin/micromamba
RUN mv bin/micromamba /usr/local/bin/
RUN micromamba create -y -p /opt/conda -c conda-forge readdy python=3.12
ENV PATH=/opt/conda/bin:$PATH

### PyPI
RUN echo "'numpy>=2.0.0' 'process-bigraph<1.0'" >> requirements.txt
RUN python3 -m pip install -r requirements.txt

##
RUN mkdir /runtime
WORKDIR /runtime
RUN git clone https://github.com/biosimulators/bsew.git  /runtime
RUN python3 -m pip install -e /runtime

ENTRYPOINT ["python3", "/runtime/main.py"]
""".strip()
    fake_input_file = \
"""
"pypi:numpy[>=2.0.0]@numpy.random.rand"
"pypi:process-bigraph[<1.0]@process_bigraph.processes.ParameterScan"
`conda:readdy@readdy.ReactionDiffusionSystem`
""".strip()
    _build_dockerfile_for_necessary_env_exec(correct_answer, fake_input_file)


def test_build_dockerfile_for_necessary_env_conda() -> None:
    correct_answer = \
"""
FROM --platform=linux/amd64 ghcr.io/astral-sh/uv:python3.12-bookworm
SHELL ["bash", "-c"]

RUN apt update
RUN apt upgrade -y
RUN apt install -y git curl

## Dependency Installs
### Conda
RUN mkdir /micromamba
RUN curl -Ls https://micro.mamba.pm/api/micromamba/linux-64/latest | tar -xvj bin/micromamba
RUN mv bin/micromamba /usr/local/bin/
RUN micromamba create -y -p /opt/conda -c conda-forge readdy python=3.12
ENV PATH=/opt/conda/bin:$PATH

### PyPI
# No PyPI dependencies!

##
RUN mkdir /runtime
WORKDIR /runtime
RUN git clone https://github.com/biosimulators/bsew.git  /runtime
RUN python3 -m pip install -e /runtime

ENTRYPOINT ["python3", "/runtime/main.py"]
""".strip()
    fake_input_file = \
"""
`conda:readdy@readdy.ReactionDiffusionSystem`
""".strip()
    _build_dockerfile_for_necessary_env_exec(correct_answer, fake_input_file)

