import json
from pathlib import Path
from backend.app.samples import samples
for industry in ('banking','ecommerce'):
    Path(f'datasets/{industry}/sample.json').write_text(json.dumps({'synthetic':True,'industry':industry,'records':samples(industry)},indent=2))
