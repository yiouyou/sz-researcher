from enum import Enum


class ReportType(Enum):
    # ResearchReport = 'research_report'
    # ResourceReport = 'resource_report'
    # OutlineReport = 'outline_report'
    # CustomReport = 'custom_report'
    # DetailedReport = 'detailed_report'
    # SubtopicReport = 'subtopic_report'
    ResearchReport = '研究'
    ResourceReport = '信源'
    OutlineReport = '大纲'
    DetailedReport = '详细'
    CustomReport = '自定义'
    SubtopicReport = '子课题'
    
class ReportSource(Enum):
    Web = 'web'
    Local = 'local'

