from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from patent_pipeline import get_tsv_source, read_columns, read_tsv_chunks

source = get_tsv_source('g_patent')
print('source', source)
cols = read_columns(source)
print('columns count', len(cols), 'sample', cols[:10])
for chunk in read_tsv_chunks(source, usecols=['patent_id', 'patent_date', 'patent_title'], chunksize=5):
    print(chunk.head())
    print('chunk size', len(chunk))
    break
