#!/usr/bin/env python3
"""Add Back/Continue navigation across Delete Account steps (JA / EN / zh-tw).

Sci-Fi and Office share the same HTML (mode toggle), so one patch covers both.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

LABELS = {
    "ja": {"back": "← 戻る", "next": "次へ →"},
    "en": {"back": "← Back", "next": "CONTINUE →"},
    "zh-tw": {"back": "← 返回", "next": "繼續 →"},
}

TARGETS = {
    "ja": ROOT / "setting",
    "en": ROOT / "en" / "setting",
    "zh-tw": ROOT / "zh-tw" / "setting",
}


def nav(back_href: str | None, next_href: str | None, *, back: str, next_: str) -> str:
    left = f'<a href="{back_href}">{back}</a>' if back_href else "<span></span>"
    right = f'<a href="{next_href}">{next_}</a>' if next_href else "<span></span>"
    return (
        '      <div class="delete-retention-nav">\n'
        f"        {left}\n"
        f"        {right}\n"
        "      </div>\n"
    )


def ensure_nav_before_main_end(text: str, block: str) -> str:
    """Insert nav once before </main> if this file does not already have one after content."""
    marker = 'class="delete-retention-nav"'
    # Step 3 already has nav; only skip when inserting another identical purpose —
    # callers pass unique blocks. For pages that already contain our marker from a prior run,
    # replace existing trailing nav before </main>.
    if marker in text:
        # Remove any delete-retention-nav blocks that sit immediately before </main>
        import re

        text2, n = re.subn(
            r'\n?\s*<div class="delete-retention-nav">[\s\S]*?</div>\s*(</main>)',
            r"\n" + block + r"\1",
            text,
            count=1,
        )
        if n:
            return text2
        # Nav exists elsewhere (step 3 mid-content): append before </main>
        return text.replace("</main>", block + "    </main>", 1)
    return text.replace("</main>", block + "    </main>", 1)


def patch_step1(text: str, *, next_: str) -> str:
    block = nav(None, "delete_account2.html", back="", next_=next_)
    return ensure_nav_before_main_end(text, block)


def patch_step2(text: str, *, back: str, next_: str) -> str:
    # Mock: Option C continues deletion flow until real Stripe URL exists.
    text = text.replace(
        '<a href="#" class="btn-delete-stripe">Go to Stripe →</a>',
        '<a href="delete_account3.html" class="btn-delete-stripe">Go to Stripe →</a>',
    )
    text = text.replace(
        '<a href="#" class="btn-delete-stripe">Stripeへ移動 →</a>',
        '<a href="delete_account3.html" class="btn-delete-stripe">Stripeへ移動 →</a>',
    )
    text = text.replace(
        '<a href="#" class="btn-delete-stripe">前往 Stripe →</a>',
        '<a href="delete_account3.html" class="btn-delete-stripe">前往 Stripe →</a>',
    )
    block = nav("delete_account1.html", "delete_account3.html", back=back, next_=next_)
    return ensure_nav_before_main_end(text, block)


def patch_step4_1(text: str, *, back: str) -> str:
    block = nav("delete_account3.html", None, back=back, next_="")
    return ensure_nav_before_main_end(text, block)


def patch_step4_2(text: str, *, back: str) -> str:
    block = nav("delete_account4-1.html", None, back=back, next_="")
    return ensure_nav_before_main_end(text, block)


def patch_step5(text: str, *, back: str) -> str:
    block = nav("delete_account4-2.html", None, back=back, next_="")
    return ensure_nav_before_main_end(text, block)


def main() -> None:
    for lang, folder in TARGETS.items():
        L = LABELS[lang]
        patches = {
            "delete_account1.html": lambda t: patch_step1(t, next_=L["next"]),
            "delete_account2.html": lambda t: patch_step2(t, back=L["back"], next_=L["next"]),
            "delete_account4-1.html": lambda t: patch_step4_1(t, back=L["back"]),
            "delete_account4-2.html": lambda t: patch_step4_2(t, back=L["back"]),
            "delete_account5.html": lambda t: patch_step5(t, back=L["back"]),
        }
        for name, fn in patches.items():
            path = folder / name
            if not path.is_file():
                raise SystemExit(f"missing {path}")
            before = path.read_text(encoding="utf-8")
            after = fn(before)
            path.write_text(after, encoding="utf-8")
            print(f"patched {path.relative_to(ROOT)}")
    print("apply_delete_account_nav: OK")


if __name__ == "__main__":
    main()
