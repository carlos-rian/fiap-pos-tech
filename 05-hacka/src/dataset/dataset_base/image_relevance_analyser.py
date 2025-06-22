import pandas as pd

df = pd.read_csv("dataset_base/mapping_images_with_relevance.csv")
relevance_counts = df["RelevanceName"].value_counts()
relevance_counts.to_csv("relevance_levels_count.csv", header=True, index=True)
