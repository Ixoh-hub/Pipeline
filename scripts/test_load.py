from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from patent_pipeline import load_patents, get_tsv_source

print('g_patent source:', get_tsv_source('g_patent'))
df = load_patents()
print('patents rows:', len(df))
print(df.head(3).to_dict(orient='records'))
