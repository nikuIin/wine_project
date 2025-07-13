import csv
from bs4 import BeautifulSoup


def get_flag_urls(html_file_path):
    # Read the HTML file
    with open(html_file_path, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")

    # Find the table (assuming it's the first table in the document)
    table = soup.find("table")
    if not table:
        raise ValueError("Table not found in the HTML file")

    flag_urls = {}
    rows = table.find_all("tr")

    for row in rows:
        cells = row.find_all("td")
        if len(cells) >= 5:  # Check if row has enough columns
            # Column with numeric ISO 3166-1 code (country-code)
            country_code = cells[3].get_text(strip=True)
            # Column with country name and flag
            country_cell = cells[0]
            # Find flag image
            img = country_cell.find("img")
            flag_url = ""
            if img and img.get("src"):
                flag_url = "https:" + img.get("src").replace(
                    "'", "''"
                )  # Escape single quotes
            flag_urls[country_code] = flag_url

    return flag_urls


def generate_sql_inserts(csv_file_path, html_file_path):
    # Get flag URLs from HTML file
    flag_urls = get_flag_urls(html_file_path)

    sql = "INSERT INTO country (country_id, name, flag_id)\nVALUES\n"
    values = []

    with open(csv_file_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            country_id = row["country-code"]
            name = row["name"].replace("'", "''")  # Escape single quotes
            # Get flag URL or empty string if not found
            flag_url = flag_urls.get(country_id, "")
            if country_id and name:  # Check for non-empty values
                values.append(f"({country_id}, '{name}', {country_id})")

    sql += ",\n".join(values) + ";"
    return sql


# Example usage
if __name__ == "__main__":
    csv_file_path = "all.csv"
    html_file_path = "country_table.html"
    sql_query = generate_sql_inserts(csv_file_path, html_file_path)
    print(sql_query)
