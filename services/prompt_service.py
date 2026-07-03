DEFAULT_FILE_ANALYSIS_PROMPT = (
    "Analyze these files. Explain what they do, point out problems, "
    "and suggest improvements."
)


def has_file(data) -> bool:
    has_file_name = bool((data.file_name or "").strip())
    has_file_content = data.file_content is not None
    has_multiple_files = bool(getattr(data, "files", None))
    return has_file_name or has_file_content or has_multiple_files


def build_file_analysis_prompt(prompt: str, file_name: str, file_content: str) -> str:
    task = prompt.strip() or DEFAULT_FILE_ANALYSIS_PROMPT

    return "\n".join(
        [
            task,
            "",
            "Attached file for analysis:",
            f"File name: {file_name.strip()}",
            "",
            "<file_contents>",
            file_content,
            "</file_contents>",
        ]
    )


def build_multiple_file_analysis_prompt(prompt: str, files: list[dict]) -> str:
    task = prompt.strip() or DEFAULT_FILE_ANALYSIS_PROMPT
    sections = []

    for item in files:
        file_name = (item.get("name") or "").strip()
        file_content = item.get("content") or ""
        sections.extend(
            [
                f"File name: {file_name}",
                "",
                "<file_contents>",
                file_content,
                "</file_contents>",
                "",
            ]
        )

    return "\n".join([task, "", "Attached files for analysis:", *sections]).strip()


def build_generation_prompt(data) -> str:
    prompt = data.prompt.strip()

    if getattr(data, "files", None):
        return build_multiple_file_analysis_prompt(prompt=prompt, files=data.files)

    if has_file(data):
        return build_file_analysis_prompt(
            prompt=prompt,
            file_name=data.file_name,
            file_content=data.file_content,
        )

    return prompt


__all__ = ["build_generation_prompt", "has_file"]
