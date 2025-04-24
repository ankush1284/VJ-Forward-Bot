# plugins/caption_manager.py

"""
Caption Manager for VJ-Forward-Bot
Supports: add, replace, off/on, delete customizations.
"""

def apply_caption_rules(
    original_caption: str,
    mode: str = "on",
    add_text: str = "",
    replace_dict: dict = None,
    delete: bool = False
) -> str:
    """
    Apply caption rules.
    :param original_caption: The original caption (can be None)
    :param mode: "on" (caption enabled), "off" (caption disabled)
    :param add_text: Text to add (prepend/append)
    :param replace_dict: dict of {old: new} to replace in caption
    :param delete: If True, delete the caption
    :return: Modified caption string or empty string if deleted/off
    """
    if mode == "off" or delete:
        return ""

    caption = original_caption or ""

    # Replace words/phrases if replace_dict is provided
    if replace_dict and isinstance(replace_dict, dict):
        for old, new in replace_dict.items():
            caption = caption.replace(old, new)

    # Add text (example: append, you can change to prepend if you want)
    if add_text:
        caption = f"{caption}\n{add_text}" if caption else add_text

    return caption
