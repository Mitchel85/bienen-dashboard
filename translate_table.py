import docx
import os

WORKSPACE = "/data/.openclaw/workspace"
DOCX_FILE = os.path.join(WORKSPACE, "MITCH", "0_Euro_Cockpit_English_Full_Layout.docx")

doc = docx.Document(DOCX_FILE)
table = doc.tables[0]

# Manually translated based on the German text
translated_cells = [
    ['What do you want to show?', 'Which tool?', 'The AI command (Snippet)', 'Test environment'],
    ['Processes & Finances', 'Mermaid.js', 'Create a Mermaid.js flowchart (graph TD) for...', 'mermaid.live'],
    ['Official Processes', 'BPMN.io', 'Create BPMN 2.0 XML. Use lanes. Generate coordinates.', 'demo.bpmn.io'],
    ['IT Architecture', 'PlantUML (C4)', 'Create a PlantUML C4 model (Context) for...', 'plantuml.com'],
    ['Knowledge Graphs', 'Vis.js', 'Create a Vis.js HTML file. Make the nodes interactive.', 'visjs.org'],
    ['Pie/Bar Charts', 'Chart.js', 'Create Chart.js code based on this CSV data...', 'chartjs.org']
]

for r_idx, row in enumerate(table.rows):
    for c_idx, cell in enumerate(row.cells):
        cell.text = translated_cells[r_idx][c_idx]

doc.save(DOCX_FILE)
print("Table translated.")
