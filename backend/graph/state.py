from typing import Annotated, Optional
import operator
from typing_extensions import TypedDict


class UserProfile(TypedDict):
    age: int
    sex: str
    location: str
    health_issues: list[str]
    lifestyle: str
    goals: list[str]
    other_info: str
    # Richer numeric/categorical inputs for better personalization
    sleep_hours: float          # average hours per night
    exercise_frequency: str     # "none" | "1-2x/semana" | "3-4x/semana" | "5+/semana"
    diet_type: str              # "omnívoro" | "vegetariano" | "vegano" | "keto" | "mediterráneo" | "otro"
    stress_level: str           # "bajo" | "moderado" | "alto" | "muy alto"
    energy_level: str           # "bajo" | "moderado" | "alto"


class SubSection(TypedDict):
    id: str           # e.g. "ch01_s02_sub03"
    chapter: str
    chapter_index: int
    section: str
    section_index: int
    title: str
    focus: str        # "Acciones concretas" | "Ciencia detrás del hábito" | "Protocolo de implementación"
    level: int        # biohacking level 1-5
    content: Optional[str]


class BookOutline(TypedDict):
    title: str
    chapters: list[dict]  # [{title, level, sections: [{title, subsections: [{title, focus}]}]}]


class GraphState(TypedDict):
    session_token: str
    user_email: str
    user_profile: UserProfile
    book_outline: Optional[BookOutline]
    sections_to_write: list[SubSection]
    written_sections: Annotated[list[SubSection], operator.add]
    final_book: Optional[str]
    pdf_path: Optional[str]     # path to cached PDF on disk
    user_feedback: Optional[str]
    status: str  # "outlining" | "awaiting_approval" | "writing" | "done"
    email_sent: bool


class WriterInput(TypedDict):
    """State passed to each parallel writer node via Send()."""
    user_profile: UserProfile
    section: SubSection
    book_outline: BookOutline   # full outline for context
