from app.services.analysis_service import AnalysisService

_service = AnalysisService()


def get_analysis_service() -> AnalysisService:
    return _service
