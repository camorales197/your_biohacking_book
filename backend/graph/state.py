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


class SubSection(TypedDict):
    id: str           # e.g. "ch1_s2_sub3"
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
    user_profile: UserProfile
    book_outline: Optional[BookOutline]
    sections_to_write: list[SubSection]
    # Annotated reducer: parallel writer results get appended into this list
    written_sections: Annotated[list[SubSection], operator.add]
    final_book: Optional[str]
    user_feedback: Optional[str]
    status: str  # "outlining" | "awaiting_approval" | "writing" | "done"


class WriterInput(TypedDict):
    """State passed to each parallel writer node via Send()."""
    user_profile: UserProfile
    section: SubSection
