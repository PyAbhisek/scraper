import json
import pandas as pd

# Load data from the JSON file
json_file_path = r"C:\Users\abhis\Downloads\partial_scraped_data (9).json"

with open(json_file_path, 'r') as json_file:
    data = json.load(json_file)

# Initialize lists to store the extracted information
rows = []

# Iterate through each JSON object and its shades
for item in data:
    shades = item.get("shades", [])

    for shade in shades:
        shade_url = shade.get("shade_url", "")
        shade_color = ', '.join(map(str, shade.get("shade_color", "")))
        shade_image_url = shade.get("shade_image_url", "")
        shade_sale_price = shade.get("shade_sale_price", "")
        shade_original_price = shade.get("shade_original_price", "")
        product_name = shade.get("Product_Name", "")
        product_type = shade.get("Product_type", "")
        selected_shade_name = shade.get("Selected_shade_name", "")
        vendor = shade.get("vendor", "")

        # Append the extracted information to the rows list
        rows.append([shade_url, shade_color, shade_image_url, shade_sale_price, shade_original_price,
                     product_name, product_type, selected_shade_name, vendor])

# Create a DataFrame from the extracted information
df = pd.DataFrame(rows, columns=["shade_url", "shade_color", "shade_image_url", "shade_sale_price",
                                 "shade_original_price", "Product_Name", "Product_type", "Selected_shade_name",
                                 "vendor"])

# Save the DataFrame to a CSV file
csv_file_path = "output.csv"
df.to_csv(csv_file_path, index=False)

print("CSV file created successfully.")
