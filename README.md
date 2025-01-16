# transform_defects4j

This repository is used for transforming the dataset using SnippetTransformer and generating the error messages accordingly.
It can also be used to generate stack traces for the un-transformed dataset.
**FOR RESEARCH PAPER ...**

The full data pipeline is shown and explained in [docs/Pipeline.md](docs/Pipeline.md).

## Usage

It is recommended to use a machine with a large amount of cores in order to speed up the process of generating stack traces.

### Setup

1. Clone the project
2. Run `docker build . --tag transform_defects4j`
3. Run `docker run -it --name transform_defects4j_container transform_defects4j`
4. Navigate to the `transform_defects4j` directory.

### Running the pipeline

To run the pipeline with transformation enabled run:

```
python3 run_pipeline.py -i datasets/defects4j-single-function.json -o datasets/defects4j-single-function-transformed.json -t 1 -thr 5
```
- `-i` specifies the input path.
- `-o` specifies the output path.
- `-t` specifies whether transformations are enabled.
- `-thr` specifies the amount of threads used for running the defects4j projects.

Any stage of the pipeline can also be run separately by finding the script in the `src` directory and running the `--help` command,
for example: `python3 src/extract_functions.py --help`.