# qfo_fas

1. Download https://applbio.biologie.uni-frankfurt.de/download/QFO/qfo20_fas.tar.gz and unpack it. You will find:
  - a **qfo20_anno_dir** folder containing the feature annotations for 79 taxa in the QfO reference set
  - a **nr_pairs.txt** file containing non-redundant pairwise orthologs between 17 different prediction tools (from QfO20)
  - a **qfo20_fas_subset.json** file containing the calculated FAS scores for all pairwise orthologs between human, mouse, rat, yeast, *A. thaliana* and *E. coli*
2. Run `parse_op.py` for a pairwise ortholog tab-delimited file from a submitteed approach to get list of ortholog pairs that are specific for that approach (an example output for this command can be found at `test_data/test_pairs.txt.mapped`
```
python parse_op.py -i test_data/test_pairs.txt -a qfo20_anno_dir --nrPairs nr_pairs.txt --cpus 8
```
3. Install [FAS tool](https://github.com/BIONF/FAS) and run `fas.setup` (the installation of the annotation tools can be skipped with the option `--noAnno`)
4. Calculate FAS scores for those approach specific ortholog pairs
```
fas.runMultiTaxa --input test_data/test_pairs.txt.mapped -a qfo20_anno_dir -o <output_path> --oldJson qfo20_fas_subset.json --bidirectional --tsv --domain --no_config --json --mergeJson --outName <output_filename> --max_cardinality 100 --pairLimit 30000 --cpus 32
```
5. Merge the result from step 4 **`<output_path>/<output_filename>.json`** with **qfo20_fas_subset.json** either manually or using this script
```
# first, copy or link qfo20_fas_subset.json to <output_path>
# then, run
fas.mergeJson -i <output_path> -n qfo20_fas_merged
```
6. and get all FAS scores for a prediction tool
```
python get_fas.py -i inparanoid.txt -f qfo20_fas_merged.json -o inparanoid_fas
```
