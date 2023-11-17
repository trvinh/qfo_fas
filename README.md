# qfo_fas

1. Download https://applbio.biologie.uni-frankfurt.de/download/QFO/qfo20_fas.tar.gz and unpack it. You will find:
  - a **qfo20_anno_dir** folder containing the feature annotations for 79 taxa in the QfO reference set
  - a **nr_pairs.txt** file containing non-redundant pairwise orthologs between 17 different prediction tools (from QfO20)
  - a **qfo20_fas_subset.json** file containing the calculated FAS scores for all pairwise orthologs between human, mouse, rat, yeast, *A. thaliana* and *E. coli*
2. Run `parse_op.py` for a pairwise ortholog tab-delimited file from a submitteed approach to get list of ortholog pairs that are specific for that approach
```
python parse_op.py -i test_data/test_pairs.txt -a ../qfo20_anno_dir --nrPairs ../nr_pairs.txt --cpus 4
```
3. Calculate FAS scores for those approach specific ortholog pairs
```
fas.runMultiTaxa --input test_data/test_pairs.txt.mapped -a ../qfo20_anno_dir -o ../test2 --bidirectional --tsv --domain --no_config --json --mergeJson --outName <fas_qfo20> --pairLimit 30000
```
4. Get all FAS scores for a prediction tool
```
python get_fas.py -i inparanoid.txt -f qfo20_fas_subset.json -o inparanoid_fas
```
