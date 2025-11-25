class Section {
  title string
  level int
  page_number int?
  subsections Section[]
}

class Outline {
  sections Section[]
}

class Concept {
  name string
  description string
  related_terms string[]
}

class LearningObjective {
  description string
}

class SlideContent {
  concepts Concept[]
  objectives LearningObjective[]
  summary string
}

function ExtractOutline(document_text: string) -> Outline {
  client Ollama
  prompt #"
    Analyze the following document text and extract the hierarchical outline (Table of Contents).
    Identify sections, their levels, and titles.

    Document Text:
    {{ document_text }}
  "#
}

function ExtractConcepts(slide_text: string) -> SlideContent {
  client Ollama
  prompt #"
    Analyze the following text from a training slide.
    Extract key technical concepts taught, define them briefly, and identify learning objectives.
    Also provide a brief summary of the slide.

    Slide Text:
    {{ slide_text }}
  "#
}
