from typing import Optional
from pydantic import BaseModel

class CourseMetadata(BaseModel):
    business_unit: str
    course_title: str
    version: str
    scope_of_material: str
    current_delivery_method: str
    duration_hours: float
    costs: str
    tech_data_assessment: str
    source_of_content: str
    current_instructors: str
    audience: str
    location: str
    level_of_material: str
    engineering_discipline: str
    comments: Optional[str] = None
