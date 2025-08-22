import argparse
import os
import sys

from bsander.bsandr_utils.input_types import ContainerizationTypes, ContainerizationEngine, ProgramArguments
from bsander.execution import execute_bsander


def get_program_arguments() -> ProgramArguments:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog='BioSimulators Tool, Abstraction, Node, & Dependency Resolver (BStandr)',
        description='''BioSimulators project designed to help users resolve any abstract or missing components, 
            and/or creating a containerized environment to repeatedly run the provided experiment''')
    parser.add_argument('input_file_path')  # positional argument
    parser.add_argument('-c', '--containerize', choices=['single', 'multiple'],
                        help="specifies if a containerized runtime should be initialized. "
                             "`single` mode will reject a configuration that results in multiple containers needing to be coordinated together."
                             "`multiple` mode will accept a result that is a coordination of multiple containers.")
    parser.add_argument('-t', '--target-containerization', choices=['docker', 'apptainer', 'both'],
                        help="if containerization is specified, selects whether to containerize with `docker` or `apptainer` (formerly Singularity CE)")
    parser.add_argument('-o', '--output_directory', nargs='?', const='.',
                        help="specifies output directory; if not provided, no output file will be generated, but validation (and containerization if requested) will occur.")
    args = parser.parse_args()
    if args.target_containerization is not None and args.containerize is None:
        parser.print_help()
        print("Error: --target-containerization requires --containerize", file=sys.stderr)
        sys.exit(10)
    if args.target_containerization is None and args.containerize is not None:
        args.target_containerization = "docker"  # docker default, because apptainer is only linux

    args.input_file_path = os.path.abspath(os.path.expanduser(args.input_file_path))
    if not os.path.exists(args.input_file_path) or not os.path.isfile(args.input_file_path) or not (
            args.input_file_path.endswith(".json") or args.input_file_path.endswith(".pbif")
            or args.input_file_path.endswith(".zip") or args.input_file_path.endswith(".omex")):
        parser.print_help()
        print("error: `input_file_path` must be either JSON/PBIF file, or ZIP/OMEX that exists!", file=sys.stderr)
        sys.exit(11)
    if args.output_directory is not None:
        args.output_directory = os.path.abspath(os.path.expanduser(args.output_directory))
        if not os.path.exists(args.output_directory) or not (
                os.path.isdir(args.output_directory) or os.path.islink(args.output_directory)):
            parser.print_help()
            print("`output_directory` must be a directory that exists!", file=sys.stderr)
            sys.exit(12)
    else:
        args.output_directory = args.input_file_path.parent

    containerization_type: ContainerizationTypes = ContainerizationTypes.NONE
    containerization_engine: ContainerizationEngine = ContainerizationEngine.NONE
    if args.containerize is not None:
        if args.containerize == 'single':
            containerization_type = ContainerizationTypes.SINGLE
        elif args.containerize == 'multiple':
            containerization_type = ContainerizationTypes.MULTIPLE
        else:  # should never get here
            parser.print_help()
            print("error: `containerize` must be `single` or `multiple` if requested.", file=sys.stderr)
            sys.exit(13)

        if args.target_containerization == 'docker':
            containerization_engine = ContainerizationEngine.DOCKER
        elif args.target_containerization == 'apptainer':
            containerization_engine = ContainerizationEngine.APPTAINER
        elif args.target_containerization == 'both':
            containerization_engine = ContainerizationEngine.BOTH
        else:
            parser.print_help()
            print("error: `target-containerization` must be `docker`, `apptainer`, or `both.", file=sys.stderr)
            sys.exit(14)

    return ProgramArguments(input_file_path=args.input_file_path, output_dir=args.output_directory,
                            containerization_type=containerization_type,
                            containerization_engine=containerization_engine)

def main():
    execute_bsander(get_program_arguments())

if __name__ == "__main__":
    main()
