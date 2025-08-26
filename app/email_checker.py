from validate_email_address import validate_email
import csv

def check_emails(input_file, output_file):
    valid_emails = []
    invalid_emails = []

    with open(input_file, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            email = row[0].strip()
            is_valid = validate_email(email, verify=True)  # SMTP check
            if is_valid:
                valid_emails.append(email)
            else:
                invalid_emails.append(email)

    # Save results
    with open(output_file, 'w') as file:
        file.write("Valid Emails:\n")
        file.writelines("\n".join(valid_emails))
        file.write("\n\nInvalid Emails:\n")
        file.writelines("\n".join(invalid_emails))

    print(f"Checked {len(valid_emails) + len(invalid_emails)} emails.")
    print(f"Valid: {len(valid_emails)}, Invalid: {len(invalid_emails)}")
    print(f"Results saved in {output_file}")

# Example usage
check_emails("emails.csv", "results.txt")
