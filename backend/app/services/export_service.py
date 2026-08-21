import io
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from typing import List, Dict, Any

def generate_csv_export(data: List[Dict[str, Any]]) -> io.BytesIO:
    df = pd.DataFrame(data)
    output = io.BytesIO()
    df.to_csv(output, index=False, encoding='utf-8')
    output.seek(0)
    return output

def generate_excel_export(incomes_data: List[Dict[str, Any]], expenses_data: List[Dict[str, Any]]) -> io.BytesIO:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        if expenses_data:
            df_exp = pd.DataFrame(expenses_data)
            df_exp.to_excel(writer, sheet_name='Expenses', index=False)
        else:
            pd.DataFrame([{"Info": "No expense data"}]).to_excel(writer, sheet_name='Expenses', index=False)
            
        if incomes_data:
            df_inc = pd.DataFrame(incomes_data)
            df_inc.to_excel(writer, sheet_name='Income', index=False)
        else:
            pd.DataFrame([{"Info": "No income data"}]).to_excel(writer, sheet_name='Income', index=False)
    output.seek(0)
    return output

def generate_pdf_report(user_name: str, period: str, summary: Dict[str, Any], expenses: List[Dict[str, Any]]) -> io.BytesIO:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=22,
        textColor=colors.HexColor('#1E1B4B'),
        spaceAfter=12
    )
    
    subtitle_style = ParagraphStyle(
        'SubTitleStyle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#475569'),
        spaceAfter=20
    )
    
    elements = []
    
    # Title & Subtitle
    elements.append(Paragraph("BudgetBuddy Financial Summary Report", title_style))
    elements.append(Paragraph(f"Prepared for: <b>{user_name}</b> | Period: <b>{period}</b>", subtitle_style))
    elements.append(Spacer(1, 10))
    
    # Financial Overview Box Table
    elements.append(Paragraph("<b>Financial Overview</b>", styles['Heading2']))
    summary_data = [
        ["Total Income", f"${summary.get('total_income', 0):,.2f}"],
        ["Total Expense", f"${summary.get('total_expense', 0):,.2f}"],
        ["Net Savings", f"${summary.get('net_savings', 0):,.2f}"],
        ["Savings Rate", f"{summary.get('savings_rate', 0):.1f}%"]
    ]
    summary_table = Table(summary_data, colWidths=[200, 300])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#0F172A')),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 20))
    
    # Expenses Table
    elements.append(Paragraph("<b>Recent Expenses Breakdown</b>", styles['Heading2']))
    if expenses:
        table_data = [["Date", "Title", "Category", "Payment", "Amount"]]
        for e in expenses[:30]:
            table_data.append([
                str(e.get('date', ''))[:10],
                str(e.get('title', '')),
                str(e.get('category', '')),
                str(e.get('payment_method', '')),
                f"${e.get('amount', 0):,.2f}"
            ])
        exp_table = Table(table_data, colWidths=[80, 150, 100, 90, 80])
        exp_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#4F46E5')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('ALIGN', (-1,0), (-1,-1), 'RIGHT'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F1F5F9')]),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ]))
        elements.append(exp_table)
    else:
        elements.append(Paragraph("No expenses recorded for this period.", styles['Normal']))

    doc.build(elements)
    buffer.seek(0)
    return buffer
