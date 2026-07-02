from pathlib import Path

from app.domain.generation.certifications import (
    detect_role_categories,
    select_reference_certifications,
)
from app.domain.generation.resume_sections import (
    extract_master_subsections,
    omit_template_section,
)

MASTER = Path(__file__).resolve().parents[3].joinpath("data/inputs/master_resume.md").read_text(
    encoding="utf-8"
)

TEMPLATE = """## Professional Summary

{{ summary }}

## Professional Experience

{{ experience }}

## Skills & Abilities

{{ skills }}

## Certifications

{{ certifications }}

## Professional Background

{{ background }}

## Education

{{ education }}
"""


def test_detect_role_categories_for_frontend() -> None:
    categories = detect_role_categories(
        "We are hiring a Frontend Developer with React, Bootstrap, and CSS experience."
    )
    assert "frontend" in categories
    assert "ai" not in categories


def test_detect_role_categories_for_ai() -> None:
    categories = detect_role_categories(
        "AI Engineer role focused on LLM integrations, OpenAI, and prompt engineering."
    )
    assert "ai" in categories
    assert "frontend" not in categories


def test_detect_role_categories_for_fullstack_ai() -> None:
    categories = detect_role_categories(
        "Fullstack AI developer building React frontends and OpenAI-powered backend services."
    )
    assert categories == {"frontend", "ai"}


def test_select_bootstrap_certification_for_frontend_role() -> None:
    selected = select_reference_certifications(
        MASTER,
        "Frontend Developer with Bootstrap and responsive UI experience.",
    )
    assert "Bootstrap 5 from Scratch" in selected
    assert "UkisAI" not in selected


def test_select_ukisai_certification_for_ai_role() -> None:
    selected = select_reference_certifications(
        MASTER,
        "AI developer building LLM-powered applications with OpenAI.",
    )
    assert "UkisAI" in selected
    assert "Bootstrap 5 from Scratch" not in selected


def test_select_both_certifications_for_relevant_fullstack_role() -> None:
    selected = select_reference_certifications(
        MASTER,
        "Fullstack AI engineer with React frontend and generative AI backend experience.",
    )
    assert "Bootstrap 5 from Scratch" in selected
    assert "UkisAI" in selected


def test_select_no_certifications_for_unrelated_role() -> None:
    selected = select_reference_certifications(
        MASTER,
        "Senior Java backend engineer for Spring Boot microservices and Oracle databases.",
    )
    assert selected == ""


def test_extract_master_subsections_reads_certifications() -> None:
    subsections = extract_master_subsections(MASTER, "Certifications")
    assert "The Ultimate Bootstrap Guide - Bootstrap 5 from Scratch" in subsections
    assert "Skills for UkisAI - 5 Week AI Bootcamp (Vibe Coding)" in subsections
    assert "Employee Management Dashboard" in subsections[
        "The Ultimate Bootstrap Guide - Bootstrap 5 from Scratch"
    ]
    assert "Cursor AI" in subsections["Skills for UkisAI - 5 Week AI Bootcamp (Vibe Coding)"]


def test_omit_template_section_removes_certifications_block() -> None:
    trimmed = omit_template_section(TEMPLATE, "Certifications")
    assert "## Certifications" not in trimmed
    assert "{{ certifications }}" not in trimmed
    assert "## Skills & Abilities" in trimmed
    assert "## Professional Background" in trimmed
