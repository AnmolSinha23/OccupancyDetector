"""
generate_print_ready_report.py
------------------------------
Generates a print-ready, professional academic report in .docx format.

Print Optimizations:
1. Standard A4 Paper Size (8.27 x 11.69 inches) for standard Indian print shops.
2. Left Margin Gutter: 1.15 inches for spiral binding / stapling without clipping text.
3. Clean Cover Page: different_first_page_header_footer = True (no page number or header on cover).
4. Modern Clean Tables: Subtle borders, cantSplit on all rows, tblHeader on header rows, light gray shading.
5. High-contrast typography: 100% black text (RGBColor(0,0,0)), optimal line spacing (1.15), widow/orphan control.
6. Figure sizing optimized for A4 printable width (approx 5.0 - 5.4 inches).
7. Synchronized INDEX & List of Figures with exact matching page numbers.
"""

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


BLACK = RGBColor(0, 0, 0)


def set_cell_background(cell, fill_hex):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_hex)
    tc_pr.append(shd)


def set_cell_margins(cell, top=70, bottom=70, left=110, right=110):
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tc_mar.append(node)
    tc_pr.append(tc_mar)


def set_clean_table_borders(table, color="D1D5DB", sz="4"):
    tblPr = table._tbl.tblPr
    tblBorders = OxmlElement('w:tblBorders')
    for b_name in ['top', 'bottom', 'insideH']:
        b = OxmlElement(f'w:{b_name}')
        b.set(qn('w:val'), 'single')
        b.set(qn('w:sz'), sz)
        b.set(qn('w:space'), '0')
        b.set(qn('w:color'), color)
        tblBorders.append(b)
    for b_name in ['left', 'right', 'insideV']:
        b = OxmlElement(f'w:{b_name}')
        b.set(qn('w:val'), 'none')
        tblBorders.append(b)
    tblPr.append(tblBorders)


def add_field(paragraph, field_text):
    run = paragraph.add_run()
    fldChar1 = OxmlElement('w:fldChar')
    fldChar1.set(qn('w:fldCharType'), 'begin')
    instrText = OxmlElement('w:instrText')
    instrText.set(qn('xml:space'), 'preserve')
    instrText.text = field_text
    fldChar2 = OxmlElement('w:fldChar')
    fldChar2.set(qn('w:fldCharType'), 'separate')
    fldChar3 = OxmlElement('w:fldChar')
    fldChar3.set(qn('w:fldCharType'), 'end')

    r = run._r
    r.append(fldChar1)
    r.append(instrText)
    r.append(fldChar2)
    r.append(fldChar3)
    run.font.name = "Calibri"
    run.font.size = Pt(9)
    run.font.color.rgb = BLACK


def format_table_black_text(table, col_widths, headers, data_rows, header_bg="E5E7EB"):
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_clean_table_borders(table)

    needed_rows = len(data_rows) + 1
    while len(table.rows) < needed_rows:
        table.add_row()

    # Header Row
    hdr_row = table.rows[0]
    tr_pr = hdr_row._tr.get_or_add_trPr()
    tr_pr.append(OxmlElement('w:tblHeader'))
    tr_pr.append(OxmlElement('w:cantSplit'))

    for i, title in enumerate(headers):
        cell = hdr_row.cells[i]
        cell.width = Inches(col_widths[i])
        set_cell_background(cell, header_bg)
        set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(2.5)
        p.paragraph_format.space_after = Pt(2.5)
        run = p.add_run(title)
        run.bold = True
        run.font.name = "Calibri"
        run.font.size = Pt(9.5)
        run.font.color.rgb = BLACK

    # Data Rows
    for r_idx, row_data in enumerate(data_rows):
        row = table.rows[r_idx + 1]
        r_tr_pr = row._tr.get_or_add_trPr()
        r_tr_pr.append(OxmlElement('w:cantSplit'))

        bg_color = "F9FAFB" if (r_idx % 2 == 1) else "FFFFFF"
        for c_idx, val in enumerate(row_data):
            cell = row.cells[c_idx]
            cell.width = Inches(col_widths[c_idx])
            set_cell_background(cell, bg_color)
            set_cell_margins(cell, top=55, bottom=55, left=100, right=100)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)

            if c_idx == 1 and ("Table" in headers[0] or "INDEX" in str(headers)):
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            elif c_idx == 0 and ("Model" in headers[0] or "Resource" in headers[0]):
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            elif c_idx == 1 and "Resource" in headers[0]:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER

            run = p.add_run(str(val))
            run.font.name = "Calibri"
            run.font.size = Pt(9.5)
            run.font.color.rgb = BLACK
            if c_idx == 0 and any(k in str(val) for k in ["Decision Tree", "All 5", "Enhanced", "Selected"]):
                run.bold = True


