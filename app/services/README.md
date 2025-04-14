# SkillSift Services

This directory contains the core service layer components of the SkillSift application. Each service handles specific business logic and functionality.

## Services Overview

### RecommendationEngine
Generates personalized recommendations based on resume analysis and job requirements.

```python
from app.services.recommendation_engine import RecommendationEngine

engine = RecommendationEngine()
recommendations = engine.generate_recommendations(
    skills=["python", "javascript"],
    skill_gaps=["react", "node.js"],
    resume_text="Resume content...",
    job_description="Job description..."
)
```

Key features:
- Skill development recommendations
- Content optimization suggestions
- Keyword enhancement
- Formatting suggestions

### MarketDataService
Handles market intelligence and industry data analysis.

```python
from app.services.market_data_service import MarketDataService

market_service = MarketDataService()
salary_data = market_service.get_salary_range(db, "Software Engineer", "Technology")
demand_data = market_service.get_job_market_demand(db, "Software Engineer", "Technology")
```

Provides:
- Salary ranges
- Job market demand analysis
- Career path recommendations
- Industry trends

### ScorerService
Evaluates candidate-job compatibility and generates scores.

```python
from app.services.scorer import CompatibilityScorer

scorer = CompatibilityScorer()
score = scorer.calculate_score(
    candidate_skills=["python", "sql"],
    job_requirements=["python", "django", "sql"]
)
```

Features:
- Skill matching
- Experience evaluation
- Education assessment
- Overall compatibility scoring

### ResumeParser
Handles resume document processing and information extraction.

```python
from app.services.parser import ResumeParser

parser = ResumeParser()
text = parser.parse_pdf(pdf_content)
```

Capabilities:
- PDF parsing
- Text extraction
- Section identification
- Skills extraction

## Architecture

The services follow these key principles:

1. **Separation of Concerns**: Each service handles a specific domain
2. **Dependency Injection**: Services are designed to be easily testable
3. **Error Handling**: Comprehensive error handling with custom exceptions
4. **Logging**: Built-in logging for debugging and monitoring

## Best Practices

When working with services:

1. Always use type hints for function arguments and return values
2. Include docstrings with examples
3. Handle exceptions appropriately
4. Use the logging framework
5. Write unit tests for new functionality

## Error Handling

Services use custom exceptions from `app.core.exceptions`:

```python
from app.core.exceptions import (
    ParsingError,
    ScoringError,
    MarketDataError
)
```

## Testing

Each service has corresponding test files in `/tests`. Run tests with:

```bash
pytest tests/test_recommendation_engine.py
pytest tests/test_market_data_service.py
pytest tests/test_scorer.py
pytest tests/test_parser.py
```

## Adding New Services

When adding a new service:

1. Create a new file in the services directory
2. Follow the established patterns for error handling and logging
3. Add corresponding test file
4. Update this README with service documentation

## Configuration

Services can be configured through environment variables or the config file at `app/core/config.py`.

## Dependencies

Services may require external dependencies listed in `requirements.txt`. Ensure all dependencies are installed:

```bash
pip install -r requirements.txt
```

## Contributing

When contributing to services:

1. Follow the existing code style
2. Add comprehensive tests
3. Update documentation
4. Use type hints
5. Handle errors appropriately

## License

This service layer is part of the SkillSift project and is licensed under the MIT License.
