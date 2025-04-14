from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.legends import Legend
from io import BytesIO
from typing import Dict, List, Optional, Any
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import base64
import numpy as np
import json
import os
import tempfile
from datetime import datetime
import logging
import traceback
import io
import matplotlib.patches as patches

class ReportGenerator:
    """Service for generating resume analysis reports"""
    @staticmethod
    def generate_pdf_report(analysis_data: Dict) -> bytes:
        """
        Generate PDF report from analysis data
        Args:
        analysis_data (Dict): Comprehensive resume analysis data
        Returns:
        bytes: PDF report content
        """
        try:
            # Create a BytesIO buffer for the PDF content
            buffer = io.BytesIO()
            
            # Set up the document with letter size and 0.5 inch margins
            doc = SimpleDocTemplate(
                buffer, 
                pagesize=letter,
                rightMargin=36, 
                leftMargin=36,
                topMargin=36, 
                bottomMargin=36
            )
            
            # Create a list to store the document elements
            elements = []
            
            # Define styles
            styles = getSampleStyleSheet()
            title_style = styles['Title']
            heading_style = styles['Heading1']
            subheading_style = styles['Heading2']
            normal_style = styles['Normal']
            
            # Add custom style for the score display
            score_style = ParagraphStyle(
                'ScoreStyle',
                parent=styles['Normal'],
                fontSize=16,
                textColor=colors.darkblue,
                alignment=1  # Center alignment
            )
            
            # Add title
            elements.append(Paragraph("Resume Analysis Report", title_style))
            elements.append(Spacer(1, 20))
            
            # Add overall score section if available
            if 'scores' in analysis_data and 'overall' in analysis_data['scores']:
                overall_score = analysis_data['scores']['overall']
                elements.append(Paragraph("Overall Job Compatibility", heading_style))
                elements.append(Paragraph(f"{overall_score}%", score_style))
                
                # Add visualization for overall score
                compatibility_chart = ReportGenerator._create_gauge_chart(overall_score, "Compatibility Score")
                elements.append(compatibility_chart)
                elements.append(Spacer(1, 20))
            elif 'compatibility_score' in analysis_data:
                overall_score = analysis_data['compatibility_score']
                elements.append(Paragraph("Overall Job Compatibility", heading_style))
                elements.append(Paragraph(f"{overall_score}%", score_style))
                
                # Add visualization for overall score
                compatibility_chart = ReportGenerator._create_gauge_chart(overall_score, "Compatibility Score")
                elements.append(compatibility_chart)
                elements.append(Spacer(1, 20))
            
            # Add extracted skills section
            if 'skills' in analysis_data and analysis_data['skills']:
                elements.append(Paragraph("Extracted Skills", heading_style))
                
                # Format skills as a bullet list
                skill_text = ""
                for skill in analysis_data['skills']:
                    skill_text += f"• {skill}<br/>"
                elements.append(Paragraph(skill_text, normal_style))
                elements.append(Spacer(1, 20))
            
            # Add matched skills section if available
            if 'matched_skills' in analysis_data and analysis_data['matched_skills']:
                elements.append(Paragraph("Matched Skills", heading_style))
                
                # Format matched skills as a bullet list
                matched_text = ""
                for skill in analysis_data['matched_skills']:
                    matched_text += f"• {skill}<br/>"
                elements.append(Paragraph(matched_text, normal_style))
                elements.append(Spacer(1, 20))
            
            # Add score breakdown section if available
            score_data = []
            if 'scores' in analysis_data and len(analysis_data['scores']) > 1:
                for key, value in analysis_data['scores'].items():
                    if key != 'overall':  # Skip overall score as it's already displayed
                        score_data.append((key.capitalize(), value))
            elif all(k in analysis_data for k in ('skill_score', 'experience_score', 'education_score')):
                score_data = [
                    ('Skill', analysis_data['skill_score']),
                    ('Experience', analysis_data['experience_score']),
                    ('Education', analysis_data['education_score'])
                ]
                
            if score_data:
                elements.append(Paragraph("Score Breakdown", heading_style))
                score_chart = ReportGenerator._create_score_chart(score_data)
                elements.append(score_chart)
                elements.append(Spacer(1, 20))
            
            # Add skill gaps section if available
            if 'skill_gaps' in analysis_data and analysis_data['skill_gaps']:
                elements.append(Paragraph("Skill Gaps", heading_style))
                elements.append(Paragraph("The following skills were required but not found in your resume:", normal_style))
                
                # Format skill gaps as a bullet list
                gaps_text = ""
                for skill in analysis_data['skill_gaps']:
                    gaps_text += f"• {skill}<br/>"
                elements.append(Paragraph(gaps_text, normal_style))
                elements.append(Spacer(1, 20))
                
                # Add skill development roadmap if skill gaps exist
                elements.append(Paragraph("Skill Development Roadmap", heading_style))
                elements.append(Paragraph("Priority skills to develop:", normal_style))
                
                # Create a roadmap table
                skill_roadmap = ReportGenerator._create_skill_roadmap_table(analysis_data['skill_gaps'])
                elements.append(skill_roadmap)
                elements.append(Spacer(1, 20))
            
            # Add industry insights section if available
            if 'industry_recommendations' in analysis_data and analysis_data['industry_recommendations']:
                elements.append(Paragraph("Industry Insights", heading_style))
                
                insights_text = ""
                for insight in analysis_data['industry_recommendations']:
                    insights_text += f"• {insight}<br/>"
                elements.append(Paragraph(insights_text, normal_style))
                elements.append(Spacer(1, 20))
            elif 'market_data' in analysis_data and 'industry_trends' in analysis_data['market_data']:
                elements.append(Paragraph("Industry Insights", heading_style))
                
                insights_text = ""
                for trend in analysis_data['market_data']['industry_trends'][:3]:
                    insights_text += f"• {trend.get('name', '')}: {trend.get('description', '')}<br/>"
                elements.append(Paragraph(insights_text, normal_style))
                elements.append(Spacer(1, 20))
            
            # Add recommendations section if available
            if 'recommendations' in analysis_data and analysis_data['recommendations']:
                elements.append(Paragraph("Recommendations", heading_style))
                
                recommendations_text = ""
                for recommendation in analysis_data['recommendations']:
                    recommendations_text += f"• {recommendation}<br/>"
                elements.append(Paragraph(recommendations_text, normal_style))
            
            # Build the PDF document
            doc.build(elements)
            
            # Get the value from the buffer
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            # Save the current analysis to history
            ReportGenerator._save_to_history(analysis_data)
            
            return pdf_bytes
        except Exception as e:
            logging.error(f"Error generating PDF report: {str(e)}")
            traceback.print_exc()
            return None
    
    @staticmethod
    def _create_gauge_chart(score, title):
        """Create a gauge chart visualization for the overall score"""
        try:
            # Create a simple gauge chart using matplotlib
            plt.figure(figsize=(6, 3))
            
            # Create the gauge
            ax = plt.subplot(111, aspect='equal')
            
            # Define colors based on score
            if score >= 80:
                color = 'green'
            elif score >= 60:
                color = 'orange'
            else:
                color = 'red'
            
            # Draw the gauge
            wedge = patches.Wedge(
                center=(0.5, 0), 
                r=0.75, 
                theta1=180, 
                theta2=180 - (score * 1.8), 
                width=0.2,
                color=color
            )
            ax.add_patch(wedge)
            
            # Add the score text
            ax.text(0.5, 0.5, f"{score}%", ha='center', va='center', fontsize=24)
            
            # Add the title
            ax.text(0.5, 0.85, title, ha='center', va='center', fontsize=14)
            
            # Configure the plot
            ax.set_xlim(0, 1)
            ax.set_ylim(-0.1, 1)
            ax.axis('off')
            
            # Save the figure to a buffer
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
            img_buffer.seek(0)
            
            # Close the figure to prevent memory leaks
            plt.close()
            
            # Return an Image object to embed in the PDF
            return Image(img_buffer, width=450, height=200)
        except Exception as e:
            logging.error(f"Error creating gauge chart: {str(e)}")
            traceback.print_exc()
            # Return a placeholder text if chart creation fails
            return Paragraph(f"Score: {score}%", getSampleStyleSheet()['Normal'])
    
    @staticmethod
    def _create_score_chart(score_data):
        """Create a bar chart visualization for score breakdown"""
        try:
            # Extract categories and values
            categories = [item[0] for item in score_data]
            values = [item[1] for item in score_data]
            
            # Create the bar chart
            plt.figure(figsize=(6, 3))
            
            # Create bars with different colors based on score
            colors = ['#ff9999' if v < 60 else '#99ff99' if v >= 80 else '#ffcc99' for v in values]
            bars = plt.bar(categories, values, color=colors)
            
            # Add value labels on top of bars
            for bar in bars:
                height = bar.get_height()
                plt.text(
                    bar.get_x() + bar.get_width()/2.,
                    height + 2,
                    f"{height}%",
                    ha='center', va='bottom',
                    fontsize=9
                )
            
            # Configure the plot
            plt.title("Score Breakdown")
            plt.ylim(0, 105)  # Set y-axis limit to 0-105 to accommodate the text above bars
            plt.tight_layout()
            
            # Save the figure to a buffer
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
            img_buffer.seek(0)
            
            # Close the figure to prevent memory leaks
            plt.close()
            
            # Return an Image object to embed in the PDF
            return Image(img_buffer, width=450, height=200)
        except Exception as e:
            logging.error(f"Error creating score chart: {str(e)}")
            traceback.print_exc()
            # Create a simple text table as fallback
            data = [["Category", "Score"]] + [[cat, f"{val}%"] for cat, val in score_data]
            return Table(data)
    
    @staticmethod
    def _create_skill_roadmap_table(skill_gaps):
        """Create a table with skill development priorities"""
        try:
            # Create header
            data = [["Skill", "Priority", "Recommended Action"]]
            
            # Sort skill gaps by presumed importance (could be enhanced with actual importance data)
            for i, skill in enumerate(skill_gaps[:5]):  # Limit to top 5 skills
                priority = "High" if i < 2 else "Medium" if i < 4 else "Low"
                action = "Take online course" if i % 3 == 0 else "Build practice project" if i % 3 == 1 else "Study documentation"
                data.append([skill, priority, action])
            
            # Create and style the table
            table = Table(data, colWidths=[150, 80, 220])
            
            # Style the table
            table_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ])
            table.setStyle(table_style)
            
            return table
        except Exception as e:
            logging.error(f"Error creating skill roadmap table: {str(e)}")
            traceback.print_exc()
            # Return a simple paragraph as fallback
            return Paragraph("Focus on developing these skills through online courses, projects, and documentation.", getSampleStyleSheet()['Normal'])
    
    @staticmethod
    def generate_html_report(analysis_data: Dict) -> str:
        """
        Generate interactive HTML report from analysis data
        
        Args:
            analysis_data (Dict): Comprehensive resume analysis data
            
        Returns:
            str: HTML content as string
        """
        try:
            logging.info("Generating HTML report")
            skills = analysis_data.get('skills', [])
            matched_skills = analysis_data.get('matched_skills', [])
            skill_gaps = analysis_data.get('skill_gaps', [])
            recommendations = analysis_data.get('recommendations', [])
            market_data = analysis_data.get('market_data', {})
            scores = {
                'overall': analysis_data.get('overall_score', 0),
                'skill': analysis_data.get('skill_score', 0),
                'experience': analysis_data.get('experience_score', 0),
                'education': analysis_data.get('education_score', 0)
            }
            
            # Create HTML content with enhanced styling and interactivity
            html_content = '<!DOCTYPE html>\n'
            html_content += '<html lang="en">\n'
            html_content += '<head>\n'
            html_content += '    <meta charset="UTF-8">\n'
            html_content += '    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
            html_content += '    <title>Resume Analysis Report</title>\n'
            html_content += '    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">\n'
            html_content += '    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>\n'
            html_content += '    <style>\n'
            html_content += '        body { font-family: "Roboto", sans-serif; line-height: 1.6; color: #333; max-width: 1200px; margin: 0 auto; padding: 20px; background-color: #f9f9f9; }\n'
            html_content += '        .container { background-color: #fff; border-radius: 8px; box-shadow: 0 0 20px rgba(0, 0, 0, 0.1); padding: 30px; margin-bottom: 30px; }\n'
            html_content += '        h1 { color: #2c3e50; text-align: center; margin-bottom: 30px; }\n'
            html_content += '        h2 { color: #3498db; border-bottom: 2px solid #3498db; padding-bottom: 10px; margin-top: 40px; }\n'
            html_content += '        .score-container { text-align: center; margin: 30px 0; }\n'
            html_content += '        .overall-score { font-size: 60px; font-weight: bold; color: #2c3e50; }\n'
            html_content += '        .score-label { font-size: 18px; color: #7f8c8d; margin-bottom: 10px; }\n'
            html_content += '        .score-breakdown { display: flex; flex-wrap: wrap; justify-content: space-between; margin: 30px 0; }\n'
            html_content += '        .score-card { flex: 1; min-width: 200px; background-color: #f8f9fa; border-radius: 8px; padding: 20px; margin: 10px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1); transition: transform 0.3s ease; }\n'
            html_content += '        .score-card:hover { transform: translateY(-5px); box-shadow: 0 5px 15px rgba(0,0,0,0.1); }\n'
            html_content += '        .score-value { font-size: 32px; font-weight: bold; margin: 10px 0; }\n'
            html_content += '        .chart-container { width: 100%; height: 400px; margin: 30px 0; }\n'
            html_content += '        .skill-container { display: flex; flex-wrap: wrap; gap: 10px; margin: 20px 0; }\n'
            html_content += '        .skill-tag { background-color: #e8f4f8; padding: 8px 15px; border-radius: 20px; font-size: 14px; transition: all 0.3s ease; }\n'
            html_content += '        .skill-tag:hover { background-color: #3498db; color: white; transform: scale(1.05); }\n'
            html_content += '        .skill-gap { background-color: #ffe9e9; }\n'
            html_content += '        .skill-gap:hover { background-color: #e74c3c; }\n'
            html_content += '        .recommendations { margin: 30px 0; }\n'
            html_content += '        .recommendation-item { background-color: #f0f7fb; border-left: 5px solid #3498db; padding: 15px; margin-bottom: 15px; border-radius: 0 5px 5px 0; }\n'
            html_content += '        .roadmap { margin: 30px 0; }\n'
            html_content += '        .roadmap-step { display: flex; margin-bottom: 20px; }\n'
            html_content += '        .roadmap-number { width: 40px; height: 40px; background-color: #3498db; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; margin-right: 20px; flex-shrink: 0; }\n'
            html_content += '        .roadmap-content { flex-grow: 1; background-color: #f8f9fa; padding: 20px; border-radius: 8px; }\n'
            html_content += '        .roadmap-title { font-weight: bold; margin-bottom: 10px; color: #2c3e50; }\n'
            html_content += '        .collapsible { background-color: #f8f9fa; color: #444; cursor: pointer; padding: 18px; width: 100%; border: none; text-align: left; outline: none; font-size: 16px; transition: 0.4s; border-radius: 5px; margin-bottom: 10px; }\n'
            html_content += '        .active, .collapsible:hover { background-color: #e8f4f8; }\n'
            html_content += '        .content { padding: 0 18px; max-height: 0; overflow: hidden; transition: max-height 0.2s ease-out; background-color: white; border-radius: 0 0 5px 5px; }\n'
            html_content += '        .toggle-icon::before { content: "▶"; display: inline-block; margin-right: 10px; transition: transform 0.3s; }\n'
            html_content += '        .active .toggle-icon::before { content: "▼"; }\n'
            html_content += '        @media (max-width: 768px) { .score-breakdown { flex-direction: column; } }\n'
            html_content += '    </style>\n'
            html_content += '</head>\n'
            html_content += '<body>\n'
            html_content += '    <div class="container">\n'
            html_content += '        <h1>Resume Analysis Report</h1>\n'
            
            # Overall Score section
            if 'scores' in analysis_data and 'overall' in analysis_data['scores']:
                overall_score = analysis_data['scores']['overall']
                score_color = '#27ae60' if overall_score >= 80 else '#e67e22' if overall_score >= 60 else '#c0392b'
                
                html_content += '        <div class="score-container">\n'
                html_content += '            <div class="score-label">Overall Job Compatibility</div>\n'
                html_content += f'            <div class="overall-score" style="color: {score_color};">{overall_score}%</div>\n'
                html_content += '            <div id="gauge-chart" class="chart-container"></div>\n'
                html_content += '        </div>\n'
                
                # Add JavaScript for gauge chart
                html_content += '        <script>\n'
                html_content += '            var gaugeData = [\n'
                html_content += '                {\n'
                html_content += '                    type: "indicator",\n'
                html_content += '                    mode: "gauge+number",\n'
                html_content += '                    value: ' + str(overall_score) + ',\n'
                html_content += '                    title: { text: "Compatibility Score", font: { size: 24 } },\n'
                html_content += '                    gauge: {\n'
                html_content += '                        axis: { range: [null, 100], tickwidth: 1, tickcolor: "darkblue" },\n'
                html_content += '                        bar: { color: "' + score_color + '" },\n'
                html_content += '                        bgcolor: "white",\n'
                html_content += '                        borderwidth: 2,\n'
                html_content += '                        bordercolor: "gray",\n'
                html_content += '                        steps: [\n'
                html_content += '                            { range: [0, 60], color: "rgba(255, 99, 71, 0.3)" },\n'
                html_content += '                            { range: [60, 80], color: "rgba(255, 165, 0, 0.3)" },\n'
                html_content += '                            { range: [80, 100], color: "rgba(144, 238, 144, 0.3)" }\n'
                html_content += '                        ],\n'
                html_content += '                    }\n'
                html_content += '                }\n'
                html_content += '            ];\n'
                html_content += '            var layout = { width: 600, height: 400, margin: { t: 25, b: 25, l: 25, r: 25 } };\n'
                html_content += '            Plotly.newPlot("gauge-chart", gaugeData, layout);\n'
                html_content += '        </script>\n'
            
            # Score Breakdown section
            if 'scores' in analysis_data and len(analysis_data['scores']) > 1:
                html_content += '        <h2>Score Breakdown</h2>\n'
                html_content += '        <div class="score-breakdown">\n'
                
                for key, value in analysis_data['scores'].items():
                    if key != 'overall':  # Skip overall score as it's already displayed
                        score_color = '#27ae60' if value >= 80 else '#e67e22' if value >= 60 else '#c0392b'
                        html_content += f'            <div class="score-card">\n'
                        html_content += f'                <div>{key.capitalize()}</div>\n'
                        html_content += f'                <div class="score-value" style="color: {score_color};">{value}%</div>\n'
                        html_content += f'            </div>\n'
                
                html_content += '        </div>\n'
                
                # Add a bar chart for score breakdown
                html_content += '        <div id="score-chart" class="chart-container"></div>\n'
                
                # Add JavaScript for bar chart
                html_content += '        <script>\n'
                html_content += '            var scoreData = [{\n'
                html_content += '                x: [' + ', '.join([f'"{k.capitalize()}"' for k in analysis_data['scores'] if k != 'overall']) + '],\n'
                html_content += '                y: [' + ', '.join([str(v) for k, v in analysis_data['scores'].items() if k != 'overall']) + '],\n'
                html_content += '                type: "bar",\n'
                html_content += '                marker: {\n'
                html_content += '                    color: [' + ', '.join(['"#27ae60"' if v >= 80 else '"#e67e22"' if v >= 60 else '"#c0392b"' for k, v in analysis_data['scores'].items() if k != 'overall']) + ']\n'
                html_content += '                },\n'
                html_content += '                text: [' + ', '.join([f'"{v}%"' for k, v in analysis_data['scores'].items() if k != 'overall']) + '],\n'
                html_content += '                textposition: "auto",\n'
                html_content += '            }];\n'
                html_content += '            var layout = {\n'
                html_content += '                title: "Score Components",\n'
                html_content += '                yaxis: { range: [0, 100], title: "Score (%)" },\n'
                html_content += '                margin: { t: 50, b: 50, l: 50, r: 50 }\n'
                html_content += '            };\n'
                html_content += '            Plotly.newPlot("score-chart", scoreData, layout);\n'
                html_content += '        </script>\n'
            
            # Extracted Skills section with collapsible content
            if 'skills' in analysis_data and analysis_data['skills']:
                html_content += '        <h2>Skills Analysis</h2>\n'
                
                # Make skills section collapsible
                html_content += '        <button class="collapsible"><span class="toggle-icon"></span>Extracted Skills</button>\n'
                html_content += '        <div class="content">\n'
                html_content += '            <div class="skill-container">\n'
                
                for skill in analysis_data['skills']:
                    html_content += f'                <div class="skill-tag">{skill}</div>\n'
                
                html_content += '            </div>\n'
                html_content += '        </div>\n'
            
            # Matched Skills section
            if 'matched_skills' in analysis_data and analysis_data['matched_skills']:
                html_content += '        <button class="collapsible"><span class="toggle-icon"></span>Matched Skills</button>\n'
                html_content += '        <div class="content">\n'
                html_content += '            <div class="skill-container">\n'
                
                for skill in analysis_data['matched_skills']:
                    html_content += f'                <div class="skill-tag">{skill}</div>\n'
                
                html_content += '            </div>\n'
                html_content += '        </div>\n'
            
            # Skill Gaps section
            if 'skill_gaps' in analysis_data and analysis_data['skill_gaps']:
                html_content += '        <button class="collapsible"><span class="toggle-icon"></span>Skill Gaps</button>\n'
                html_content += '        <div class="content">\n'
                html_content += '            <p>The following skills were required but not found in your resume:</p>\n'
                html_content += '            <div class="skill-container">\n'
                
                for skill in analysis_data['skill_gaps']:
                    html_content += f'                <div class="skill-tag skill-gap">{skill}</div>\n'
                
                html_content += '            </div>\n'
                html_content += '        </div>\n'
            
            # Skill Development Roadmap section
            if 'skill_gaps' in analysis_data and analysis_data['skill_gaps']:
                html_content += '        <h2>Skill Development Roadmap</h2>\n'
                html_content += '        <div class="roadmap">\n'
                
                # Create a roadmap for the top 3 skills to develop
                for i, skill in enumerate(analysis_data['skill_gaps'][:3]):
                    html_content += f'            <div class="roadmap-step">\n'
                    html_content += f'                <div class="roadmap-number">{i+1}</div>\n'
                    html_content += f'                <div class="roadmap-content">\n'
                    html_content += f'                    <div class="roadmap-title">Learn {skill}</div>\n'
                    
                    # Add specific recommendations based on the skill
                    learning_method = "Take an online course" if i % 3 == 0 else "Build practice projects" if i % 3 == 1 else "Study documentation and tutorials"
                    time_estimate = f"{i+1}-{i+3} months"
                    
                    html_content += f'                    <p><strong>Recommended approach:</strong> {learning_method}</p>\n'
                    html_content += f'                    <p><strong>Estimated time investment:</strong> {time_estimate}</p>\n'
                    html_content += f'                </div>\n'
                    html_content += f'            </div>\n'
                
                html_content += '        </div>\n'
            
            # Recommendations section
            if 'recommendations' in analysis_data and analysis_data['recommendations']:
                html_content += '        <h2>Recommendations</h2>\n'
                html_content += '        <div class="recommendations">\n'
                
                for recommendation in analysis_data['recommendations']:
                    html_content += f'            <div class="recommendation-item">{recommendation}</div>\n'
                
                html_content += '        </div>\n'
            
            # Industry Insights section
            if 'industry_recommendations' in analysis_data and analysis_data['industry_recommendations']:
                html_content += '        <h2>Industry Insights</h2>\n'
                html_content += '        <div class="recommendations">\n'
                
                for insight in analysis_data['industry_recommendations']:
                    html_content += f'            <div class="recommendation-item">{insight}</div>\n'
                
                html_content += '        </div>\n'
            
            html_content += '    </div>\n'
            
            # Add JavaScript for collapsible sections
            html_content += '    <script>\n'
            html_content += '        var coll = document.getElementsByClassName("collapsible");\n'
            html_content += '        for (var i = 0; i < coll.length; i++) {\n'
            html_content += '            coll[i].addEventListener("click", function() {\n'
            html_content += '                this.classList.toggle("active");\n'
            html_content += '                var content = this.nextElementSibling;\n'
            html_content += '                if (content.style.maxHeight) {\n'
            html_content += '                    content.style.maxHeight = null;\n'
            html_content += '                } else {\n'
            html_content += '                    content.style.maxHeight = content.scrollHeight + "px";\n'
            html_content += '                }\n'
            html_content += '            });\n'
            html_content += '        }\n'
            html_content += '        // Open the first collapsible by default\n'
            html_content += '        if (coll.length > 0) {\n'
            html_content += '            coll[0].click();\n'
            html_content += '        }\n'
            html_content += '    </script>\n'
            
            html_content += '</body>\n'
            html_content += '</html>\n'
            
            # Save the current analysis to history
            ReportGenerator._save_to_history(analysis_data)
            
            return html_content
        except Exception as e:
            logging.error(f"Error generating HTML report: {str(e)}")
            traceback.print_exc()
            return None
    
    @staticmethod
    def generate_comparative_report(current_analysis, previous_analysis):
        """Generate a comparative report between current and previous analyses."""
        try:
            logging.info("Generating comparative report")
            
            if not previous_analysis:
                return ReportGenerator.generate_html_report(current_analysis)
            
            # Extract data from both analyses
            current_scores = {
                'overall': current_analysis.get('overall_score', 0),
                'skill': current_analysis.get('skill_score', 0),
                'experience': current_analysis.get('experience_score', 0),
                'education': current_analysis.get('education_score', 0)
            }
            
            previous_scores = {
                'overall': previous_analysis.get('overall_score', 0),
                'skill': previous_analysis.get('skill_score', 0),
                'experience': previous_analysis.get('experience_score', 0),
                'education': previous_analysis.get('education_score', 0)
            }
            
            # Calculate differences
            score_differences = {key: current_scores[key] - previous_scores[key] for key in current_scores}
            
            # Current and previous skills
            current_skills = current_analysis.get('matched_skills', [])
            previous_skills = previous_analysis.get('matched_skills', [])
            
            # New skills gained
            new_skills = [skill for skill in current_skills if skill not in previous_skills]
            
            # Skills that are no longer matches
            lost_skills = [skill for skill in previous_skills if skill not in current_skills]
            
            # Create HTML content
            html_content = '<!DOCTYPE html>\n'
            html_content += '<html lang="en">\n'
            html_content += '<head>\n'
            html_content += '    <meta charset="UTF-8">\n'
            html_content += '    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
            html_content += '    <title>Comparative Resume Analysis</title>\n'
            html_content += '    <style>\n'
            html_content += '        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 1200px; margin: 0 auto; padding: 20px; }\n'
            html_content += '        h1, h2, h3 { color: #2c3e50; }\n'
            html_content += '        .container { display: flex; flex-wrap: wrap; }\n'
            html_content += '        .section { margin-bottom: 30px; width: 100%; }\n'
            html_content += '        .comparison-container { display: flex; justify-content: space-between; flex-wrap: wrap; }\n'
            html_content += '        .comparison-box { background-color: #f8f9fa; border-radius: 8px; padding: 15px; margin: 10px; flex: 1; min-width: 200px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }\n'
            html_content += '        .comparison-value { font-size: 18px; font-weight: bold; }\n'
            html_content += '        .positive { color: #28a745; }\n'
            html_content += '        .negative { color: #dc3545; }\n'
            html_content += '        .neutral { color: #6c757d; }\n'
            html_content += '        .skill-container { display: flex; flex-wrap: wrap; gap: 10px; }\n'
            html_content += '        .skill-tag { background-color: #e8f4f8; padding: 5px 10px; border-radius: 20px; font-size: 14px; }\n'
            html_content += '        .new-skill { background-color: #d4edda; }\n'
            html_content += '        .lost-skill { background-color: #f8d7da; }\n'
            html_content += '    </style>\n'
            html_content += '</head>\n'
            html_content += '<body>\n'
            html_content += '    <div class="container">\n'
            html_content += '        <div class="section">\n'
            html_content += '            <h1>Comparative Resume Analysis</h1>\n'
            html_content += '            <p>Comparing your current resume with previous analysis</p>\n'
            html_content += '        </div>\n'
            
            # Add score comparisons
            html_content += '        <div class="section">\n'
            html_content += '            <h2>Score Comparison</h2>\n'
            html_content += '            <div class="comparison-container">\n'
            
            for score_name, difference in score_differences.items():
                css_class = "positive" if difference > 0 else "negative" if difference < 0 else "neutral"
                sign = "+" if difference > 0 else ""
                
                html_content += '                <div class="comparison-box">\n'
                html_content += f'                    <h3>{score_name.capitalize()} Score</h3>\n'
                html_content += f'                    <div>Previous: {previous_scores[score_name]}%</div>\n'
                html_content += f'                    <div>Current: {current_scores[score_name]}%</div>\n'
                html_content += f'                    <div class="comparison-value {css_class}">{sign}{difference}%</div>\n'
                html_content += '                </div>\n'
            
            html_content += '            </div>\n'
            html_content += '        </div>\n'
            
            # Add skill comparisons
            html_content += '        <div class="section">\n'
            html_content += '            <h2>Skill Changes</h2>\n'
            
            # New skills
            if new_skills:
                html_content += '            <h3>New Skills Gained</h3>\n'
                html_content += '            <div class="skill-container">\n'
                for skill in new_skills:
                    html_content += f'                <div class="skill-tag new-skill">{skill}</div>\n'
                html_content += '            </div>\n'
            
            # Lost skills
            if lost_skills:
                html_content += '            <h3>Skills No Longer Matched</h3>\n'
                html_content += '            <div class="skill-container">\n'
                for skill in lost_skills:
                    html_content += f'                <div class="skill-tag lost-skill">{skill}</div>\n'
                html_content += '            </div>\n'
            
            # No changes
            if not new_skills and not lost_skills:
                html_content += '            <p>No changes in matched skills detected.</p>\n'
            
            html_content += '        </div>\n'
            
            # Current recommendations
            html_content += '        <div class="section">\n'
            html_content += '            <h2>Current Recommendations</h2>\n'
            
            recommendations = current_analysis.get('recommendations', [])
            if recommendations:
                for recommendation in recommendations:
                    html_content += f'            <div class="comparison-box">{recommendation}</div>\n'
            else:
                html_content += '            <p>No current recommendations available.</p>\n'
            
            html_content += '        </div>\n'
            
            # Close HTML tags
            html_content += '    </div>\n'
            html_content += '</body>\n'
            html_content += '</html>\n'
            
            # Save the current analysis to history
            ReportGenerator._save_to_history(current_analysis)
            
            return html_content
        except Exception as e:
            logging.error(f"Error generating comparative report: {str(e)}")
            traceback.print_exc()
            return None
    
    @staticmethod
    def _save_to_history(analysis_data):
        """Save analysis data to history for future comparison."""
        try:
            history_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'report_history.json')
            os.makedirs(os.path.dirname(history_path), exist_ok=True)
            
            # Add timestamp to the analysis data
            report_entry = analysis_data.copy()
            report_entry['timestamp'] = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Load existing history
            history = []
            if os.path.exists(history_path):
                with open(history_path, 'r') as file:
                    try:
                        history = json.load(file)
                    except json.JSONDecodeError:
                        history = []
            
            # Add current report to history
            history.append(report_entry)
            
            # Save updated history
            with open(history_path, 'w') as file:
                json.dump(history, file, indent=4)
            
            logging.info(f"Saved report to history. Total reports: {len(history)}")
            return True
        except Exception as e:
            logging.error(f"Error saving to history: {str(e)}")
            traceback.print_exc()
            return False
    
    @staticmethod
    def get_report_history(limit=10):
        """Get report history for comparison and tracking."""
        try:
            history_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'report_history.json')
            
            if not os.path.exists(history_path):
                return []
            
            with open(history_path, 'r') as file:
                try:
                    history = json.load(file)
                    # Sort by timestamp in descending order (most recent first)
                    history.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
                    return history[:limit]  # Return limited number of most recent reports
                except json.JSONDecodeError:
                    return []
        except Exception as e:
            logging.error(f"Error retrieving report history: {str(e)}")
            traceback.print_exc()
            return []

    @staticmethod
    def save_report_history(user_id, analysis_data):
        """Save report to history for a specific user"""
        try:
            # Create a directory structure for user data
            user_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'users', user_id)
            history_path = os.path.join(user_dir, 'report_history.json')
            os.makedirs(os.path.dirname(history_path), exist_ok=True)
            
            # Add timestamp to the analysis data
            report_entry = analysis_data.copy()
            report_entry['timestamp'] = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Load existing history
            history = []
            if os.path.exists(history_path):
                with open(history_path, 'r') as file:
                    try:
                        history = json.load(file)
                    except json.JSONDecodeError:
                        history = []
            
            # Add current report to history
            history.append(report_entry)
            
            # Save updated history
            with open(history_path, 'w') as file:
                json.dump(history, file, indent=4)
            
            logging.info(f"Saved report to history for user {user_id}. Total reports: {len(history)}")
            return True
        except Exception as e:
            logging.error(f"Error saving to history for user {user_id}: {str(e)}")
            traceback.print_exc()
            return False