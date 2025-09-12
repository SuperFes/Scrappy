import csv

def write_csv_report(page_data, filename="report.csv"):
    with open(filename, 'w') as csvfile:
        fieldnames = ['page_url', 'h1', 'first_paragraph', 'outgoing_link_urls', 'image_urls']

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()

        for page in page_data:
            row = page

            row['outgoing_link_urls'] = ";".join(page['outgoing_link_urls'])
            row['image_urls'] = ";".join(page['image_urls'])

            writer.writerow(row)