def build_doc(index_page_map=None, fig_page_map=None):
    """
    Build the document. If index_page_map and fig_page_map are provided,
    use them to populate the exact page numbers in the Index and Figure tables.
    """
    doc = docx.Document()

    # Section & Page Setup: A4 Paper with binding gutter
    section = doc.sections[0]
    section.page_width = Inches(8.27)    # 210 mm
    section.page_height = Inches(11.69)  # 297 mm
    section.top_margin = Inches(1.0)
    section.bottom_margin = Inches(1.0)
    section.left_margin = Inches(1.15)   # Gutter for binding
    section.right_margin = Inches(0.85)

    # First page has DIFFERENT header/footer (Blank for Cover Page)
    section.different_first_page_header_footer = True

    # Normal Page Footer (Page 2 onwards)
    footer = section.footer
    p_ft = footer.paragraphs[0]
    p_ft.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_ft.paragraph_format.space_before = Pt(6)
    p_ft.paragraph_format.space_after = Pt(0)
    r_l = p_ft.add_run("CSE-3006: Advanced Programming Lab Report  |  ")
    r_l.font.name = "Calibri"
    r_l.font.size = Pt(9)
    r_l.font.color.rgb = BLACK
    r_p = p_ft.add_run("Page ")
    r_p.font.name = "Calibri"
    r_p.font.size = Pt(9)
    r_p.font.color.rgb = BLACK
    add_field(p_ft, "PAGE")
    r_o = p_ft.add_run(" of ")
    r_o.font.name = "Calibri"
    r_o.font.size = Pt(9)
    r_o.font.color.rgb = BLACK
    add_field(p_ft, "NUMPAGES")

    # Helper function for adding paragraphs
    def add_p(text, bold_prefix="", space_before=0, space_after=3.5, align=WD_ALIGN_PARAGRAPH.LEFT):
        p = doc.add_paragraph()
        p.alignment = align
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.widow_control = True
        if bold_prefix:
            r_b = p.add_run(bold_prefix)
            r_b.bold = True
            r_b.font.name = "Calibri"
            r_b.font.size = Pt(11)
            r_b.font.color.rgb = BLACK
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(11)
        r.font.color.rgb = BLACK
        return p

    def add_head(title, level=1, space_before=11, space_after=3.5):
        h = doc.add_heading(title, level=level)
        h.paragraph_format.space_before = Pt(space_before)
        h.paragraph_format.space_after = Pt(space_after)
        h.paragraph_format.keep_with_next = True
        h.paragraph_format.widow_control = True
        for r in h.runs:
            r.font.name = "Calibri"
            r.font.color.rgb = BLACK
            r.bold = True
            if level == 1:
                r.font.size = Pt(14)
            else:
                r.font.size = Pt(12)
        return h

    def add_image_with_explanation(fig_path, caption_title, how_made, why_included, width_inches=5.2):
        if os.path.exists(fig_path):
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.space_before = Pt(4)
            p_img.paragraph_format.space_after = Pt(2)
            p_img.paragraph_format.keep_with_next = True
            p_img.paragraph_format.widow_control = True
            run_img = p_img.add_run()
            run_img.add_picture(fig_path, width=Inches(width_inches))

            # Caption
            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.paragraph_format.space_after = Pt(2)
            p_cap.paragraph_format.keep_with_next = True
            r_cap = p_cap.add_run(caption_title)
            r_cap.bold = True
            r_cap.font.name = "Calibri"
            r_cap.font.size = Pt(10)
            r_cap.font.color.rgb = BLACK

            # How it was made
            p_how = doc.add_paragraph()
            p_how.paragraph_format.left_indent = Inches(0.2)
            p_how.paragraph_format.space_after = Pt(1.5)
            p_how.paragraph_format.line_spacing = 1.1
            p_how.paragraph_format.keep_with_next = True
            r_h_lbl = p_how.add_run("• How this image was made: ")
            r_h_lbl.bold = True
            r_h_lbl.font.name = "Calibri"
            r_h_lbl.font.size = Pt(9.5)
            r_h_lbl.font.color.rgb = BLACK
            r_h_txt = p_how.add_run(how_made)
            r_h_txt.font.name = "Calibri"
            r_h_txt.font.size = Pt(9.5)
            r_h_txt.font.color.rgb = BLACK

            # Why it is included
            p_why = doc.add_paragraph()
            p_why.paragraph_format.left_indent = Inches(0.2)
            p_why.paragraph_format.space_after = Pt(6)
            p_why.paragraph_format.line_spacing = 1.1
            r_w_lbl = p_why.add_run("• Why this image is included: ")
            r_w_lbl.bold = True
            r_w_lbl.font.name = "Calibri"
            r_w_lbl.font.size = Pt(9.5)
            r_w_lbl.font.color.rgb = BLACK
            r_w_txt = p_why.add_run(why_included)
            r_w_txt.font.name = "Calibri"
            r_w_txt.font.size = Pt(9.5)
            r_w_txt.font.color.rgb = BLACK

    # =========================================================================
    # PAGE 1: TITLE / COVER PAGE
    # =========================================================================
    add_p("Indian Institute of Information Technology, Bhopal", space_before=12, space_after=2, align=WD_ALIGN_PARAGRAPH.CENTER)
    doc.paragraphs[-1].runs[0].bold = True
    doc.paragraphs[-1].runs[0].font.size = Pt(14)

    add_p("Department of Computer Science and Engineering", space_before=0, space_after=24, align=WD_ALIGN_PARAGRAPH.CENTER)
    doc.paragraphs[-1].runs[0].font.size = Pt(12)

    add_p("Course Project Report", space_before=14, space_after=3, align=WD_ALIGN_PARAGRAPH.CENTER)
    doc.paragraphs[-1].runs[0].font.size = Pt(11)

    add_p("on", space_before=0, space_after=4, align=WD_ALIGN_PARAGRAPH.CENTER)
    doc.paragraphs[-1].runs[0].font.size = Pt(11)

    add_p("SMART ROOM OCCUPANCY DETECTION USING NON-INTRUSIVE AMBIENT SENSORS", space_before=4, space_after=3, align=WD_ALIGN_PARAGRAPH.CENTER)
    doc.paragraphs[-1].runs[0].bold = True
    doc.paragraphs[-1].runs[0].font.size = Pt(15)

    add_p("An Explainable Machine Learning Approach with Sensor Ablation & Past Trend Analysis", space_before=2, space_after=26, align=WD_ALIGN_PARAGRAPH.CENTER)
    doc.paragraphs[-1].runs[0].italic = True
    doc.paragraphs[-1].runs[0].font.size = Pt(10.5)

    add_p("Course: CSE-3006 Advance Programming Lab (Python)", space_before=0, space_after=2, align=WD_ALIGN_PARAGRAPH.CENTER)
    doc.paragraphs[-1].runs[0].font.size = Pt(11)
    doc.paragraphs[-1].runs[0].bold = True

    add_p("(CSE Section: 04)", space_before=0, space_after=34, align=WD_ALIGN_PARAGRAPH.CENTER)
    doc.paragraphs[-1].runs[0].font.size = Pt(11)

    # Coordinator and Student Information Table
    t_cover = doc.add_table(rows=1, cols=2)
    t_cover.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell_coord = t_cover.rows[0].cells[0]
    cell_prep = t_cover.rows[0].cells[1]
    cell_coord.width = Inches(3.1)
    cell_prep.width = Inches(3.1)
    set_cell_margins(cell_coord, top=100, bottom=100, left=120, right=120)
    set_cell_margins(cell_prep, top=100, bottom=100, left=120, right=120)
    set_cell_background(cell_coord, "F3F4F6")
    set_cell_background(cell_prep, "F3F4F6")

    # Left cell: Subject Coordinator
    p_c = cell_coord.paragraphs[0]
    p_c.paragraph_format.space_after = Pt(2)
    r = p_c.add_run("Subject Coordinator:\n")
    r.bold = True
    r.font.name = "Calibri"
    r.font.size = Pt(9.5)
    r.font.color.rgb = BLACK
    r2 = p_c.add_run("Dr. Gagan Vishwakarma\nAssistant Professor (CSE)\nIIIT Bhopal")
    r2.font.name = "Calibri"
    r2.font.size = Pt(9)
    r2.font.color.rgb = BLACK

    # Right cell: Prepared by
    p_p = cell_prep.paragraphs[0]
    p_p.paragraph_format.space_after = Pt(2)
    r = p_p.add_run("Prepared by:\n")
    r.bold = True
    r.font.name = "Calibri"
    r.font.size = Pt(9.5)
    r.font.color.rgb = BLACK
    r3 = p_p.add_run("1. Gautam Kumar (25U023062) CSE(CS)\n2. Anmol Sinha (25U023064) CSE(CS)\nB.Tech 2nd Year, IIIT Bhopal")
    r3.font.name = "Calibri"
    r3.font.size = Pt(9)
    r3.font.color.rgb = BLACK

    # Project Links Table
    add_p("", space_before=20, space_after=4)
    t_links = doc.add_table(rows=3, cols=2)
    t_links.alignment = WD_TABLE_ALIGNMENT.CENTER
    link_widths = [1.8, 4.4]
    link_headers = ["Project Resource", "Access Link / Repository Path"]
    link_rows = [
        ["GitHub Repository", "https://github.com/AnmolSinha23/OccupancyDetector"],
        ["Live Cloud App", "Streamlit Community Cloud (Interactive Model Demonstration)"],
        ["Benchmark Dataset", "UCI Machine Learning Repository (Dataset ID: 357)"]
    ]
    format_table_black_text(t_links, link_widths, link_headers, link_rows, header_bg="E5E7EB")

    doc.add_page_break()

    # =========================================================================
    # PAGE 2: INDEX & LIST OF FIGURES / OUTPUTS
    # =========================================================================
    add_head("TABLE OF CONTENTS (INDEX)", level=1, space_before=4, space_after=4)

    # Defaults if not provided yet
    ip = index_page_map or {
        1: "3", 2: "3", 3: "4", 4: "7", 5: "9", 6: "11", 7: "13", 8: "13", 9: "14", 10: "14"
    }
    fp = fig_page_map or {
        1: "4", 2: "5", 3: "6", 4: "7", 5: "8", 6: "10", 7: "11", 8: "12", "A1": "14", "A2": "15", "A3": "15"
    }

    t_index = doc.add_table(rows=11, cols=3)
    idx_widths = [0.7, 4.8, 0.7]
    idx_headers = ["S. No.", "Topic / Section Name", "Page No."]
    idx_rows = [
        ["1", "Executive Summary & Problem Motivation", str(ip.get(1, "3"))],
        ["2", "Related Research Paper & Benchmark Dataset Description", str(ip.get(2, "3"))],
        ["3", "Exploratory Data Analysis & Physical Sensor Trends", str(ip.get(3, "4"))],
        ["4", "Explainable Machine Learning Methodology & Architecture", str(ip.get(4, "7"))],
        ["5", "Experimental Results & Baseline Model Evaluation", str(ip.get(5, "9"))],
        ["6", "Our Original Contributions: Sensor Ablation & Trend Features", str(ip.get(6, "11"))],
        ["7", "Real-World Physical Edge Cases & Viva Defense Questions", str(ip.get(7, "13"))],
        ["8", "Conclusion & Key Engineering Learnings", str(ip.get(8, "13"))],
        ["9", "References & Online Project Links", str(ip.get(9, "14"))],
        ["10", "APPENDIX: Interactive Web Demonstration & Cloud Screenshots", str(ip.get(10, "14"))]
    ]
    format_table_black_text(t_index, idx_widths, idx_headers, idx_rows, header_bg="E5E7EB")

    add_head("LIST OF FIGURES AND OUTPUTS", level=1, space_before=14, space_after=4)

    t_figs = doc.add_table(rows=12, cols=3)
    fig_widths = [0.9, 4.6, 0.7]
    fig_headers = ["Figure No.", "Title / Description of Visual Output", "Page No."]
    fig_rows = [
        ["Fig 1", "Class Distribution Across Training, Test 1, and Test 2 Datasets", str(fp.get(1, "4"))],
        ["Fig 2", "Light Intensity and CO2 Concentration Over Time by Occupancy", str(fp.get(2, "5"))],
        ["Fig 3", "Sensor Correlation Heatmap with Room Occupancy", str(fp.get(3, "6"))],
        ["Fig 4", "Random Forest Feature Importance Rankings", str(fp.get(4, "7"))],
        ["Fig 5", "Fully Explainable Decision Tree Architecture Flowchart", str(fp.get(5, "8"))],
        ["Fig 6", "Decision Tree Confusion Matrices on Test 1 and Test 2", str(fp.get(6, "10"))],
        ["Fig 7", "Sensor Ablation Study: Impact of Removing Individual Sensors", str(fp.get(7, "11"))],
        ["Fig 8", "Performance Boost from 5-Minute Past Trend Features", str(fp.get(8, "12"))],
        ["Fig A.1", "Web Interface Predicting Empty Room (Low Light Condition)", str(fp.get("A1", "14"))],
        ["Fig A.2", "Web Interface Predicting Occupied Room (Active Lighting & CO2)", str(fp.get("A2", "15"))],
        ["Fig A.3", "Live Cloud Architecture, Decision Trace & Physical Principles", str(fp.get("A3", "15"))]
    ]
    format_table_black_text(t_figs, fig_widths, fig_headers, fig_rows, header_bg="E5E7EB")

    doc.add_page_break()

    # =========================================================================
    # PAGE 3: SECTIONS 1 & 2
    # =========================================================================
    add_head("1. Executive Summary & Problem Motivation", level=1, space_before=4, space_after=3)
    add_p(
        "Modern commercial and educational buildings waste large amounts of electrical energy every day by running heating, "
        "ventilation, and air conditioning (HVAC) systems as well as lighting in empty rooms. Automatically detecting "
        "whether an office, lab, or lecture hall is occupied allows automated systems to activate equipment only when humans "
        "are present. While digital surveillance cameras could detect people easily, cameras create severe privacy concerns "
        "(workers do not want video feeds in offices), demand high network bandwidth, and fail in the dark. "
        "Passive infrared (PIR) motion sensors are also flawed because they fail when occupants sit quietly studying or working."
    )
    add_p(
        "In this project, we built a non-intrusive, privacy-preserving, and fully explainable room occupancy detection system using only "
        "low-cost ambient environmental sensors: Light, Carbon Dioxide (CO2), Temperature, and Humidity. Our primary engineering goal "
        "was complete clarity and explainability: rather than deploying complex 'black-box' neural networks that make decisions through "
        "thousands of uninterpretable weights, we implemented shallow, rule-based machine learning models where every decision can be "
        "traced and verified by hand. In addition, we introduced two original engineering contributions: a systematic sensor ablation "
        "study proving that humidity sensors are redundant, and causal past-only trend features that boost open-door accuracy to 99.27%."
    )

    add_head("2. Related Research Paper & Benchmark Dataset Description", level=1, space_before=10, space_after=3)
    add_p(
        "Our work builds upon the research published by Luis M. Candanedo and Veronique Feldheim titled "
        "'Accurate occupancy detection of an office room from light, temperature, humidity and CO2 measurements using statistical learning models' "
        "(Energy and Buildings, Vol. 112, 2016, pp. 28-39). The authors gathered an empirical dataset in an office measuring "
        "3.1m × 5.8m in Mons, Belgium, and published it on the UC Irvine Machine Learning Repository (Dataset ID: 357)."
    )
    add_p(
        "The benchmark dataset consists of three separate files sampled every 60 seconds (1-minute intervals). Ground-truth occupancy "
        "(1 for occupied, 0 for empty) was verified using continuous time-stamped digital photographs taken during the experiment:"
    )
    add_p(
        "• datatraining.txt (Training Dataset): Recorded from February 4 to February 10, 2015. Contains 8,143 rows (minutes). Used strictly "
        "for model training and chronological validation. The office door was kept closed during occupied hours."
    )
    add_p(
        "• datatest.txt (Test Set 1 - Door Closed): Recorded from February 11 to February 18, 2015. Contains 2,665 rows. The office door "
        "was closed as in training. Evaluates model generalizability over a completely new week under identical door conditions."
    )
    add_p(
        "• datatest2.txt (Test Set 2 - Door Mostly Open): Recorded from February 18 to February 26, 2015. Contains 9,752 rows. The office "
        "door was left mostly open during working hours. This provides a rigorous real-world stress test: open doors allow exhaled CO2 and "
        "heat to diffuse freely into corridors, testing whether models collapse when airflow patterns change."
    )

    doc.add_page_break()

    # =========================================================================
    # SECTION 3: DATA EXPLORATION
    # =========================================================================
    add_head("3. Exploratory Data Analysis & Physical Sensor Trends", level=1, space_before=4, space_after=3)
    add_p(
        "Before training any machine learning models, we conducted an exploratory data analysis to inspect data distributions, verify "
        "class balance, and understand how physical sensors respond when humans enter and leave the room."
    )

    # Figure 1: Class Balance
    add_image_with_explanation(
        "outputs/figures/class_balance.png",
        "Figure 1: Class Distribution Across Training, Test 1, and Test 2 Datasets",
        how_made="Generated in src/exploration.py by counting empty rows (0) and occupied rows (1) across each file and plotting count bars using Seaborn.",
        why_included="To show that the dataset is naturally imbalanced: Empty rows make up 78.8% of training data, 73.6% of Test 1, and 64.6% of Test 2. This visually proves why raw accuracy alone is deceptive: a trivial model that simply guessed 'Empty' every minute would score ~79% accuracy without detecting a single person! This justifies why Recall is our primary metric.",
        width_inches=5.0
    )

    # Figure 2: Time Series
    add_image_with_explanation(
        "outputs/figures/time_series_light_co2.png",
        "Figure 2: Light Intensity and CO2 Concentration Over Time by Occupancy Status",
        how_made="Generated in src/exploration.py by plotting timestamps on the x-axis and sensor readings on the y-axis, with points colored blue for Empty (0) and red for Occupied (1).",
        why_included="To visually confirm the physical laws of indoor occupancy: when workers enter (red points), Light turns on immediately (0 to >400 Lux) and CO2 begins climbing due to human respiration. When occupants leave (blue points), Light drops to zero instantly, while CO2 slowly decays over 45-60 minutes.",
        width_inches=5.0
    )

    # Figure 3: Correlation Heatmap
    add_image_with_explanation(
        "outputs/figures/correlation_heatmap.png",
        "Figure 3: Sensor Correlation Heatmap with Room Occupancy",
        how_made="Generated in src/exploration.py by computing Pearson correlation coefficients (a score from -1 to +1 measuring how closely two variables move together) using pandas df.corr().",
        why_included="To provide an initial statistical ranking of sensor strength. It shows Light has the highest correlation (+0.91) because people turn on lamps to work, and CO2 is strong (+0.71) because humans exhale it. Humidity (+0.14) has a very weak correlation, signaling early on that it may be redundant.",
        width_inches=4.4
    )

    doc.add_page_break()

    # =========================================================================
    # SECTION 4: METHODOLOGY & ARCHITECTURE
    # =========================================================================
    add_head("4. Explainable Machine Learning Methodology & Architecture", level=1, space_before=4, space_after=3)
    add_p(
        "We prioritized explainability above all else. In a viva assessment or commercial building deployment, an engineer must be able "
        "to explain why the model made a specific prediction. We selected three transparent models from Scikit-Learn:"
    )
    add_p(
        "1. Decision Tree (max_depth=3): A simple flowchart of yes/no threshold questions. With a maximum depth of 3, the entire tree "
        "contains only 8 decision leaves. Any human can trace its logic in 10 seconds without a computer."
    )
    add_p(
        "2. Logistic Regression: A transparent linear model that calculates a weighted score from scaled sensor inputs and passes it "
        "through a sigmoid function (an S-shaped curve converting any number into a probability between 0 and 1)."
    )
    add_p(
        "3. Random Forest (100 trees, max_depth=3): An ensemble (team) of 100 shallow decision trees that vote on the final outcome, "
        "used as a robust benchmark to verify feature importances."
    )

    # Figure 4: Feature Importance
    add_image_with_explanation(
        "outputs/figures/feature_importance_rf.png",
        "Figure 4: Random Forest Feature Importance Rankings",
        how_made="Generated in src/baseline_models.py by extracting the feature_importances_ attribute from the trained Random Forest and plotting a horizontal bar chart.",
        why_included="To prove which sensors matter most. Light provides 55.4% and CO2 provides 31.2% of total predictive power (86.6% combined). Humidity accounts for less than 1.6%, providing concrete evidence that moisture sensors add almost zero value.",
        width_inches=5.0
    )

    # Figure 5: Decision Tree Flowchart
    add_image_with_explanation(
        "outputs/figures/decision_tree_structure.png",
        "Figure 5: Fully Explainable Decision Tree Architecture Flowchart (Max Depth = 3)",
        how_made="Generated in src/baseline_models.py using Scikit-Learn's plot_tree() function, rendering all decision nodes, split thresholds, and class counts.",
        why_included="To provide a visual blueprint of the model. Examiners can inspect every branch. How to read each box: (1) Top line is the split question (e.g. Light <= 365.12 Lux); (2) 'samples' is the number of training minutes that reached that node; (3) 'value = [Empty, Occupied]' shows class counts; (4) 'gini' is the purity score (0.0 means 100% pure all-one-class; 0.5 means 50/50 mixed).",
        width_inches=5.2
    )

    doc.add_page_break()

    # =========================================================================
    # SECTION 5: EXPERIMENTAL RESULTS
    # =========================================================================
    add_head("5. Experimental Results & Baseline Model Evaluation", level=1, space_before=4, space_after=3)
    add_p(
        "We evaluated all baseline models on both test files using four standard classification metrics: Accuracy (percentage of all "
        "minutes predicted correctly), Recall (percentage of occupied minutes correctly detected), Precision (percentage of occupied flags "
        "that were real), and F1 Score (harmonic mean balancing precision and recall). In occupancy detection, missing an occupied room "
        "(leaving people in the dark) is worse than a false alarm, making Recall our most critical metric."
    )

    # Table 1: Baseline Metrics
    add_p("Table 1: Baseline Model Performance Across Both Environmental Conditions", bold_prefix="")
    t_base = doc.add_table(rows=7, cols=7)
    base_widths = [1.5, 1.1, 0.75, 0.75, 0.75, 0.75, 0.65]
    base_headers = ["Model Name", "Dataset Condition", "Accuracy", "Recall", "Precision", "F1 Score", "TN / FP / FN / TP"]
    base_rows = [
        ["Decision Tree", "Test 1 (Door Closed)", "97.82%", "99.49%", "94.80%", "97.09%", "1640 / 53 / 5 / 967"],
        ["Logistic Regression", "Test 1 (Door Closed)", "97.90%", "97.84%", "96.45%", "97.14%", "1658 / 35 / 21 / 951"],
        ["Random Forest", "Test 1 (Door Closed)", "98.24%", "97.53%", "97.63%", "97.58%", "1670 / 23 / 24 / 948"],
        ["Decision Tree", "Test 2 (Door Open)", "97.67%", "99.41%", "90.45%", "94.72%", "7691 / 349 / 19 / 1693"],
        ["Logistic Regression", "Test 2 (Door Open)", "98.66%", "94.74%", "97.45%", "96.08%", "7998 / 42 / 90 / 1622"],
        ["Random Forest", "Test 2 (Door Open)", "98.47%", "94.80%", "96.38%", "95.58%", "7979 / 61 / 89 / 1623"]
    ]
    format_table_black_text(t_base, base_widths, base_headers, base_rows, header_bg="E5E7EB")

    # Figure 6: Simplified Decision Tree Confusion Matrix
    add_image_with_explanation(
        "outputs/figures/confusion_matrix_decision_tree.png",
        "Figure 6: Decision Tree Confusion Matrices on Test 1 (Door Closed) and Test 2 (Door Open)",
        how_made="Generated by plotting the exact true vs predicted counts from baseline_metrics.csv as clean 2x2 heatmaps using Seaborn.",
        why_included="To show the exact count of correct predictions and errors for our primary model. Top-Left is True Empty (correct vacancy), Bottom-Right is True Occupied (correct presence). Bottom-Left is False Negatives (missed people) — notice the Decision Tree missed only 5 minutes out of 972 on Test 1, yielding a remarkable 99.49% Recall.",
        width_inches=5.2
    )

    doc.add_page_break()

    # =========================================================================
    # SECTION 6: ORIGINAL CONTRIBUTIONS
    # =========================================================================
    add_head("6. Our Original Contributions: Sensor Ablation & Past Trend Features", level=1, space_before=4, space_after=3)
    add_p(
        "To advance beyond simply reproducing the Candanedo & Feldheim paper, we designed and implemented two original engineering contributions:"
    )

    add_p(
        "Contribution 1: Sensor Ablation Study (Hardware Cost Reduction)", bold_prefix="• "
    )
    add_p(
        "We systematically tested whether all four sensors are truly necessary. We trained models removing one sensor at a time (leave-one-out) "
        "and using only a single sensor. The empirical results revealed that removing Humidity causes a 0.00% drop in accuracy and recall! "
        "Relative humidity changes too slowly in a room to detect real-time occupancy. Deploying organizations can completely eliminate humidity "
        "sensors, saving component costs, PCB space, and microcontroller ADC channels without sacrificing any performance."
    )

    # Figure 7: Ablation Study
    add_image_with_explanation(
        "outputs/figures/ablation_study.png",
        "Figure 7: Sensor Ablation Study: Impact of Removing Individual Sensors on Performance",
        how_made="Generated in src/sensor_ablation.py by retraining the Decision Tree on all 11 sensor subsets and plotting comparative accuracy and recall bars.",
        why_included="To visually justify hardware reduction: removing Light causes performance to collapse, whereas removing Humidity produces identical accuracy (97.82% on Test 1, 97.67% on Test 2). Light + CO2 alone achieve full performance.",
        width_inches=5.2
    )

    add_p(
        "Contribution 2: 5-Minute Past Trend Features (Door-Open Robustness)", bold_prefix="• "
    )
    add_p(
        "When the door is open (Test 2), air drafts disperse CO2, causing static snapshot models to generate 349 false alarms. To fix this, "
        "we engineered two dynamic features using ONLY past sensor readings: (1) 5-minute CO2 change (CO2(t) - CO2(t-5)), and (2) 5-minute "
        "rolling average of Light. Strict Causal Rule: Live systems cannot see the future. We used df['CO2'].shift(5) to inspect only past data."
    )

    # Figure 8: Trend Features
    add_image_with_explanation(
        "outputs/figures/trend_features_comparison.png",
        "Figure 8: Impact of Adding 5-Minute Past Trend Features on Test 1 and Test 2 Performance",
        how_made="Generated in src/trend_features.py by comparing baseline models against trend-enhanced models on Test 1 and Test 2.",
        why_included="To demonstrate our solution to the door-open challenge: adding past CO2 slope increases Test 2 accuracy from 97.67% to 99.27% and precision from 90.45% to 97.05%, eliminating over 60% of false alarms.",
        width_inches=5.2
    )

    doc.add_page_break()

    # =========================================================================
    # SECTIONS 7 & 8: VIVA DEFENSE & CONCLUSION
    # =========================================================================
    add_head("7. Real-World Physical Edge Cases & Viva Defense Questions", level=1, space_before=4, space_after=3)
    add_p(
        "During live testing with our interactive web demonstration sliders, two critical edge-case behaviors emerge that examiners frequently ask:"
    )

    add_p(
        "Q1: If Light is 0 Lux and CO2 is high (e.g. 1,000 ppm), why does the model predict EMPTY? Wouldn't someone assume a person is sleeping in the dark?",
        bold_prefix="• "
    )
    add_p(
        "Defense: Light changes instantaneously (0 seconds) when someone switches off a lamp, but exhaled CO2 is a heavy gas trapped in the air "
        "that takes 45 to 60 minutes to vent out through doors or ducts. When office staff leave at 6:00 PM, they turn off the lights, leaving "
        "warm, CO2-rich air behind. In the actual dataset, there are 3,233 real sensor readings where Light < 10 Lux and CO2 > 650 ppm, and in "
        "100% of those 3,233 instances, the room was confirmed to be EMPTY! People do not sleep in commercial offices during work hours. "
        "Predicting 'Occupied' here would waste electricity running air conditioning in empty rooms every evening. (Our 5-minute trend feature "
        "solves this: a sleeping person keeps CO2 rising, whereas an empty room has actively falling CO2)."
    )

    add_p(
        "Q2: If Light is 0 Lux but Relative Humidity is pushed to 40.5%, why does the Decision Tree switch to OCCUPIED?",
        bold_prefix="• "
    )
    add_p(
        "Defense: Humans exhale water vapor and emit body perspiration alongside CO2. In winter Mons, Belgium, ambient office humidity averaged "
        "only 25.7%. Whenever the room was empty, humidity never exceeded 37.69%. The only times humidity crossed 37.74% in dim light was at "
        "dusk (5:30 to 6:00 PM) when staff worked late, causing accumulated respiration to drive humidity high. Furthermore, 40.5% humidity "
        "exceeds the highest humidity in the entire training dataset (39.12%), demonstrating how decision trees extrapolate on out-of-distribution inputs."
    )

    add_head("8. Conclusion & Key Engineering Learnings", level=1, space_before=10, space_after=3)
    add_p(
        "1. Ambient non-intrusive sensors reliably detect room occupancy without infringing on personal privacy or deploying expensive cameras."
    )
    add_p(
        "2. An explainable Decision Tree (max_depth=3) achieves 97.82% accuracy and 99.49% recall, matching or exceeding complex black-box models "
        "while providing total transparency."
    )
    add_p(
        "3. Humidity sensors are redundant: removing them produces a 0.00% drop in accuracy, enabling significant hardware cost reduction."
    )
    add_p(
        "4. Causal 5-minute past trend features overcome open-door airflow dispersion, boosting open-door accuracy to 99.27%."
    )

    doc.add_page_break()

    # =========================================================================
    # SECTION 9 & APPENDIX
    # =========================================================================
    add_head("9. References & Online Project Links", level=1, space_before=4, space_after=3)
    add_p(
        "1. Candanedo, L. M., & Feldheim, V. (2016). Accurate occupancy detection of an office room from light, temperature, humidity and CO2 "
        "measurements using statistical learning models. Energy and Buildings, 112, 28-39."
    )
    add_p(
        "2. UCI Machine Learning Repository: Occupancy Detection Dataset (ID: 357). https://archive.ics.uci.edu/dataset/357/occupancy+detection"
    )
    add_p(
        "3. Project GitHub Repository: https://github.com/AnmolSinha23/OccupancyDetector (Complete source code, training scripts, figures, and model weights)."
    )
    add_p(
        "4. Live Interactive Cloud Application: Deployed on Streamlit Community Cloud for instant demonstration on mobile and desktop browsers."
    )

    add_head("10. APPENDIX: Interactive Web Demonstration & Cloud Screenshots", level=1, space_before=10, space_after=3)
    add_p(
        "We packaged our trained explainable Decision Tree into an interactive web demonstration using Streamlit (app.py) and deployed it online. "
        "The application features real-time sliders for Light, CO2, Temperature, and Humidity, automatically computes physical HumidityRatio "
        "using the Magnus-Tetens formula, displays instantaneous occupancy state with predicted confidence, traces the exact decision tree path, "
        "and provides pre-configured scenario buttons. Below are actual screenshots of the deployed application:"
    )

    # Screenshot 1: Empty Room
    add_image_with_explanation(
        "outputs/figures/app_empty_screenshot.png",
        "Figure A.1: Live Web Application Output - Room Correctly Classified as EMPTY",
        how_made="Captured directly from our live Streamlit Cloud deployment with input sliders set to: Light = 145.00 Lux, CO2 = 720.00 ppm, Temperature = 21.80 °C, Relative Humidity = 27.20 %.",
        why_included="Demonstrates real-time model inference: because Light is below the primary split threshold of 365.12 Lux and Humidity is below 37.74%, the decision trace follows Node 1 and Node 2 to declare ROOM STATUS: EMPTY with 99.97% confidence.",
        width_inches=5.2
    )

    doc.add_page_break()

    # Screenshot 2: Occupied Room
    add_head("APPENDIX (Continued): Live Cloud Deployment Interface", level=1, space_before=4, space_after=3)

    add_image_with_explanation(
        "outputs/figures/app_occupied_screenshot.png",
        "Figure A.2: Live Web Application Output - Room Correctly Classified as OCCUPIED",
        how_made="Captured directly from our live Streamlit Cloud deployment with input sliders set to: Light = 425.00 Lux, CO2 = 720.00 ppm, Temperature = 21.80 °C, Relative Humidity = 27.20 %.",
        why_included="Demonstrates occupied room classification: because Light is above 365.12 Lux (active artificial illumination) and CO2 is above 456.33 ppm (human respiration buildup), the model confirms ROOM STATUS: OCCUPIED with 98.41% confidence.",
        width_inches=5.2
    )

    # Screenshot 3: Cloud Architecture
    add_image_with_explanation(
        "outputs/figures/app_cloud_architecture_screenshot.png",
        "Figure A.3: Live Cloud Interface Showing Model Architecture, Decision Logic Trace, and Physical Boundaries",
        how_made="Captured directly from our Streamlit Cloud deployment, showing the live browser toolbar (Share, Star, GitHub icon, Manage App) and the tabs explaining model mechanics.",
        why_included="Proves live cloud deployment and self-contained explainability: any evaluator can open the three tabs to inspect algorithm details, physical sensor principles, and documented real-world edge cases directly inside the application.",
        width_inches=5.2
    )

    output_path = "Room_Occupancy_Detection_Project_Report.docx"
    doc.save(output_path)
    print(f"Report saved to '{output_path}'")


if __name__ == "__main__":
    build_doc()
