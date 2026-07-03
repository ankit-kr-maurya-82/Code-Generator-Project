DEFAULT_FILE_ANALYSIS_PROMPT = (
    "Analyze this file. Explain what it does, point out problems, "
    "and suggest improvements."
)


def has_file(data) -> bool:
    return bool((data.file_name or "").strip() and (data.file_content or "").strip())


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


def build_generation_prompt(data) -> str:
    prompt = data.prompt.strip()

    if has_file(data):
        return build_file_analysis_prompt(
            prompt=prompt,
            file_name=data.file_name,
            file_content=data.file_content,
        )

    return prompt


__all__ = ["build_generation_prompt", "has_file"]
