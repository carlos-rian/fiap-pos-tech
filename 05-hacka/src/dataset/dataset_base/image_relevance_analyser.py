from pathlib import Path

import pandas as pd

base_path = Path(__file__).parent
filepath = base_path / "mapping_images_with_relevance.csv"
df = pd.read_csv(filepath)
relevance_counts = df["RelevanceName"].value_counts()
relevance_counts.to_csv(base_path / "relevance_levels_count.csv", header=True, index=True)

# relevance by prefix resource and relevance name
df["PrefixResource"] = df["ImageName"].str.split("_").str[0]
relevance_by_prefix = df.groupby(["PrefixResource", "RelevanceName"]).size().reset_index(name="Count")
relevance_by_prefix.to_csv(base_path / "relevance_by_prefix.csv", header=True, index=False)
