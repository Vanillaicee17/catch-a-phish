import pandas as pd

# Read the CSV file into a DataFrame.
df = pd.read_csv(r"C:\Users\ameys\Desktop\Projects\Phishing URL Predictor\dataset\cleaned_phishing_links.csv")
# Identify the column containing the URLs.
# Adjust the column name if it isn't 'url' or 'URL'.
if 'url' in df.columns:
    url_col = 'url'
elif 'URL' in df.columns:
    url_col = 'URL'
else:
    raise ValueError("No URL column found. Please verify the column name in your CSV.")

# Filter out rows where the URL ends with "..."
filtered_df = df[~df[url_col].str.endswith("...", na=False)]

# Save the filtered DataFrame to a new CSV file.
filtered_df.to_csv('cleaned_phishing_links_filtered.csv', index=False)

print("Filtered CSV saved as 'cleaned_phishing_links_filtered.csv'")
