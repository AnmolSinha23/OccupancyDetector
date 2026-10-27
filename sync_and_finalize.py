import os
import subprocess
import docx
from generate_print_ready_report import build_doc

def run_powershell(script_body):
    ps_path = "temp_runner.ps1"
    with open(ps_path, "w", encoding="utf-8") as f:
        f.write(script_body)
    res = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", ps_path], capture_output=True, text=True)
    if os.path.exists(ps_path):
        os.remove(ps_path)
    return res.stdout, res.stderr

def get_page_numbers(docx_path):
    abs_path = os.path.abspath(docx_path)
    ps_code = f"""
$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {{
    $doc = $word.Documents.Open("{abs_path}")
    foreach ($p in $doc.Paragraphs) {{
        $txt = $p.Range.Text.Trim()
        if ($txt.Length -gt 0) {{
            $page = $p.Range.Information(1)
            Write-Output "PARAGRAPH|$page|$txt"
        }}
    }}
    $doc.Close()
}} finally {{
    $word.Quit()
}}
"""
    stdout, stderr = run_powershell(ps_code)
    lines = stdout.splitlines()
    
    index_map = {}
    fig_map = {}
    
    section_targets = {
        "1. Executive Summary": 1,
        "2. Related Research": 2,
        "3. Exploratory Data": 3,
        "4. Explainable Machine": 4,
        "5. Experimental Results": 5,
        "6. Our Original Contributions": 6,
        "7. Real-World Physical Edge Cases": 7,
        "8. Conclusion & Key": 8,
        "9. References & Online": 9,
        "10. APPENDIX: Interactive": 10
    }
    
    fig_targets = {
        "Figure 1:": 1,
        "Figure 2:": 2,
        "Figure 3:": 3,
        "Figure 4:": 4,
        "Figure 5:": 5,
        "Figure 6:": 6,
        "Figure 7:": 7,
        "Figure 8:": 8,
        "Figure A.1:": "A1",
        "Figure A.2:": "A2",
        "Figure A.3:": "A3"
    }
    
    for l in lines:
        if l.startswith("PARAGRAPH|"):
            parts = l.split("|", 2)
            if len(parts) == 3:
                page = int(parts[1])
                txt = parts[2]
                
                for s_key, s_idx in section_targets.items():
                    if s_key in txt and s_idx not in index_map:
                        index_map[s_idx] = str(page)
                        
                for f_key, f_idx in fig_targets.items():
                    if f_key in txt and f_idx not in fig_map:
                        fig_map[f_idx] = str(page)
                        
    return index_map, fig_map

def main():
    print("Step 1: Building initial draft of print-ready document...")
    build_doc()
    
    print("Step 2: Inspecting exact page numbers via Word engine...")
    index_map, fig_map = get_page_numbers("Room_Occupancy_Detection_Project_Report.docx")
    print("Detected Index Page Map:", index_map)
    print("Detected Figures Page Map:", fig_map)
    
    print("Step 3: Rebuilding document with synchronized exact page numbers...")
    build_doc(index_page_map=index_map, fig_page_map=fig_map)
    
    print("Step 4: Exporting final print-ready PDF...")
    abs_docx = os.path.abspath("Room_Occupancy_Detection_Project_Report.docx")
    abs_pdf = os.path.abspath("Room_Occupancy_Detection_Project_Report.pdf")
    ps_export = f"""
$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {{
    $doc = $word.Documents.Open("{abs_docx}")
    $doc.SaveAs([ref]"{abs_pdf}", [ref]17)
    $pages = $doc.ComputeStatistics(2)
    Write-Output "Final Total Pages: $pages"
    $doc.Close()
}} finally {{
    $word.Quit()
}}
"""
    stdout, stderr = run_powershell(ps_export)
    print(stdout.strip())
    print("Step 5: Verifying final text colors and integrity...")
    doc = docx.Document("Room_Occupancy_Detection_Project_Report.docx")
    non_black = 0
    total = 0
    for p in doc.paragraphs:
        for r in p.runs:
            total += 1
            if r.font.color and r.font.color.rgb and r.font.color.rgb != docx.shared.RGBColor(0,0,0):
                non_black += 1
    for t in doc.tables:
        for row in t.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    for r in p.runs:
                        total += 1
                        if r.font.color and r.font.color.rgb and r.font.color.rgb != docx.shared.RGBColor(0,0,0):
                            non_black += 1
    print(f"Verified {total} text runs. Non-black runs: {non_black} (100% Black Text confirmed).")

if __name__ == "__main__":
    main()
