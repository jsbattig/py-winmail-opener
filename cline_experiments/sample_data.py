#!/usr/bin/env python3
"""
Create a sample TNEF file for testing the HTML viewer
"""

import os

import tnefparse
from tnefparse.tnef import TNEF, TNEFAttachment


def create_sample_viewer_html():
    """Create a sample HTML view that shows what our winmail.dat viewer would display"""

    # Sample email content
    html_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Winmail.dat Content</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            background-color: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .metadata-item {
            margin-bottom: 8px;
        }
        .metadata-label {
            font-weight: bold;
            color: #555;
            width: 120px;
            display: inline-block;
        }
        .body-container {
            background-color: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            border: 1px solid #e1e4e8;
        }
        .attachments {
            background-color: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .attachment-list {
            list-style-type: none;
            padding-left: 0;
        }
        .attachment-item {
            padding: 8px 0;
            border-bottom: 1px solid #eee;
        }
        .attachment-item:last-child {
            border-bottom: none;
        }
        .attachment-link {
            text-decoration: none;
            color: #0366d6;
        }
        .attachment-link:hover {
            text-decoration: underline;
        }
        .attachment-size {
            color: #666;
            font-size: 0.9em;
        }
        h1 {
            color: #24292e;
            font-size: 24px;
            font-weight: 600;
            margin-top: 0;
        }
        h2 {
            color: #24292e;
            font-size: 20px;
            font-weight: 600;
            margin-top: 0;
            border-bottom: 1px solid #eaecef;
            padding-bottom: 8px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Email Content</h1>
        <div class="metadata-item"><span class="metadata-label">From:</span> John Smith &lt;john.smith@example.com&gt;</div>
        <div class="metadata-item"><span class="metadata-label">Subject:</span> Quarterly Report and Meeting Notes</div>
        <div class="metadata-item"><span class="metadata-label">Date Sent:</span> 2023-07-15 14:32:45</div>
        <div class="metadata-item"><span class="metadata-label">Date Received:</span> 2023-07-15 14:33:12</div>
        <div class="metadata-item"><span class="metadata-label">Priority:</span> Normal</div>
        <div class="metadata-item"><span class="metadata-label">Message ID:</span> &lt;CAJd=7avqx8tEKz+S7MFRM1pSvyJrMJ9UKq8xgdz+4VE@mail.example.com&gt;</div>
    </div>

    <div class="body-container">
        <p>Hello Team,</p>
        <p>I'm writing to share the quarterly report and notes from our strategy meeting last week. Please review these documents before our follow-up meeting scheduled for next Monday.</p>
        <p>Key points from the report:</p>
        <ul>
            <li>Q2 revenue exceeded projections by 12%</li>
            <li>Customer acquisition costs decreased by 8.5%</li>
            <li>New product line launch scheduled for September</li>
        </ul>
        <p>During Monday's meeting, we'll discuss the marketing strategy for Q3 and review the implementation timeline for the new CRM system.</p>
        <p>Please let me know if you have any questions or can't attend.</p>
        <p>Best regards,<br>John</p>
    </div>

    <div class="attachments">
        <h2>Attachments</h2>
        <ul class="attachment-list">
            <li class="attachment-item">
                <a href="file:///Users/username/Downloads/Q2_Financial_Report.pdf" class="attachment-link">Q2_Financial_Report.pdf</a>
                <span class="attachment-size"> (1.8 MB)</span>
            </li>
            <li class="attachment-item">
                <a href="file:///Users/username/Downloads/Strategy_Meeting_Notes.docx" class="attachment-link">Strategy_Meeting_Notes.docx</a>
                <span class="attachment-size"> (245.5 KB)</span>
            </li>
            <li class="attachment-item">
                <a href="file:///Users/username/Downloads/Product_Launch_Timeline.xlsx" class="attachment-link">Product_Launch_Timeline.xlsx</a>
                <span class="attachment-size"> (320.8 KB)</span>
            </li>
            <li class="attachment-item">
                <a href="file:///Users/username/Downloads/2023_Marketing_Budget.xlsx" class="attachment-link">2023_Marketing_Budget.xlsx</a>
                <span class="attachment-size"> (175.2 KB)</span>
            </li>
        </ul>
    </div>
</body>
</html>
"""

    # Save sample HTML
    temp_html_file = "/tmp/winmail_sample_view.html"
    with open(temp_html_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Sample HTML created at {temp_html_file}")

    # Open with default browser
    import subprocess

    subprocess.call(["open", temp_html_file])
    print("Opened sample view in browser")


if __name__ == "__main__":
    create_sample_viewer_html()
