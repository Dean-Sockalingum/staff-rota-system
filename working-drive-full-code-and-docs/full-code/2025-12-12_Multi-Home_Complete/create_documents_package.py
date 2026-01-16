#!/usr/bin/env python3
"""
Create a ZIP package of all HSCP Word documents for easy sharing and download.
"""

import zipfile
from pathlib import Path
from datetime import datetime


def create_zip_package():
    """Create ZIP file containing all 6 Word documents."""
    print("\nCreating HSCP Documents Package...")
    print("=" * 60)
    
    base_dir = Path(__file__).parent
    
    # Define all Word documents to include
    documents = [
        'HSCP_12_Week_Implementation_Plan.docx',
        'HSCP_ROI_Analysis.docx',
        'HSCP_Business_Case_Five_Case_Model.docx',
        'SYSTEM_CAPABILITIES_WIIFM.docx',
        'ACADEMIC_PAPER_FIGURES.docx',
        'ACADEMIC_PAPER_TEMPLATE.docx'
    ]
    
    # Create timestamp for zip filename
    timestamp = datetime.now().strftime('%Y%m%d')
    zip_filename = f'HSCP_Complete_Documentation_Package_{timestamp}.zip'
    zip_path = base_dir / zip_filename
    
    # Create ZIP file
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        print("\nAdding documents to package:")
        for doc in documents:
            doc_path = base_dir / doc
            if doc_path.exists():
                zipf.write(doc_path, doc)
                size_kb = doc_path.stat().st_size / 1024
                print(f"  ✅ {doc} ({size_kb:.1f} KB)")
            else:
                print(f"  ⚠️  {doc} (not found)")
    
    # Get final zip size
    zip_size_kb = zip_path.stat().st_size / 1024
    
    print("\n" + "=" * 60)
    print(f"✅ Package created successfully!")
    print(f"\nFile: {zip_filename}")
    print(f"Size: {zip_size_kb:.1f} KB")
    print(f"Location: {zip_path}")
    print("\n📦 Package Contents:")
    print("   1. 12-Week Implementation Plan")
    print("   2. ROI Analysis (1,143% ROI, £682,829 Year 1 savings)")
    print("   3. UK Green Book Business Case (Five Case Model)")
    print("   4. System Capabilities Guide (WIIFM)")
    print("   5. Academic Paper Figures")
    print("   6. Academic Paper Template")
    print("\n✨ Ready for board presentation and sharing!")


if __name__ == '__main__':
    create_zip_package()
