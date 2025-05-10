import argparse
import os

import tnefparse


def extract_tnef_data(winmail_dat_file, output_dir=None):
    """
    Extracts attachments and email body from a Winmail.dat file using tnefparse.
    """
    try:
        with open(winmail_dat_file, "rb") as tnef_file:
            tnef = tnefparse.TNEF(tnef_file.read())

        if output_dir is None:
            output_dir = "output"  # Default output directory

        os.makedirs(output_dir, exist_ok=True)

        # Extract attachments
        for attachment in tnef.attachments:
            if isinstance(attachment.name, bytes):
                attachment_path = os.path.join(
                    output_dir, attachment.name.decode("utf-8", "ignore")
                )
                print(
                    f"Extracted attachment: {attachment.name.decode('utf-8', 'ignore')} to {output_dir}"
                )
            else:
                attachment_path = os.path.join(output_dir, attachment.name)
                print(f"Extracted attachment: {attachment.name} to {output_dir}")
            with open(attachment_path, "wb") as f:
                f.write(attachment.data)

        # Extract email body
        if tnef.body:
            email_body_path = os.path.join(output_dir, "email_body.txt")
            with open(email_body_path, "w", encoding="utf-8", errors="ignore") as f:
                f.write(tnef.body.decode("utf-8", "ignore"))
            print(f"Extracted email body to {email_body_path}")
        else:
            print("No email body found.")

    except Exception as e:
        print(f"An error occurred: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Extract attachments and email body from Winmail.dat files using tnefparse."
    )
    parser.add_argument("winmail_dat_file", help="Path to the Winmail.dat file.")
    parser.add_argument(
        "-o", "--output_dir", help="Output directory for attachments (optional)."
    )

    args = parser.parse_args()

    extract_tnef_data(args.winmail_dat_file, args.output_dir)


if __name__ == "__main__":
    main()
