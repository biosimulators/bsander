import os
import tempfile
import zipfile

from bsander.bsandr_utils.input_types import ContainerizationTypes, ContainerizationEngine, ProgramArguments
from bsander.execution import execute_bsander as run_bsander


def test_build_dockerfile_for_necessary_env_from_archive() -> None:
    correct_answer = \
"""
FROM ghcr.io/astral-sh/uv:python3.12-bookworm

RUN apt update
RUN apt upgrade -y
RUN apt install -y git curl

## Dependency Installs
### Conda
# No conda dependencies!

### PyPI
RUN python3 -m pip install 'numpy>=2.0.0' 'process-bigraph<1.0'

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
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, "inputArchive.omex")
        with zipfile.ZipFile(zip_path, "a") as zip_ref:
            zip_ref.writestr("inputFile.pbif", fake_input_file)
        test_args = ProgramArguments(zip_path, tmpdir, ContainerizationTypes.SINGLE, ContainerizationEngine.DOCKER)
        run_bsander(test_args)
        output_dockerfile = os.path.join(tmpdir, "Dockerfile")
        with open(output_dockerfile, "r") as results_file:
            results = results_file.read()
        assert results == correct_answer